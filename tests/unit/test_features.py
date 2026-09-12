"""Tests for feature engineering.

Covers: form features, H2H features, season-boundary reset,
newly promoted teams, and data leakage prevention.
"""

import pandas as pd

from ml.features.form import compute_form_features, compute_temporal_features
from ml.features.h2h import compute_h2h_features
from ml.features.pipeline import build_match_features


class TestFormFeatures:
    """Test recent form feature computation."""

    def test_form_after_several_matches(self, sample_matches):
        """Form features should be computed correctly after 5+ matches."""
        # Arsenal has played several matches by 2024-10-05
        features = compute_form_features(
            sample_matches, "Arsenal",
            pd.Timestamp("2024-10-05"), "2024-25", window=5,
        )
        assert features["matches_available"] > 0
        assert features["points_last_n"] is not None
        assert features["wins_last_n"] >= 0
        assert features["losses_last_n"] >= 0

    def test_form_first_match_of_season(self, sample_matches):
        """First match of season should return null/empty form."""
        features = compute_form_features(
            sample_matches, "Arsenal",
            pd.Timestamp("2024-08-17"), "2024-25", window=5,
        )
        # No matches before the first match
        assert features["matches_available"] == 0
        assert features["points_last_n"] is None

    def test_form_partial_window(self, sample_matches):
        """Early in season, form uses however many matches are available."""
        # Arsenal has played 3 matches before 2024-08-31 in sample_matches
        features = compute_form_features(
            sample_matches, "Arsenal",
            pd.Timestamp("2024-08-31"), "2024-25", window=5,
        )
        assert features["matches_available"] == 3

    def test_form_does_not_leak_future_data(self, sample_matches):
        """Features must NOT use data from after the match date."""
        date = pd.Timestamp("2024-09-14")
        features = compute_form_features(
            sample_matches, "Arsenal", date, "2024-25", window=5,
        )
        # Arsenal's matches on 2024-09-14 and after should NOT be counted
        matches_before = sample_matches[
            (sample_matches["Date"] < date)
            & (
                (sample_matches["HomeTeam"] == "Arsenal")
                | (sample_matches["AwayTeam"] == "Arsenal")
            )
            & (sample_matches["Season"] == "2024-25")
        ]
        assert features["matches_available"] == len(matches_before)


class TestSeasonBoundary:
    """Test that form features reset at season boundaries."""

    def test_form_resets_at_season_start(self, multi_season_matches):
        """Form features should NOT carry over from previous season."""
        # First match of 2024-25 season
        features = compute_form_features(
            multi_season_matches, "Arsenal",
            pd.Timestamp("2024-08-17"), "2024-25", window=5,
        )
        # Despite having 2023-24 data, form should be null (reset at season start)
        assert features["matches_available"] == 0
        assert features["points_last_n"] is None

    def test_newly_promoted_team_has_no_form(self, multi_season_matches):
        """Newly promoted team should have null form features."""
        features = compute_form_features(
            multi_season_matches, "Ipswich",
            pd.Timestamp("2024-08-17"), "2024-25", window=5,
        )
        assert features["matches_available"] == 0
        assert features["points_last_n"] is None

    def test_is_newly_promoted_flag(self, multi_season_matches):
        """is_newly_promoted should be True for teams not in previous season."""
        all_seasons = sorted(multi_season_matches["Season"].unique().tolist())
        temporal = compute_temporal_features(
            multi_season_matches, "Ipswich",
            pd.Timestamp("2024-08-17"), "2024-25", all_seasons,
        )
        assert temporal["is_newly_promoted"] is True

    def test_established_team_not_promoted(self, multi_season_matches):
        """Teams present in previous season should NOT be flagged as promoted."""
        all_seasons = sorted(multi_season_matches["Season"].unique().tolist())
        temporal = compute_temporal_features(
            multi_season_matches, "Arsenal",
            pd.Timestamp("2024-08-17"), "2024-25", all_seasons,
        )
        assert temporal["is_newly_promoted"] is False


class TestH2HFeatures:
    """Test head-to-head feature computation."""

    def test_h2h_with_history(self, sample_matches):
        """H2H features should reflect actual results."""
        features = compute_h2h_features(
            sample_matches, "Arsenal", "Chelsea",
            pd.Timestamp("2024-10-05"),
        )
        assert features["h2h_total_matches"] > 0
        total = (
            features["h2h_home_team_wins"]
            + features["h2h_draws"]
            + features["h2h_away_team_wins"]
        )
        assert total == features["h2h_total_matches"]

    def test_h2h_no_history(self, sample_matches):
        """Teams that never met should get null H2H features."""
        # Create a dataset where two specific teams never meet
        features = compute_h2h_features(
            sample_matches, "Arsenal", "Nonexistent",
            pd.Timestamp("2024-10-05"),
        )
        assert features["h2h_total_matches"] == 0
        assert features["h2h_home_team_wins"] is None


class TestFeaturePipeline:
    """Test the full feature pipeline orchestrator."""

    def test_build_match_features_returns_all_keys(self, sample_matches):
        """Pipeline should return features for both teams plus H2H."""
        all_seasons = ["2024-25"]
        features = build_match_features(
            sample_matches, "Arsenal", "Chelsea",
            pd.Timestamp("2024-10-05"), "2024-25", all_seasons,
        )
        # Check home team features present
        assert "home_points_last_n" in features
        assert "home_matches_played" in features
        # Check away team features present
        assert "away_points_last_n" in features
        # Check H2H features present
        assert "h2h_total_matches" in features
        # Check temporal features
        assert "home_days_since_last_match" in features
        assert "home_is_newly_promoted" in features
