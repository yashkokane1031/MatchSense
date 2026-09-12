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

    def predict_score_distribution(
        self, home_team: str, away_team: str, max_goals: int = 8
    ) -> np.ndarray | None:
        """Predict the joint score probability distribution.

        Optional. Returns None for models that do not natively model joint scores.

        Args:
            home_team: Canonical name of the home team.
            away_team: Canonical name of the away team.
            max_goals: Maximum goals to consider per team.

        Returns:
            (max_goals+1, max_goals+1) numpy array or None.
        """
        return None

    def predict_most_likely_score(
        self, home_team: str, away_team: str
    ) -> tuple[int, int] | None:
        """Predict the single most likely scoreline.

        Optional. Returns None if score distribution is not supported.

        Args:
            home_team: Canonical name of the home team.
            away_team: Canonical name of the away team.

        Returns:
            Tuple of (home_goals, away_goals) or None.
        """
        dist = self.predict_score_distribution(home_team, away_team)
        if dist is None:
            return None
        idx = np.unravel_index(dist.argmax(), dist.shape)
        return int(idx[0]), int(idx[1])

    def get_team_strengths(self) -> dict[str, dict[str, float]] | None:
        """Return estimated attack/defense strengths for all teams.

        Optional. Returns None for models without alpha/beta parameter decomposition.

        Returns:
            Dict mapping team name to {"attack": float, "defense": float} or None.
        """
        return None

    def get_model_info(self) -> dict[str, object]:
        """Return human-readable metadata about the model instance.

        Optional. Subclasses can override to return model parameters and status.
        """
        return {"model_name": self.model_name}

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Human-readable model name for API responses."""
        ...
