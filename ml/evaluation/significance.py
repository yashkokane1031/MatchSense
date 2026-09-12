"""Hypothesis testing for comparative model evaluation."""

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class WilcoxonResult:
    statistic: float
    p_value: float
    mean_diff: float
    median_diff: float
    n_pairs: int


@dataclass(frozen=True)
class McNemarResult:
    statistic: float
    p_value: float
    n10: int
    n01: int
    is_exact: bool


def wilcoxon_rps_test(rps_a: np.ndarray, rps_b: np.ndarray) -> WilcoxonResult:
    """Paired Wilcoxon signed-rank test on match-by-match RPS differences.

    Uses Pratt zero-method: zero-differences are retained in the ranking pool,
    and only their signed-rank contributions are dropped from the test statistic.
    """
    rps_a = np.asarray(rps_a, dtype=float)
    rps_b = np.asarray(rps_b, dtype=float)
    diff = rps_a - rps_b
    n = len(diff)

    if np.all(diff == 0.0):
        return WilcoxonResult(
            statistic=0.0, p_value=1.0, mean_diff=0.0, median_diff=0.0, n_pairs=n
        )

    res = stats.wilcoxon(diff, zero_method="pratt", alternative="two-sided")
    return WilcoxonResult(
        statistic=float(res.statistic),
        p_value=float(res.pvalue),
        mean_diff=float(np.mean(diff)),
        median_diff=float(np.median(diff)),
        n_pairs=n,
    )


def mcnemar_accuracy_test(
    correct_a: np.ndarray, correct_b: np.ndarray
) -> McNemarResult:
    """McNemar's test for paired classification accuracy.

    Uses continuity correction for discordant counts >= 25, and exact
    two-sided binomial test when discordant counts < 25.
    """
    correct_a = np.asarray(correct_a, dtype=int)
    correct_b = np.asarray(correct_b, dtype=int)

    n10 = int(np.sum((correct_a == 1) & (correct_b == 0)))
    n01 = int(np.sum((correct_a == 0) & (correct_b == 1)))
    discordant = n10 + n01

    if discordant == 0:
        return McNemarResult(statistic=0.0, p_value=1.0, n10=0, n01=0, is_exact=True)

    if discordant < 25:
        # Exact two-sided binomial test under H0: p=0.5
        k = min(n10, n01)
        p_val = float(2.0 * stats.binom.cdf(k, discordant, 0.5))
        p_val = min(1.0, p_val)
        return McNemarResult(statistic=float(k), p_value=p_val, n10=n10, n01=n01, is_exact=True)

    # Continuity-corrected chi-squared test: (|n10 - n01| - 1)^2 / (n10 + n01)
    chi2_stat = float(((abs(n10 - n01) - 1.0) ** 2) / discordant)
    p_val = float(1.0 - stats.chi2.cdf(chi2_stat, df=1))
    return McNemarResult(statistic=chi2_stat, p_value=p_val, n10=n10, n01=n01, is_exact=False)


def evaluate_significance_suite(
    df_eval: pd.DataFrame,
    model_rps_col: str,
    model_correct_col: str,
    baseline_specs: list[dict[str, str]],
    season_col: str = "Season",
) -> dict[str, Any]:
    """Evaluate statistical significance per fold (primary evidence) and pooled (descriptive with caveat).

    Args:
        df_eval: DataFrame of evaluated out-of-sample matches.
        model_rps_col: Column name for model's RPS values.
        model_correct_col: Column name for model's binary correctness (1/0).
        baseline_specs: List of dicts with keys 'name', 'rps_col', 'correct_col'.
        season_col: Column name identifying the season.

    Returns:
        Structured dict with 'per_fold' (primary) and 'pooled' (descriptive with caveat).
    """
    seasons = sorted(df_eval[season_col].unique()) if season_col in df_eval.columns else []
    per_fold: dict[str, dict[str, Any]] = {}

    for s in seasons:
        s_df = df_eval[df_eval[season_col] == s]
        per_fold[str(s)] = {}
        for b in baseline_specs:
            w_res = wilcoxon_rps_test(s_df[model_rps_col].to_numpy(), s_df[b["rps_col"]].to_numpy())
            m_res = mcnemar_accuracy_test(s_df[model_correct_col].to_numpy(), s_df[b["correct_col"]].to_numpy())
            per_fold[str(s)][b["name"]] = {"wilcoxon": w_res, "mcnemar": m_res}

    pooled_results: dict[str, dict[str, Any]] = {}
    for b in baseline_specs:
        w_res = wilcoxon_rps_test(df_eval[model_rps_col].to_numpy(), df_eval[b["rps_col"]].to_numpy())
        m_res = mcnemar_accuracy_test(df_eval[model_correct_col].to_numpy(), df_eval[b["correct_col"]].to_numpy())
        pooled_results[b["name"]] = {"wilcoxon": w_res, "mcnemar": m_res}

    caveat = (
        "The pooled 1,140-match significance test combines overlapping training windows across "
        "adjacent seasons; per-fold test statistics provide the primary independent verification."
    )

    return {
        "per_fold": per_fold,
        "pooled": {"caveat": caveat, "results": pooled_results},
    }
