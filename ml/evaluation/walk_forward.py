"""Walk-forward cross validation engine with parallel baseline evaluation."""

import logging
from collections.abc import Callable

import numpy as np
import pandas as pd

from ml.evaluation.metrics import (
    compute_accuracy,
    compute_brier_score,
    compute_log_loss,
    compute_rps,
)
from ml.models.base import BasePredictor

logger = logging.getLogger(__name__)


def _odds_to_implied(h: float, d: float, a: float) -> tuple[float, float, float]:
    """Convert decimal odds to overround-removed implied probabilities."""
    if h <= 0 or d <= 0 or a <= 0 or np.isnan(h) or np.isnan(d) or np.isnan(a):
        return (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)
    raw_h = 1.0 / h
    raw_d = 1.0 / d
    raw_a = 1.0 / a
    tot = raw_h + raw_d + raw_a
    if tot <= 0:
        return (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)
    return (raw_h / tot, raw_d / tot, raw_a / tot)


def run_walk_forward_cv(
    model_factory: Callable[[], BasePredictor],
    matches_df: pd.DataFrame,
    test_seasons: list[str],
    window_size_seasons: int = 4,
) -> tuple[pd.DataFrame, list[dict]]:
    """Execute rolling fixed-window walk-forward cross validation gameweek-by-gameweek.

    Args:
        model_factory: Callable returning an unfitted BasePredictor instance.
        matches_df: DataFrame containing Date, Season, Gameweek, HomeTeam, AwayTeam,
            FTHG, FTAG, FTR, and odds columns.
        test_seasons: List of season strings to evaluate out-of-sample.
        window_size_seasons: Number of preceding seasons in the fixed rolling training window.

    Returns:
        Tuple of (df_all_eval, fold_metrics_list).
    """
    matches_df = matches_df.sort_values("Date").reset_index(drop=True)
    if "Gameweek" not in matches_df.columns:
        gw_list: list[int] = []
        for _, s_df in matches_df.groupby("Season", sort=False):
            gw_list.extend(np.clip(np.arange(len(s_df)) // 10 + 1, 1, 38).tolist())
        matches_df["Gameweek"] = gw_list

    all_seasons = sorted(matches_df["Season"].unique())
    eval_records: list[pd.DataFrame] = []
    fold_metrics: list[dict] = []

    for test_s in test_seasons:
        if test_s not in all_seasons:
            raise ValueError(f"Test season '{test_s}' not present in matches dataset.")

        test_idx = all_seasons.index(test_s)
        if test_idx < window_size_seasons:
            raise ValueError(
                f"Insufficient history for test season '{test_s}': need {window_size_seasons} seasons, "
                f"only {test_idx} available prior."
            )

        train_seasons = all_seasons[test_idx - window_size_seasons : test_idx]
        test_data = matches_df[matches_df["Season"] == test_s].copy()
        matches_per_season = int(len(test_data))
        window_size_matches = window_size_seasons * matches_per_season

        logger.info(
            "Evaluating fold: train on %s -> test on %s (%d matches, rolling window=%d matches)",
            train_seasons,
            test_s,
            len(test_data),
            window_size_matches,
        )

        test_gameweeks = sorted(test_data["Gameweek"].unique())
        fold_predictions: list[dict] = []
        warm_start_params = None  # Carries params between consecutive GW fits
        convergence_failures = 0

        for gw in test_gameweeks:
            gw_fixtures = test_data[test_data["Gameweek"] == gw]
            min_date = gw_fixtures["Date"].min()

            # Strict chronological filtering: all matches prior to current gameweek kickoff,
            # retaining the most recent window_size_matches to maintain fixed rolling window
            prior_matches = matches_df[matches_df["Date"] < min_date]
            train_pool = prior_matches.tail(window_size_matches)

            # Fit model on current training pool with warm-start from previous GW
            model = model_factory()
            if hasattr(model, "fit") and "warm_start_params" in model.fit.__code__.co_varnames:
                model.fit(train_pool, warm_start_params=warm_start_params)
            else:
                model.fit(train_pool)

            # Capture warm-start params for the next gameweek
            if hasattr(model, "get_warm_start_params"):
                warm_start_params = model.get_warm_start_params()

            # Track convergence status
            if hasattr(model, "_converged") and model._converged is False:
                convergence_failures += 1
                logger.warning(
                    "Fold %s GW %d: Dixon-Coles did not converge (%s)",
                    test_s, gw, getattr(model, "_convergence_message", "unknown"),
                )

            # Empirical prior baseline from current training slice
            h_freq = float((train_pool["FTR"] == "H").mean())
            d_freq = float((train_pool["FTR"] == "D").mean())
            a_freq = float((train_pool["FTR"] == "A").mean())

            for _, match in gw_fixtures.iterrows():
                ht = str(match["HomeTeam"])
                at = str(match["AwayTeam"])

                probs = model.predict_proba(ht, at)
                p_h, p_d, p_a = probs["prob_home"], probs["prob_draw"], probs["prob_away"]

                # Baselines
                imp_mkt = _odds_to_implied(
                    float(match.get("AvgH", 2.5)),
                    float(match.get("AvgD", 3.2)),
                    float(match.get("AvgA", 3.0)),
                )
                imp_b365 = _odds_to_implied(
                    float(match.get("B365H", 2.5)),
                    float(match.get("B365D", 3.2)),
                    float(match.get("B365A", 3.0)),
                )

                rec = match.to_dict()
                rec.update({
                    "prob_home": p_h,
                    "prob_draw": p_d,
                    "prob_away": p_a,
                    "prob_home_uniform": 1.0 / 3.0,
                    "prob_draw_uniform": 1.0 / 3.0,
                    "prob_away_uniform": 1.0 / 3.0,
                    "prob_home_empirical": h_freq,
                    "prob_draw_empirical": d_freq,
                    "prob_away_empirical": a_freq,
                    "prob_home_market": imp_mkt[0],
                    "prob_draw_market": imp_mkt[1],
                    "prob_away_market": imp_mkt[2],
                    "prob_home_b365": imp_b365[0],
                    "prob_draw_b365": imp_b365[1],
                    "prob_away_b365": imp_b365[2],
                })
                fold_predictions.append(rec)

        df_fold = pd.DataFrame(fold_predictions)

        # One-hot outcome array
        outcomes_1hot = np.zeros((len(df_fold), 3))
        for i, ftr in enumerate(df_fold["FTR"]):
            idx = 0 if ftr == "H" else (1 if ftr == "D" else 2)
            outcomes_1hot[i, idx] = 1.0

        # Model scores
        model_probs = df_fold[["prob_home", "prob_draw", "prob_away"]].to_numpy()
        df_fold["rps"] = compute_rps(model_probs, outcomes_1hot)
        df_fold["brier"] = compute_brier_score(model_probs, outcomes_1hot)
        df_fold["log_loss"] = compute_log_loss(model_probs, outcomes_1hot)
        df_fold["correct"] = compute_accuracy(model_probs, outcomes_1hot)

        # Baseline scores for comparisons
        for pfx in ["uniform", "empirical", "market", "b365"]:
            b_probs = df_fold[
                [f"prob_home_{pfx}", f"prob_draw_{pfx}", f"prob_away_{pfx}"]
            ].to_numpy()
            df_fold[f"rps_{pfx}"] = compute_rps(b_probs, outcomes_1hot)
            df_fold[f"correct_{pfx}"] = compute_accuracy(b_probs, outcomes_1hot)

        fold_metrics.append({
            "season": test_s,
            "n_matches": len(df_fold),
            "rps": float(df_fold["rps"].mean()),
            "brier": float(df_fold["brier"].mean()),
            "log_loss": float(df_fold["log_loss"].mean()),
            "accuracy": float(df_fold["correct"].mean()),
            "convergence_failures": convergence_failures,
        })
        if convergence_failures > 0:
            logger.warning(
                "Fold %s completed with %d/%d non-converged fits",
                test_s, convergence_failures, len(test_gameweeks),
            )
        eval_records.append(df_fold)

    df_all_eval = pd.concat(eval_records, ignore_index=True)
    return df_all_eval, fold_metrics
