"""Unit tests for rolling match statistics and shot quality feature extractor."""

import pandas as pd
import pytest

from ml.features.match_stats import compute_match_stats_features


@pytest.fixture
def sample_match_data():
    return pd.DataFrame([
        {
            "Date": pd.Timestamp("2024-08-17"),
            "Season": "2024-25",
            "HomeTeam": "Arsenal",
            "AwayTeam": "Wolves",
            "HS": 18,
            "AS": 9,
            "HST": 6,
            "AST": 3,
            "HC": 8,
            "AC": 2,
        },
        {
            "Date": pd.Timestamp("2024-08-24"),
            "Season": "2024-25",
            "HomeTeam": "Aston Villa",
            "AwayTeam": "Arsenal",
            "HS": 11,
            "AS": 14,
            "HST": 4,
            "AST": 5,
            "HC": 3,
            "AC": 6,
        },
        {
            "Date": pd.Timestamp("2024-08-31"),
            "Season": "2024-25",
            "HomeTeam": "Arsenal",
            "AwayTeam": "Brighton",
            "HS": 12,
            "AS": 16,
            "HST": 4,
            "AST": 5,
            "HC": 4,
            "AC": 7,
        },
    ])


def test_match_stats_returns_nan_for_zero_history(sample_match_data):
    stats = compute_match_stats_features(
        sample_match_data, "Arsenal", pd.Timestamp("2024-08-17"), "2024-25"
    )
    assert stats["rolling_shots_for"] is None
    assert stats["rolling_sot_for"] is None
    assert stats["rolling_sot_ratio"] is None
    assert stats["rolling_corners_for"] is None


def test_match_stats_averages_over_prior_matches(sample_match_data):
    stats = compute_match_stats_features(
        sample_match_data, "Arsenal", pd.Timestamp("2024-08-31"), "2024-25", window=5
    )
    # Arsenal shots: 18 (home vs Wolves), 14 (away vs Villa) -> mean = 16.0
    assert stats["rolling_shots_for"] == pytest.approx(16.0)
    # Arsenal SOT: 6, 5 -> mean = 5.5
    assert stats["rolling_sot_for"] == pytest.approx(5.5)
    # SOT ratio: 5.5 / 16.0 = 0.34375
    assert stats["rolling_sot_ratio"] == pytest.approx(5.5 / 16.0, abs=1e-3)
    # Corners: 8, 6 -> mean = 7.0
    assert stats["rolling_corners_for"] == pytest.approx(7.0)
    # Opponents conceded shots to Arsenal: 9 (Wolves), 11 (Villa) -> mean = 10.0
    assert stats["rolling_shots_against"] == pytest.approx(10.0)
