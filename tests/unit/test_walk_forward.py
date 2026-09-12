"""Unit tests for rolling fixed-window walk-forward cross validation."""

import pandas as pd
import pytest

from ml.evaluation.walk_forward import run_walk_forward_cv
from ml.models.dixon_coles import DixonColesModel


@pytest.fixture
def synthetic_seasons_data():
    """Create 5 teams across 2 small test seasons (20 matches per season)."""
    dates = pd.date_range("2023-08-01", periods=40, freq="7D")
    teams = ["Arsenal", "Chelsea", "Liverpool", "ManCity", "Tottenham"]
    rows = []
    for i in range(40):
        ht = teams[i % 5]
        at = teams[(i + 1) % 5]
        season = "2023-24" if i < 20 else "2024-25"
        gw = (i % 20) + 1
        rows.append({
            "Season": season,
            "Gameweek": gw,
            "Date": dates[i],
            "HomeTeam": ht,
            "AwayTeam": at,
            "FTHG": (i % 3),
            "FTAG": ((i + 1) % 2),
            "FTR": "H" if (i % 3) > ((i + 1) % 2) else ("D" if (i % 3) == ((i + 1) % 2) else "A"),
            "AvgH": 2.1,
            "AvgD": 3.3,
            "AvgA": 3.8,
            "B365H": 2.0,
            "B365D": 3.4,
            "B365A": 4.0,
        })
    return pd.DataFrame(rows)


def test_walk_forward_execution(synthetic_seasons_data):
    """Walk forward CV runs on test season using rolling 1-season window."""
    df_eval, fold_metrics = run_walk_forward_cv(
        model_factory=lambda: DixonColesModel(xi=0.005),
        matches_df=synthetic_seasons_data,
        test_seasons=["2024-25"],
        window_size_seasons=1,
    )
    assert len(df_eval) == 20
    assert "prob_home" in df_eval.columns
    assert "prob_home_uniform" in df_eval.columns
    assert "prob_home_market" in df_eval.columns
    assert "prob_home_b365" in df_eval.columns
    assert "prob_home_empirical" in df_eval.columns
    assert len(fold_metrics) == 1
    assert "rps" in fold_metrics[0]
    assert "accuracy" in fold_metrics[0]
