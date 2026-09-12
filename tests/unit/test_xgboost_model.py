"""Unit tests for XGBoostPredictor and BasePredictor decoupling."""

import numpy as np
import pandas as pd
import pytest

from ml.models.base import BasePredictor
from ml.models.xgboost_model import XGBoostPredictor


@pytest.fixture
def mock_training_data():
    np.random.seed(42)
    teams = ["Arsenal", "Chelsea", "Liverpool", "Man City"]
    records = []
    dates = pd.date_range("2023-08-11", periods=60, freq="7D")
    for d in dates:
        h, a = np.random.choice(teams, size=2, replace=False)
        fthg = int(np.random.poisson(1.5))
        ftag = int(np.random.poisson(1.1))
        ftr = "H" if fthg > ftag else ("D" if fthg == ftag else "A")
        records.append({
            "Date": d,
            "Season": "2023-24",
            "HomeTeam": h,
            "AwayTeam": a,
            "FTHG": fthg,
            "FTAG": ftag,
            "FTR": ftr,
            "HS": fthg + 8,
            "AS": ftag + 6,
            "HST": fthg + 3,
            "AST": ftag + 2,
            "HC": 5,
            "AC": 4,
        })
    return pd.DataFrame(records)


def test_xgboost_predictor_satisfies_base_interface():
    model = XGBoostPredictor()
    assert isinstance(model, BasePredictor)
    assert model.model_name == "xgboost"
    assert model.predict_score_distribution("Arsenal", "Chelsea") is None
    assert model.predict_most_likely_score("Arsenal", "Chelsea") is None
    assert model.get_team_strengths() is None


def test_xgboost_fit_and_predict_proba(mock_training_data):
    model = XGBoostPredictor()
    model.fit(mock_training_data)
    assert len(model.feature_names) > 10

    probs = model.predict_proba("Arsenal", "Chelsea")
    assert "prob_home" in probs
    assert "prob_draw" in probs
    assert "prob_away" in probs
    total_prob = probs["prob_home"] + probs["prob_draw"] + probs["prob_away"]
    assert total_prob == pytest.approx(1.0, abs=1e-4)
    assert 0.0 <= probs["prob_home"] <= 1.0
    assert 0.0 <= probs["prob_draw"] <= 1.0
    assert 0.0 <= probs["prob_away"] <= 1.0


def test_xgboost_cold_start_fallback_for_promoted_team(mock_training_data):
    model = XGBoostPredictor()
    model.fit(mock_training_data)
    # "Luton" has zero matches in mock_training_data, but is a real team triggering cold-start fallback
    probs = model.predict_proba("Arsenal", "Luton")
    assert probs["prob_home"] > 0
    assert probs["prob_away"] > 0
    total_prob = probs["prob_home"] + probs["prob_draw"] + probs["prob_away"]
    assert total_prob == pytest.approx(1.0, abs=1e-4)
