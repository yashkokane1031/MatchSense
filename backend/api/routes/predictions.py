"""Prediction endpoints for MatchSense API.

Provides head-to-head match predictions and team information.
Gameweek predictions will be added in Phase 3 when live data is integrated.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.prediction import PredictionService

router = APIRouter()
_service = PredictionService()


class HeadToHeadRequest(BaseModel):
    """Request body for a head-to-head prediction."""
    home_team: str
    away_team: str


class ScorePrediction(BaseModel):
    """Predicted most likely score."""
    home: int
    away: int


class MatchPrediction(BaseModel):
    """Full prediction for a match."""
    home_team: str
    away_team: str
    prob_home: float
    prob_draw: float
    prob_away: float
    predicted_score: ScorePrediction | None = None
    score_distribution: list[list[float]] | None = None
    model: str


class TeamStrength(BaseModel):
    """Attack and defense strengths for a team."""
    team: str
    attack: float
    defense: float


@router.post("/predictions/head-to-head", response_model=MatchPrediction)
def predict_head_to_head(request: HeadToHeadRequest) -> MatchPrediction:
    """Predict the outcome of a match between two teams.

    Returns outcome probabilities (W/D/L), the most likely score,
    and the full score distribution matrix.
    """
    try:
        pred = _service.predict_match(request.home_team, request.away_team)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return MatchPrediction(**pred)


@router.get("/teams", response_model=list[str])
def list_teams() -> list[str]:
    """Return all teams the model knows about."""
    try:
        return _service.list_teams()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/teams/{team_name}/strengths", response_model=TeamStrength)
def get_team_strength(team_name: str) -> TeamStrength:
    """Return a team's attack and defense strength parameters."""
    try:
        strength = _service.get_team_strength(team_name)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return TeamStrength(**strength)
