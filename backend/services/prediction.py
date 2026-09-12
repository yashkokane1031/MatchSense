"""Prediction service encapsulating prediction domain logic."""

from backend.api.dependencies import get_model
from ml.models.dixon_coles import DixonColesModel


class PredictionService:
    """Service providing match prediction operations."""

    def __init__(self, model: DixonColesModel | None = None):
        self._model = model

    @property
    def model(self) -> DixonColesModel:
        """Get the model instance, falling back to dependency injector."""
        if self._model is not None:
            return self._model
        return get_model()

    def predict_match(self, home_team: str, away_team: str) -> dict:
        """Predict match outcome probabilities, most likely score, and distribution.

        Args:
            home_team: Canonical home team name.
            away_team: Canonical away team name.

        Returns:
            Dict matching MatchPrediction schema.
        """
        model = self.model
        proba = model.predict_proba(home_team, away_team)
        score = model.predict_most_likely_score(home_team, away_team)
        dist = model.predict_score_distribution(home_team, away_team)

        return {
            "home_team": home_team,
            "away_team": away_team,
            "prob_home": round(proba["prob_home"], 4),
            "prob_draw": round(proba["prob_draw"], 4),
            "prob_away": round(proba["prob_away"], 4),
            "predicted_score": {"home": score[0], "away": score[1]},
            "score_distribution": dist.tolist(),
            "model": model.model_name,
        }

    def list_teams(self) -> list[str]:
        """Return sorted list of known teams."""
        return sorted(self.model._teams)

    def get_team_strength(self, team_name: str) -> dict:
        """Return attack and defense parameters for team.

        Raises:
            ValueError: If team is not known to the model.
        """
        strengths = self.model.get_team_strengths()
        if team_name not in strengths:
            known = ", ".join(sorted(strengths.keys()))
            raise ValueError(f"Unknown team '{team_name}'. Known teams: {known}")
        return {
            "team": team_name,
            "attack": round(strengths[team_name]["attack"], 4),
            "defense": round(strengths[team_name]["defense"], 4),
        }
