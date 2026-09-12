"""Shared test fixtures for MatchSense.

Provides sample match data, a fitted model, and test database sessions.
"""

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import pandas as pd
import pytest

from ml.models.dixon_coles import DixonColesModel


@pytest.fixture
def sample_matches() -> pd.DataFrame:
    """Small realistic dataset for unit tests.

    20 matches across 5 teams in 1 season, with known outcomes
    for verifiable feature calculations.
    """
    data = [
        # Season start - matchday 1
        {"Date": "2024-08-17", "HomeTeam": "Arsenal", "AwayTeam": "Liverpool", "FTHG": 2, "FTAG": 1, "FTR": "H", "Season": "2024-25"},
        {"Date": "2024-08-17", "HomeTeam": "Chelsea", "AwayTeam": "Brentford", "FTHG": 1, "FTAG": 1, "FTR": "D", "Season": "2024-25"},
        # Matchday 2
        {"Date": "2024-08-24", "HomeTeam": "Liverpool", "AwayTeam": "Chelsea", "FTHG": 3, "FTAG": 0, "FTR": "H", "Season": "2024-25"},
        {"Date": "2024-08-24", "HomeTeam": "Brentford", "AwayTeam": "Arsenal", "FTHG": 0, "FTAG": 2, "FTR": "A", "Season": "2024-25"},
        {"Date": "2024-08-24", "HomeTeam": "Wolves", "AwayTeam": "Arsenal", "FTHG": 1, "FTAG": 3, "FTR": "A", "Season": "2024-25"},
        # Matchday 3
        {"Date": "2024-08-31", "HomeTeam": "Arsenal", "AwayTeam": "Chelsea", "FTHG": 1, "FTAG": 0, "FTR": "H", "Season": "2024-25"},
        {"Date": "2024-08-31", "HomeTeam": "Liverpool", "AwayTeam": "Brentford", "FTHG": 2, "FTAG": 0, "FTR": "H", "Season": "2024-25"},
        {"Date": "2024-08-31", "HomeTeam": "Wolves", "AwayTeam": "Chelsea", "FTHG": 0, "FTAG": 2, "FTR": "A", "Season": "2024-25"},
        # Matchday 4
        {"Date": "2024-09-14", "HomeTeam": "Chelsea", "AwayTeam": "Arsenal", "FTHG": 0, "FTAG": 1, "FTR": "A", "Season": "2024-25"},
        {"Date": "2024-09-14", "HomeTeam": "Brentford", "AwayTeam": "Liverpool", "FTHG": 1, "FTAG": 2, "FTR": "A", "Season": "2024-25"},
        {"Date": "2024-09-14", "HomeTeam": "Wolves", "AwayTeam": "Liverpool", "FTHG": 0, "FTAG": 1, "FTR": "A", "Season": "2024-25"},
        # Matchday 5
        {"Date": "2024-09-21", "HomeTeam": "Arsenal", "AwayTeam": "Wolves", "FTHG": 3, "FTAG": 0, "FTR": "H", "Season": "2024-25"},
        {"Date": "2024-09-21", "HomeTeam": "Liverpool", "AwayTeam": "Wolves", "FTHG": 4, "FTAG": 1, "FTR": "H", "Season": "2024-25"},
        {"Date": "2024-09-21", "HomeTeam": "Brentford", "AwayTeam": "Chelsea", "FTHG": 2, "FTAG": 2, "FTR": "D", "Season": "2024-25"},
        # Matchday 6
        {"Date": "2024-09-28", "HomeTeam": "Chelsea", "AwayTeam": "Liverpool", "FTHG": 1, "FTAG": 1, "FTR": "D", "Season": "2024-25"},
        {"Date": "2024-09-28", "HomeTeam": "Arsenal", "AwayTeam": "Brentford", "FTHG": 2, "FTAG": 0, "FTR": "H", "Season": "2024-25"},
        {"Date": "2024-09-28", "HomeTeam": "Wolves", "AwayTeam": "Brentford", "FTHG": 1, "FTAG": 0, "FTR": "H", "Season": "2024-25"},
        # Matchday 7
        {"Date": "2024-10-05", "HomeTeam": "Liverpool", "AwayTeam": "Arsenal", "FTHG": 2, "FTAG": 2, "FTR": "D", "Season": "2024-25"},
        {"Date": "2024-10-05", "HomeTeam": "Chelsea", "AwayTeam": "Wolves", "FTHG": 3, "FTAG": 1, "FTR": "H", "Season": "2024-25"},
        {"Date": "2024-10-05", "HomeTeam": "Brentford", "AwayTeam": "Wolves", "FTHG": 2, "FTAG": 1, "FTR": "H", "Season": "2024-25"},
    ]
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


@pytest.fixture
def multi_season_matches(sample_matches: pd.DataFrame) -> pd.DataFrame:
    """Two-season dataset for testing season-boundary behavior."""
    prev_season = sample_matches.copy()
    prev_season["Season"] = "2023-24"
    prev_season["Date"] = prev_season["Date"] - pd.DateOffset(years=1)

    # Add a "promoted" team to current season
    promoted = pd.DataFrame([
        {"Date": "2024-08-17", "HomeTeam": "Ipswich", "AwayTeam": "Wolves", "FTHG": 0, "FTAG": 1, "FTR": "A", "Season": "2024-25"},
        {"Date": "2024-08-24", "HomeTeam": "Arsenal", "AwayTeam": "Ipswich", "FTHG": 2, "FTAG": 0, "FTR": "H", "Season": "2024-25"},
    ])
    promoted["Date"] = pd.to_datetime(promoted["Date"])

    combined = pd.concat([prev_season, sample_matches, promoted], ignore_index=True)
    return combined.sort_values("Date").reset_index(drop=True)


@pytest.fixture
def fitted_model(sample_matches: pd.DataFrame) -> DixonColesModel:
    """A pre-fitted Dixon-Coles model on sample data."""
    model = DixonColesModel(xi=0.005)
    model.fit(sample_matches)
    return model
