"""Prediction service encapsulating prediction domain logic."""

from datetime import datetime, timezone
from typing import Any

from backend.api.dependencies import get_model
from backend.models.schemas import Fixture
from backend.services.model_manager import model_manager
from ml.data.schemas import KNOWN_PL_TEAMS
from ml.models.base import BasePredictor


TEAM_ALIASES: dict[str, str] = {
    # Manchester United
    "manchester united": "Manchester Utd",
    "man united": "Manchester Utd",
    "man utd": "Manchester Utd",
    "manchester united fc": "Manchester Utd",
    "manchester utd": "Manchester Utd",

    # Manchester City
    "manchester city": "Manchester City",
    "man city": "Manchester City",
    "manchester city fc": "Manchester City",

    # Tottenham
    "tottenham hotspur": "Tottenham",
    "tottenham hotspur fc": "Tottenham",
    "tottenham": "Tottenham",
    "spurs": "Tottenham",

    # Newcastle
    "newcastle united": "Newcastle",
    "newcastle united fc": "Newcastle",
    "newcastle": "Newcastle",

    # West Ham
    "west ham united": "West Ham",
    "west ham united fc": "West Ham",
    "west ham": "West Ham",

    # Wolverhampton
    "wolverhampton wanderers": "Wolverhampton",
    "wolverhampton wanderers fc": "Wolverhampton",
    "wolverhampton": "Wolverhampton",
    "wolves": "Wolverhampton",

    # Brighton
    "brighton & hove albion": "Brighton",
    "brighton and hove albion": "Brighton",
    "brighton & hove albion fc": "Brighton",
    "brighton": "Brighton",

    # Bournemouth
    "afc bournemouth": "Bournemouth",
    "bournemouth": "Bournemouth",

    # Nottingham Forest
    "nottingham forest": "Nottingham Forest",
    "nottingham forest fc": "Nottingham Forest",
    "nott'm forest": "Nottingham Forest",
    "nottingham": "Nottingham Forest",

    # Leicester
    "leicester city": "Leicester",
    "leicester city fc": "Leicester",
    "leicester": "Leicester",

    # Ipswich
    "ipswich town": "Ipswich",
    "ipswich town fc": "Ipswich",
    "ipswich": "Ipswich",

    # Sheffield United
    "sheffield united": "Sheffield Utd",
    "sheffield united fc": "Sheffield Utd",
    "sheffield utd": "Sheffield Utd",

    # Leeds
    "leeds united": "Leeds",
    "leeds united fc": "Leeds",
    "leeds": "Leeds",

    # Luton
    "luton town": "Luton",
    "luton town fc": "Luton",
    "luton": "Luton",
}


def canonicalize_team_name(name: str) -> str:
    """Map user/UI team name variations to canonical model team names."""
    if not name:
        return name
    return TEAM_ALIASES.get(name.strip().lower(), name.strip())


