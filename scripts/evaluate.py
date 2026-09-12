"""CLI tool to execute full walk-forward CV and benchmark models."""

import argparse
import logging
from pathlib import Path

import numpy as np

from ml.data.ingestion import load_all_seasons
from ml.evaluation.backtest import simulate_betting
from ml.evaluation.calibration import compute_calibration
from ml.evaluation.report import EvaluationReport
from ml.evaluation.significance import evaluate_significance_suite
from ml.evaluation.walk_forward import run_walk_forward_cv
from ml.models.dixon_coles import DixonColesModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("evaluate")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Evaluate MatchSense models")
    parser.add_argument(
        "--model",
        type=str,
        default="dixon_coles",
        choices=["dixon_coles"],
        help="Model architecture to evaluate",
    )
    parser.add_argument(
        "--edge",
        type=float,
        default=0.05,
        help="EV edge threshold for betting backtesting (default: 0.05)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="reports/baseline_evaluation.md",
        help="Output Markdown report path",
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=4,
        help="Number of seasons in fixed rolling training window (default: 4 = 1,520 matches)",
    )
    return parser.parse_args()


def main() -> None:
    """Run full out-of-sample walk-forward benchmark."""
    args = parse_args()

    # 1. Load 7 historical seasons (2019-20 through 2025-26)
    season_configs = [
        {"code": "1920", "label": "2019-20"},
        {"code": "2021", "label": "2020-21"},
        {"code": "2122", "label": "2021-22"},
        {"code": "2223", "label": "2022-23"},
        {"code": "2324", "label": "2023-24"},
        {"code": "2425", "label": "2024-25"},
        {"code": "2526", "label": "2025-26"},
    ]
    cache_dir = Path("data/raw")
    logger.info("Loading %d seasons from cache: %s", len(season_configs), cache_dir)
    matches = load_all_seasons(season_configs, cache_dir=cache_dir)
    logger.info("Loaded %d total matches across %d seasons", len(matches), len(season_configs))

    # 2. Run walk-forward CV across 3 test seasons (1,140 matches)
    test_seasons = ["2023-24", "2024-25", "2025-26"]
    logger.info("Starting rolling walk-forward CV on test seasons: %s", test_seasons)
    df_eval, fold_metrics = run_walk_forward_cv(
        model_factory=lambda: DixonColesModel(xi=0.005, allow_unknown=True),
        matches_df=matches,
        test_seasons=test_seasons,
        window_size_seasons=args.window_size,
    )
    logger.info("Walk-forward CV complete: %d matches evaluated", len(df_eval))

    # 3. Aggregate metrics
    agg_metrics = {
        "rps": float(df_eval["rps"].mean()),
        "brier": float(df_eval["brier"].mean()),
        "log_loss": float(df_eval["log_loss"].mean()),
        "accuracy": float(df_eval["correct"].mean()),
    }

    # 4. Significance Testing vs Baselines
    baseline_specs = [
        {"name": "Market Consensus (Avg)", "rps_col": "rps_market", "correct_col": "correct_market"},
        {"name": "Retail Bookmaker (B365)", "rps_col": "rps_b365", "correct_col": "correct_b365"},
        {"name": "Empirical Prior", "rps_col": "rps_empirical", "correct_col": "correct_empirical"},
        {"name": "Naive Uniform", "rps_col": "rps_uniform", "correct_col": "correct_uniform"},
    ]
    significance = evaluate_significance_suite(
        df_eval=df_eval,
        model_rps_col="rps",
        model_correct_col="correct",
        baseline_specs=baseline_specs,
        season_col="Season",
    )

    # 5. Calibration
    outcomes_1hot = np.zeros((len(df_eval), 3))
    for i, ftr in enumerate(df_eval["FTR"]):
        idx = 0 if ftr == "H" else (1 if ftr == "D" else 2)
        outcomes_1hot[i, idx] = 1.0

    model_probs = df_eval[["prob_home", "prob_draw", "prob_away"]].to_numpy()
    cal_res = compute_calibration(model_probs, outcomes_1hot, n_bins=10)
    calibration_data = {
        "ece_overall": cal_res.ece_overall,
        "ece_home": cal_res.ece_home,
        "ece_draw": cal_res.ece_draw,
        "ece_away": cal_res.ece_away,
        "mce_home": cal_res.mce_home,
        "mce_draw": cal_res.mce_draw,
        "mce_away": cal_res.mce_away,
    }

    # 6. Financial Backtesting
    backtests: dict[str, dict] = {}
    for odds_pfx in ["Avg", "B365"]:
        for stak in ["flat", "quarter_kelly"]:
            res = simulate_betting(
                df_eval,
                odds_col_prefix=odds_pfx,
                edge_threshold=args.edge,
                staking=stak,
            )
            key = f"{odds_pfx}_{stak}"
            backtests[key] = {
                "odds_source": odds_pfx,
                "staking": stak,
                "total_bets": res.total_bets,
                "turnover": res.turnover,
                "net_pnl": res.net_pnl,
                "roi": res.roi,
                "win_rate": res.win_rate,
                "max_drawdown_pct": res.max_drawdown_pct,
                "annualized_sharpe": res.annualized_sharpe,
            }

    # 7. Go / No-Go Sanity Verification Gates
    logger.info("=== Go / No-Go Sanity Verification Gates ===")
    agg_rps = agg_metrics["rps"]
    logger.info("Aggregate Out-of-Sample RPS: %.4f", agg_rps)
    if agg_rps < 0.150:
        raise ValueError(
            f"SANITY GATE FAILURE: RPS={agg_rps:.4f} < 0.150! "
            "Severe risk of forward-looking data leakage."
        )
    if not (0.180 <= agg_rps <= 0.240):
        logger.warning(
            "RPS %.4f outside typical empirical range [0.180, 0.240]", agg_rps
        )

    for key, b_data in backtests.items():
        if b_data["staking"] == "flat":
            roi = b_data["roi"]
            logger.info("Flat Staking ROI against %s: %+.2f%%", b_data["odds_source"], roi)
            if roi > 10.0:
                raise ValueError(
                    f"SANITY GATE FAILURE: Flat ROI against {b_data['odds_source']} = {roi:.2f}% > +10.0%! "
                    "Unrealistic beating of closing market lines indicates odds alignment bug."
                )

    # 8. Build & Save Report
    report = EvaluationReport(
        model_name=args.model,
        folds=fold_metrics,
        aggregate_metrics=agg_metrics,
        significance_results=significance,
        backtest_results=backtests,
        calibration_results=calibration_data,
    )

    report.print_summary()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report.to_markdown(), encoding="utf-8")
    logger.info("Benchmark report saved to %s", out_path)


if __name__ == "__main__":
    main()
