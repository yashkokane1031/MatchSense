"""Unit tests for statistical significance tests (Wilcoxon Pratt & McNemar)."""

import numpy as np
import pandas as pd
import pytest

from ml.evaluation.significance import (
    evaluate_significance_suite,
    mcnemar_accuracy_test,
    wilcoxon_rps_test,
)


def test_wilcoxon_identical_models():
    """Identical models should return p-value = 1.0 and zero difference."""
    rps = np.array([0.2, 0.3, 0.1, 0.4, 0.25])
    res = wilcoxon_rps_test(rps, rps)
    assert res.p_value == pytest.approx(1.0)
    assert res.mean_diff == pytest.approx(0.0)


def test_wilcoxon_significant_improvement():
    """Model A strictly lower RPS than Model B should yield negative difference and small p-value."""
    rps_a = np.linspace(0.1, 0.3, 50)
    rps_b = rps_a + 0.05
    res = wilcoxon_rps_test(rps_a, rps_b)
    assert res.mean_diff < 0.0
    assert res.p_value < 0.001


def test_mcnemar_exact_binomial_fallback():
    """Small discordant count (n10 + n01 < 25) must use exact two-sided binomial test."""
    correct_a = np.array([1] * 10 + [0] * 2 + [1] * 50 + [0] * 10)
    correct_b = np.array([0] * 10 + [1] * 2 + [1] * 50 + [0] * 10)
    res = mcnemar_accuracy_test(correct_a, correct_b)
    assert res.is_exact is True
    assert res.p_value < 0.05


def test_mcnemar_large_sample_continuity():
    """Large discordant count (n10 + n01 >= 25) must use continuity-corrected chi2."""
    correct_a = np.array([1] * 40 + [0] * 10 + [1] * 100)
    correct_b = np.array([0] * 40 + [1] * 10 + [1] * 100)
    res = mcnemar_accuracy_test(correct_a, correct_b)
    assert res.is_exact is False
    assert res.statistic > 0.0
    assert res.p_value < 0.001


def test_evaluate_significance_suite():
    """Significance suite should produce per-fold primary tests and pooled test with caveat."""
    df = pd.DataFrame({
        "Season": ["2023-24"] * 20 + ["2024-25"] * 20,
        "rps_model": np.random.uniform(0.18, 0.22, 40),
        "correct_model": np.random.choice([0, 1], size=40, p=[0.4, 0.6]),
        "rps_base": np.random.uniform(0.20, 0.24, 40),
        "correct_base": np.random.choice([0, 1], size=40, p=[0.5, 0.5]),
    })

    res = evaluate_significance_suite(
        df_eval=df,
        model_rps_col="rps_model",
        model_correct_col="correct_model",
        baseline_specs=[{"name": "Base", "rps_col": "rps_base", "correct_col": "correct_base"}],
        season_col="Season",
    )

    assert "per_fold" in res
    assert "2023-24" in res["per_fold"]
    assert "2024-25" in res["per_fold"]
    assert "pooled" in res
    assert "caveat" in res["pooled"]
    assert "overlapping training windows" in res["pooled"]["caveat"]
