"""Prediction service encapsulating prediction domain logic."""

from typing import Any

from backend.api.dependencies import get_model
from ml.data.schemas import KNOWN_PL_TEAMS
from ml.models.base import BasePredictor


class PredictionService:
    """Service providing match prediction operations."""

    def __init__(self, model: BasePredictor | None = None):
        self._model = model

    @property
    def model(self) -> BasePredictor:
        """Get the model instance, falling back to dependency injector."""
        if self._model is not None:
            return self._model
        return get_model()

    def predict_match(self, home_team: str, away_team: str) -> dict[str, Any]:
        """Predict match outcome probabilities, most likely score, and distribution.

        Args:
            home_team: Canonical home team name.
            away_team: Canonical away team name.

        Returns:
            Dict matching MatchPrediction schema.
        """
        model = self.model
        model_teams = getattr(model, "teams", getattr(model, "_teams", []))
        known_pool = set(model_teams) | KNOWN_PL_TEAMS
        for team in [home_team, away_team]:
            if team not in known_pool:
                known = ", ".join(sorted(known_pool))
                raise ValueError(f"Unknown team '{team}'. Known teams: {known}")

        has_allow = hasattr(model, "allow_unknown")
        prev_allow = getattr(model, "allow_unknown", False)
        if has_allow:
            setattr(model, "allow_unknown", True)

        try:
            proba = model.predict_proba(home_team, away_team)
            score = model.predict_most_likely_score(home_team, away_team)
            dist = model.predict_score_distribution(home_team, away_team)
        finally:
            if has_allow:
                setattr(model, "allow_unknown", prev_allow)

        predicted_score = (
            {"home": score[0], "away": score[1]} if score is not None else None
        )
        score_distribution = dist.tolist() if dist is not None else None

        return {
            "home_team": home_team,
            "away_team": away_team,
            "prob_home": round(proba["prob_home"], 4),
            "prob_draw": round(proba["prob_draw"], 4),
            "prob_away": round(proba["prob_away"], 4),
            "predicted_score": predicted_score,
            "score_distribution": score_distribution,
            "model": model.model_name,
        }

    def list_teams(self) -> list[str]:
        """Return sorted list of known teams."""
        model_teams = getattr(self.model, "teams", getattr(self.model, "_teams", []))
        return sorted(model_teams)

    def get_team_strength(self, team_name: str) -> dict[str, Any]:
        """Return attack and defense parameters for team.

        Raises:
            ValueError: If model does not support strengths or team is unknown.
        """
        strengths = self.model.get_team_strengths()
        if strengths is None:
            raise ValueError(
                f"Active model '{self.model.model_name}' does not provide attack/defense parameter decompositions."
            )
        if team_name not in strengths:
            known = ", ".join(sorted(strengths.keys()))
            raise ValueError(f"Unknown team '{team_name}'. Known teams: {known}")
        return {
            "team": team_name,
            "attack": round(strengths[team_name]["attack"], 4),
            "defense": round(strengths[team_name]["defense"], 4),
        }