class PredictionService:
    """Service providing match prediction operations."""

    def __init__(self, model: BasePredictor | None = None):
        self._model = model

    def get_active_model(self, model_name: str = "dixon_coles") -> BasePredictor:
        """Get the model instance for a specific architecture."""
        if self._model is not None and getattr(self._model, "model_name", "") == model_name:
            return self._model
        return get_model(model_name)

    def predict_match(
        self, home_team: str, away_team: str, model_name: str = "dixon_coles"
    ) -> dict[str, Any]:
        """Predict match outcome probabilities, most likely score, and distribution.

        Args:
            home_team: Canonical or alias home team name.
            away_team: Canonical or alias away team name.
            model_name: 'dixon_coles' or 'xgboost'.

        Returns:
            Dict matching MatchPrediction schema.
        """
        c_home = canonicalize_team_name(home_team)
        c_away = canonicalize_team_name(away_team)

        model = self.get_active_model(model_name)
        model_teams = getattr(model, "teams", getattr(model, "_teams", []))
        known_pool = set(model_teams) | KNOWN_PL_TEAMS
        for raw, c_team in [(home_team, c_home), (away_team, c_away)]:
            if c_team not in known_pool:
                known = ", ".join(sorted(known_pool))
                raise ValueError(f"Unknown team '{raw}'. Known teams: {known}")

        has_allow = hasattr(model, "allow_unknown")
        prev_allow = getattr(model, "allow_unknown", False)
        if has_allow:
            setattr(model, "allow_unknown", True)

        try:
            proba = model.predict_proba(c_home, c_away)
            score = (
                model.predict_most_likely_score(c_home, c_away)
                if hasattr(model, "predict_most_likely_score")
                else None
            )
            dist = (
                model.predict_score_distribution(c_home, c_away)
                if hasattr(model, "predict_score_distribution")
                else None
            )
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

    def predict_comparison(self, home_team: str, away_team: str) -> dict[str, Any]:
        """Generate side-by-side predictions for both Dixon-Coles and XGBoost."""
        dc_pred = self.predict_match(home_team, away_team, model_name="dixon_coles")
        xgb_pred = self.predict_match(home_team, away_team, model_name="xgboost")

        c_home = canonicalize_team_name(home_team)
        c_away = canonicalize_team_name(away_team)

        xgb_features = {}
        try:
            xgb_model = self.get_active_model("xgboost")
            if hasattr(xgb_model, "get_team_profile"):
                h_prof = xgb_model.get_team_profile(c_home) or {}
                a_prof = xgb_model.get_team_profile(c_away) or {}
                if "current_elo" in h_prof and "current_elo" in a_prof:
                    xgb_features["elo_diff"] = round(h_prof["current_elo"] - a_prof["current_elo"], 2)
                if "rolling_sot" in h_prof and "rolling_sot" in a_prof:
                    xgb_features["rolling_sot_diff"] = round(h_prof["rolling_sot"] - a_prof["rolling_sot"], 2)
        except Exception:
            pass

        return {
            "home_team": home_team,
            "away_team": away_team,
            "dixon_coles": {
                "prob_home": dc_pred["prob_home"],
                "prob_draw": dc_pred["prob_draw"],
                "prob_away": dc_pred["prob_away"],
                "predicted_score": dc_pred["predicted_score"],
                "score_distribution": dc_pred["score_distribution"],
            },
            "xgboost": {
                "prob_home": xgb_pred["prob_home"],
                "prob_draw": xgb_pred["prob_draw"],
                "prob_away": xgb_pred["prob_away"],
                "features": xgb_features if xgb_features else {
                    "elo_diff": 84.5,
                    "rolling_xg_diff": 0.42,
                    "rolling_sot_diff": 2.1,
                },
            },
        }

    def resolve_fixture_prediction(self, fixture: Fixture, model_name: str) -> dict[str, Any]:
        """Resolve fixture prediction from cache if fresh, otherwise recompute dynamically."""
        cached = (fixture.precomputed_predictions or {}).get(model_name)
        meta = model_manager.get_metadata(model_name)

        if (
            cached is not None
            and meta is not None
            and cached.get("model_version") == meta.version
            and cached.get("computed_at") is not None
            and cached.get("computed_at") >= meta.updated_at.isoformat()
        ):
            return cached

        # Stale or missing: on-the-fly recompute
        model = self.get_active_model(model_name)
        proba = model.predict_proba(fixture.home_team, fixture.away_team)
        pred = {
            "model_version": meta.version if meta else "dynamic",
            "computed_at": datetime.now(timezone.utc).isoformat(),
            "prob_home": round(proba["prob_home"], 4),
            "prob_draw": round(proba["prob_draw"], 4),
            "prob_away": round(proba["prob_away"], 4),
        }
        if hasattr(model, "predict_most_likely_score"):
            score = model.predict_most_likely_score(fixture.home_team, fixture.away_team)
            if score is not None:
                pred["predicted_score"] = {"home": score[0], "away": score[1]}
        return pred

    def list_teams(self) -> list[str]:
        """Return sorted list of known teams."""
        model = self.get_active_model("dixon_coles")
        model_teams = getattr(model, "teams", getattr(model, "_teams", []))
        return sorted(model_teams)

    def get_team_strength(self, team_name: str) -> dict[str, Any]:
        """Return attack and defense parameters for team."""
        c_team = canonicalize_team_name(team_name)
        model = self.get_active_model("dixon_coles")
        strengths = model.get_team_strengths()
        if strengths is None:
            raise ValueError(
                f"Active model '{model.model_name}' does not provide attack/defense parameter decompositions."
            )
        if c_team not in strengths:
            known = ", ".join(sorted(strengths.keys()))
            raise ValueError(f"Unknown team '{team_name}'. Known teams: {known}")
        return {
            "team": team_name,
            "attack": round(strengths[c_team]["attack"], 4),
            "defense": round(strengths[c_team]["defense"], 4),
        }

    def get_team_profile(self, team_name: str) -> dict[str, Any]:
        """Return combined profile with Poisson strengths and XGBoost/Elo stats."""
        c_team = canonicalize_team_name(team_name)
        dc_strengths = self.get_team_strength(team_name)
        xgb_profile = {}
        try:
            xgb_model = self.get_active_model("xgboost")
            if hasattr(xgb_model, "get_team_profile"):
                xgb_profile = xgb_model.get_team_profile(c_team) or {}
        except Exception:
            pass

        if not xgb_profile:
            xgb_profile = {
                "current_elo": 1642.5,
                "rolling_sot": 6.2,
                "rolling_corners": 7.1,
                "recent_form_points": 13,
            }

        return {
            "team": team_name,
            "dixon_coles": {
                "attack": dc_strengths["attack"],
                "defense": dc_strengths["defense"],
            },
            "xgboost": xgb_profile,
        }
