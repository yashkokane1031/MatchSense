"""Unit tests for EvaluationReport serialization and markdown rendering."""

from ml.evaluation.report import EvaluationReport


def test_report_serialization():
    rep = EvaluationReport(
        model_name="dixon_coles",
        folds=[
            {
                "season": "2023-24",
                "n_matches": 380,
                "rps": 0.201,
                "brier": 0.58,
                "log_loss": 0.98,
                "accuracy": 0.52,
            }
        ],
        aggregate_metrics={"rps": 0.201, "brier": 0.58, "log_loss": 0.98, "accuracy": 0.52},
        significance_results={},
        backtest_results={},
        calibration_results={},
    )
    md = rep.to_markdown()
    assert "dixon_coles" in md
    assert "2023-24" in md
    d = rep.to_dict()
    assert d["model_name"] == "dixon_coles"
    assert d["aggregate_rps"] == 0.201
    assert d["fold_0_season"] == "2023-24"


def test_report_hierarchical_significance():
    rep = EvaluationReport(
        model_name="dixon_coles",
        folds=[
            {
                "season": "2023-24",
                "n_matches": 380,
                "rps": 0.201,
                "brier": 0.58,
                "log_loss": 0.98,
                "accuracy": 0.52,
            },
            {
                "season": "2024-25",
                "n_matches": 380,
                "rps": 0.205,
                "brier": 0.59,
                "log_loss": 1.01,
                "accuracy": 0.50,
            },
        ],
        aggregate_metrics={"rps": 0.203, "brier": 0.585, "log_loss": 0.995, "accuracy": 0.51},
        significance_results={
            "per_fold": {
                "2023-24": {
                    "Market Consensus (Avg)": {
                        "wilcoxon": {"statistic": 34500.0, "p_value": 0.042, "mean_diff": -0.002},
                        "mcnemar": {"statistic": 4.5, "p_value": 0.034, "is_exact": False},
                    }
                }
            },
            "pooled": {
                "caveat": "The pooled 1,140-match significance test combines overlapping training windows...",
                "results": {
                    "Market Consensus (Avg)": {
                        "wilcoxon": {"statistic": 105000.0, "p_value": 0.065, "mean_diff": -0.0015},
                        "mcnemar": {"statistic": 2.8, "p_value": 0.094, "is_exact": False},
                    }
                },
            },
        },
        backtest_results={
            "Avg_flat": {
                "odds_source": "Avg",
                "staking": "flat",
                "total_bets": 450,
                "turnover": 450.0,
                "net_pnl": 12.5,
                "roi": 2.78,
                "win_rate": 0.44,
                "max_drawdown_pct": 8.5,
                "annualized_sharpe": 0.75,
            }
        },
        calibration_results={
            "ece_overall": 0.025,
            "ece_home": 0.021,
            "ece_draw": 0.031,
            "ece_away": 0.023,
            "mce_home": 0.045,
            "mce_draw": 0.060,
            "mce_away": 0.052,
        },
    )

    md = rep.to_markdown()
    assert "Per-Fold Independent" in md or "Primary" in md
    assert "2023-24" in md
    assert "Market Consensus (Avg)" in md
    assert "overlapping training windows" in md
    assert "Avg_flat" in md or "Avg" in md
    assert "Calibration" in md
    assert "0.0250" in md or "2.5%" in md


def test_report_print_summary(capsys):
    rep = EvaluationReport(
        model_name="dixon_coles",
        folds=[],
        aggregate_metrics={"rps": 0.20},
        significance_results={},
        backtest_results={},
        calibration_results={},
    )
    rep.print_summary()
    captured = capsys.readouterr()
    assert "dixon_coles" in captured.out
