"""Unit tests for window-anchored Elo rating engine."""

import numpy as np
import pandas as pd
import pytest

from ml.features.elo import EloEngine, compute_window_elo


def test_elo_win_probability_formula():
    engine = EloEngine(home_advantage=65.0)
    # Equal ratings: home team has advantage of 65 points
    p_home, p_away = engine.expected_probabilities(1500.0, 1500.0)
    assert p_home > 0.50
    assert p_home + p_away == pytest.approx(1.0)

    # 400 point difference favoring away team
    p_home_underdog, p_away_favorite = engine.expected_probabilities(1100.0, 1500.0)
    assert p_away_favorite > p_home_underdog


def test_margin_of_victory_multiplier():
    engine = EloEngine()
    assert engine.margin_multiplier(1) == 1.0
    assert engine.margin_multiplier(2) == 1.5
    assert engine.margin_multiplier(3) == pytest.approx(14.0 / 8.0)
    assert engine.margin_multiplier(4) == pytest.approx(15.0 / 8.0)


def test_summer_mean_reversion_and_promoted_entry():
    engine = EloEngine(reversion_weight=0.75)
    ratings = {
        "Arsenal": 1700.0,
        "Chelsea": 1600.0,
        "Everton": 1400.0,
        "Wolves": 1300.0,
    }
    reverted = engine.apply_season_transition(ratings, promoted_teams=["Luton"])
    # 0.75 * 1700 + 0.25 * 1500 = 1275 + 375 = 1650
    assert reverted["Arsenal"] == pytest.approx(1650.0)
    # Promoted team enters at 25th percentile of surviving post-reversion ratings
    surviving_ratings = [reverted[t] for t in ratings]
    expected_q25 = float(np.percentile(surviving_ratings, 25))
    assert reverted["Luton"] == pytest.approx(expected_q25)


def test_compute_window_elo_anchors_at_1500():
    matches = pd.DataFrame([
        {
            "Date": pd.Timestamp("2020-09-12"),
            "Season": "2020-21",
            "HomeTeam": "Arsenal",
            "AwayTeam": "Fulham",
            "FTHG": 3,
            "FTAG": 0,
            "FTR": "H",
        },
        {
            "Date": pd.Timestamp("2020-09-19"),
            "Season": "2020-21",
            "HomeTeam": "Arsenal",
            "AwayTeam": "West Ham",
            "FTHG": 2,
            "FTAG": 1,
            "FTR": "H",
        },
        {
            "Date": pd.Timestamp("2021-08-14"),
            "Season": "2021-22",
            "HomeTeam": "Arsenal",
            "AwayTeam": "Chelsea",
            "FTHG": 0,
            "FTAG": 2,
            "FTR": "A",
        },
    ])
    match_features, final_ratings = compute_window_elo(matches)
    # First match should have Arsenal and Fulham at 1500.0
    key1 = (pd.Timestamp("2020-09-12"), "Arsenal", "Fulham")
    assert match_features[key1]["home_elo"] == 1500.0
    assert match_features[key1]["away_elo"] == 1500.0
    assert match_features[key1]["elo_diff"] == 65.0  # (1500 + 65) - 1500
    # Arsenal won, rating increased for match 2
    key2 = (pd.Timestamp("2020-09-19"), "Arsenal", "West Ham")
    assert match_features[key2]["home_elo"] > 1500.0
    assert "Arsenal" in final_ratings
