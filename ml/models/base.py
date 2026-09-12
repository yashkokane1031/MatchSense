"""Abstract base class for prediction models.

All models (Dixon-Coles, XGBoost in Phase 2) implement this interface,
enabling clean comparison and interchangeable use in the API layer.
"""

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd


class BasePredictor(ABC):
    """Interface that every prediction model must implement."""

    @abstractmethod
    def fit(self, matches: pd.DataFrame) -> "BasePredictor":
        """Fit the model on historical match data.

        Args:
            matches: DataFrame with at minimum HomeTeam, AwayTeam, FTHG, FTAG, Date columns.

        Returns:
            Self, for method chaining.
        """
        ...

    @abstractmethod
    def predict_proba(self, home_team: str, away_team: str) -> dict[str, float]:
        """Predict outcome probabilities for a match.

        Args:
            home_team: Canonical name of the home team.
            away_team: Canonical name of the away team.

        Returns:
            Dict with keys 'prob_home', 'prob_draw', 'prob_away'.
            Values sum to ~1.0.
        """
        ...

    @abstractmethod
    def predict_score_distribution(
        self, home_team: str, away_team: str, max_goals: int = 8
    ) -> np.ndarray:
        """Predict the joint score probability distribution.

        Args:
            home_team: Canonical name of the home team.
            away_team: Canonical name of the away team.
            max_goals: Maximum goals to consider per team.

        Returns:
            (max_goals+1, max_goals+1) numpy array where entry [i, j]
            is P(home_goals=i, away_goals=j).
        """
        ...

    def predict_most_likely_score(self, home_team: str, away_team: str) -> tuple[int, int]:
        """Predict the single most likely scoreline.

        Args:
            home_team: Canonical name of the home team.
            away_team: Canonical name of the away team.

        Returns:
            Tuple of (home_goals, away_goals) for the most probable score.
        """
        dist = self.predict_score_distribution(home_team, away_team)
        idx = np.unravel_index(dist.argmax(), dist.shape)
        return int(idx[0]), int(idx[1])

    @abstractmethod
    def get_team_strengths(self) -> dict[str, dict[str, float]]:
        """Return estimated attack/defense strengths for all teams.

        Returns:
            Dict mapping team name to {"attack": float, "defense": float}.
        """
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Human-readable model name for API responses."""
        ...
