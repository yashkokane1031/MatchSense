"""Unit tests for dynamic season derivation logic."""

from datetime import datetime, timezone

import pytest

from ml.data.season import (
    derive_current_season,
    derive_season_from_date,
    derive_training_window,
    _season_code_from_start_year,
    _season_label_from_start_year,
    _start_year_from_code,
)


# --- Helper function tests ---


class TestSeasonConversions:
    def test_code_from_start_year(self):
        assert _season_code_from_start_year(2026) == "2627"
        assert _season_code_from_start_year(2025) == "2526"
        assert _season_code_from_start_year(2023) == "2324"

    def test_label_from_start_year(self):
        assert _season_label_from_start_year(2026) == "2026-27"
        assert _season_label_from_start_year(2025) == "2025-26"

    def test_start_year_from_code(self):
        assert _start_year_from_code("2627") == 2026
        assert _start_year_from_code("2526") == 2025
        assert _start_year_from_code("2324") == 2023
        assert _start_year_from_code("0102") == 2001


# --- Date-based fallback tests ---


class TestDeriveSeasonFromDate:
    """Tests for the date-based fallback path."""

    def test_september_maps_to_current_year(self):
        """Sep 2026 → 2026-27 season."""
        now = datetime(2026, 9, 13, tzinfo=timezone.utc)
        code, label = derive_season_from_date(now)
        assert code == "2627"
        assert label == "2026-27"

    def test_march_maps_to_previous_year(self):
        """Mar 2027 → still 2026-27 season."""
        now = datetime(2027, 3, 15, tzinfo=timezone.utc)
        code, label = derive_season_from_date(now)
        assert code == "2627"
        assert label == "2026-27"

    def test_august_maps_to_new_season(self):
        """Aug 2025 → 2025-26 season."""
        now = datetime(2025, 8, 1, tzinfo=timezone.utc)
        code, label = derive_season_from_date(now)
        assert code == "2526"
        assert label == "2025-26"

    def test_july_maps_to_previous_season(self):
        """Jul 2026 → still 2025-26 season (pre-season)."""
        now = datetime(2026, 7, 31, tzinfo=timezone.utc)
        code, label = derive_season_from_date(now)
        assert code == "2526"
        assert label == "2025-26"

    def test_january_maps_to_previous_year_start(self):
        """Jan 2027 → 2026-27 season (mid-season)."""
        now = datetime(2027, 1, 1, tzinfo=timezone.utc)
        code, label = derive_season_from_date(now)
        assert code == "2627"
        assert label == "2026-27"

    def test_may_maps_to_previous_year_start(self):
        """May 2026 → 2025-26 season (end of season)."""
        now = datetime(2026, 5, 25, tzinfo=timezone.utc)
        code, label = derive_season_from_date(now)
        assert code == "2526"
        assert label == "2025-26"


# --- API-first derivation tests ---


class TestDeriveCurrentSeason:
    """Tests for the primary derive_current_season() function."""

    def test_api_season_takes_priority(self):
        """When API reports a season, it wins over date-math."""
        api = ("2627", "2026-27")
        # Even if date-math would say "2526", the API answer wins
        now = datetime(2026, 7, 15, tzinfo=timezone.utc)  # date-math → "2526"
        code, label = derive_current_season(api_season=api, now=now)
        assert code == "2627"
        assert label == "2026-27"

    def test_api_season_none_falls_back_to_date(self):
        """When API season is None, date-math fallback activates."""
        now = datetime(2026, 9, 13, tzinfo=timezone.utc)
        code, label = derive_current_season(api_season=None, now=now)
        assert code == "2627"
        assert label == "2026-27"

    def test_api_season_empty_strings_falls_back_to_date(self):
        """Empty API strings are treated as absent."""
        now = datetime(2026, 9, 13, tzinfo=timezone.utc)
        code, label = derive_current_season(api_season=("", ""), now=now)
        assert code == "2627"
        assert label == "2026-27"

    def test_early_august_with_api_reporting_new_season(self):
        """Early Aug: date-math says new season, API agrees → new season."""
        api = ("2627", "2026-27")
        now = datetime(2026, 8, 5, tzinfo=timezone.utc)
        code, label = derive_current_season(api_season=api, now=now)
        assert code == "2627"
        assert label == "2026-27"

    def test_early_august_with_api_reporting_old_season(self):
        """Early Aug: date-math says new season, but API still reports old → old season wins.
        
        This is the critical edge case: the PL season hasn't started yet,
        football-data.co.uk still shows last season's fixtures, and the API
        correctly reports the old season. Without the API check, the pipeline
        would attempt to ingest a non-existent season.
        """
        api = ("2526", "2025-26")
        now = datetime(2026, 8, 5, tzinfo=timezone.utc)  # date-math → "2627"
        code, label = derive_current_season(api_season=api, now=now)
        assert code == "2526"
        assert label == "2025-26"

    def test_early_august_without_api_falls_back_to_date(self):
        """Early Aug without API: falls back to date-math (known limitation)."""
        now = datetime(2026, 8, 5, tzinfo=timezone.utc)
        code, label = derive_current_season(api_season=None, now=now)
        # Date-math says "2627" — this is the fallback's known weakness,
        # but it's the best we can do without network access.
        assert code == "2627"
        assert label == "2026-27"


# --- Training window tests ---


class TestDeriveTrainingWindow:
    def test_standard_4_season_window(self):
        result = derive_training_window("2627", 4)
        assert len(result) == 4
        assert result[0] == {"code": "2324", "label": "2023-24"}
        assert result[1] == {"code": "2425", "label": "2024-25"}
        assert result[2] == {"code": "2526", "label": "2025-26"}
        assert result[3] == {"code": "2627", "label": "2026-27"}

    def test_previous_season_window(self):
        result = derive_training_window("2526", 4)
        assert len(result) == 4
        assert result[0] == {"code": "2223", "label": "2022-23"}
        assert result[3] == {"code": "2526", "label": "2025-26"}

    def test_window_size_1(self):
        result = derive_training_window("2627", 1)
        assert len(result) == 1
        assert result[0] == {"code": "2627", "label": "2026-27"}

    def test_window_size_6(self):
        result = derive_training_window("2627", 6)
        assert len(result) == 6
        assert result[0] == {"code": "2122", "label": "2021-22"}
        assert result[5] == {"code": "2627", "label": "2026-27"}
