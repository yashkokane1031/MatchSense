"""Integration test for multi-model walk-forward cross validation and comparison."""

import pandas as pd
import pytest

from ml.evaluation.significance import wilcoxon_rps_test
from ml.evaluation.walk_forward import run_walk_forward_cv
from ml.models.dixon_coles import DixonColesModel
from ml.models.xgboost_model import XGBoostPredictor


@pytest.fixture
def mini_league_dataset():
    """Small realistic 6-team dataset across 2 seasons with match stats."""
    dates = pd.date_range("2023-08-11", periods=60, freq="7D")
    teams = ["Arsenal", "Chelsea", "Liverpool", "Man City", "Tottenham", "Aston Villa"]
    rows = []
    for i, d in enumerate(dates):
        ht = teams[i % 6]
        at = teams[(i + 1) % 6]
        season = "2023-24" if i < 30 else "2024-25"
        gw = (i % 30) // 3 + 1
        fthg = int(i % 3)
        ftag = int((i + 2) % 3)
        ftr = "H" if fthg > ftag else ("D" if fthg == ftag else "A")
        rows.append({
            "Season": season,
            "Gameweek": gw,
            "Date": d,
            "HomeTeam": ht,
            "AwayTeam": at,
            "FTHG": fthg,
            "FTAG": ftag,
            "FTR": ftr,
            "HS": fthg + 10,
            "AS": ftag + 8,
            "HST": fthg + 4,
            "AST": ftag + 3,
            "HC": 6,
            "AC": 4,
            "AvgH": 2.2,
            "AvgD": 3.4,
            "AvgA": 3.6,
            "B365H": 2.1,
            "B365D": 3.5,
            "B365A": 3.7,
        })
    return pd.DataFrame(rows)


def test_multi_model_cv_execution_and_comparison(mini_league_dataset):
    # 1. Run Dixon-Coles walk-forward
    dc_eval, dc_metrics = run_walk_forward_cv(
        model_factory=lambda: DixonColesModel(xi=0.005),
        matches_df=mini_league_dataset,
        test_seasons=["2024-25"],
        window_size_seasons=1,
    )
    assert len(dc_eval) == 30
    assert "prob_home" in dc_eval.columns

    # 2. Run XGBoost walk-forward
    xgb_eval, xgb_metrics = run_walk_forward_cv(
        model_factory=lambda: XGBoostPredictor(),
        matches_df=mini_league_dataset,
        test_seasons=["2024-25"],
        window_size_seasons=1,
    )
    assert len(xgb_eval) == 30
    assert "prob_home" in xgb_eval.columns

    # 3. Direct head-to-head comparison
    rps_dc = dc_eval["rps"].to_numpy()
    rps_xgb = xgb_eval["rps"].to_numpy()

    diff_rps = float(rps_xgb.mean() - rps_dc.mean())
    assert isinstance(diff_rps, float)

    # Paired Wilcoxon
    wilc = wilcoxon_rps_test(rps_xgb, rps_dc)
    assert hasattr(wilc, "p_value")
    assert hasattr(wilc, "statistic")
