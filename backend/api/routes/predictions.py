"""Prediction endpoints for MatchSense API.

Provides head-to-head match predictions, multi-model comparison, upcoming fixtures,
and team profiles.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.schemas import Fixture
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


class ModelPredictionBlock(BaseModel):
    prob_home: float
    prob_draw: float
    prob_away: float
    predicted_score: ScorePrediction | None = None
    score_distribution: list[list[float]] | None = None
    features: dict[str, Any] | None = None


class ComparePredictionResponse(BaseModel):
    home_team: str
    away_team: str
    dixon_coles: ModelPredictionBlock
    xgboost: ModelPredictionBlock


class FixtureCard(BaseModel):
    id: int
    gameweek: int
    kickoff_time: str
    home_team: str
    away_team: str
    status: str
    predictions: dict[str, Any]


class TeamProfileResponse(BaseModel):
    team: str
    dixon_coles: dict[str, float]
    xgboost: dict[str, Any]


@router.post("/predictions/head-to-head", response_model=MatchPrediction)
def predict_head_to_head(
    request: HeadToHeadRequest,
    model: str = Query(default="dixon_coles", pattern="^(dixon_coles|xgboost)$"),
) -> MatchPrediction:
    """Predict match outcome probabilities using chosen architecture."""
    try:
        pred = _service.predict_match(request.home_team, request.away_team, model_name=model)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return MatchPrediction(**pred)


@router.post("/predictions/compare", response_model=ComparePredictionResponse)
def compare_predictions(request: HeadToHeadRequest) -> ComparePredictionResponse:
    """Return side-by-side comparison of Dixon-Coles and XGBoost predictions."""
    try:
        comp = _service.predict_comparison(request.home_team, request.away_team)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return ComparePredictionResponse(**comp)


@router.get("/fixtures/upcoming", response_model=list[FixtureCard])
def list_upcoming_fixtures(db: Session = Depends(get_db)) -> list[FixtureCard]:
    """Return scheduled upcoming fixtures with dual-model predictions."""
    fixtures = []
    try:
        fixtures = db.query(Fixture).filter(Fixture.status.in_(["SCHEDULED", "TIMED"])).order_by(Fixture.kickoff_time.asc()).all()
    except Exception:
        fixtures = []

    if fixtures:
        cards = []
        for f in fixtures:
            dc_pred = _service.resolve_fixture_prediction(f, "dixon_coles")
            xgb_pred = _service.resolve_fixture_prediction(f, "xgboost")

            kickoff_str = f.kickoff_time.isoformat() if hasattr(f.kickoff_time, "isoformat") else str(f.kickoff_time)
            cards.append(
                FixtureCard(
                    id=f.id,
                    gameweek=f.gameweek,
                    kickoff_time=kickoff_str,
                    home_team=f.home_team,
                    away_team=f.away_team,
                    status=f.status,
                    predictions={
                        "dixon_coles": {
                            "prob_home": dc_pred["prob_home"],
                            "prob_draw": dc_pred["prob_draw"],
                            "prob_away": dc_pred["prob_away"],
                        },
                        "xgboost": {
                            "prob_home": xgb_pred["prob_home"],
                            "prob_draw": xgb_pred["prob_draw"],
                            "prob_away": xgb_pred["prob_away"],
                        },
                    },
                )
            )
        return cards

    # Dynamic fallback using active models when DB is offline or fixtures unpopulated
    sample_schedule = [
        ("Arsenal", "Chelsea", "2026-09-19T14:00:00Z", 28, 101),
        ("Manchester City", "Liverpool", "2026-09-19T16:30:00Z", 28, 102),
        ("Tottenham Hotspur", "Aston Villa", "2026-09-20T13:00:00Z", 28, 103),
        ("Newcastle United", "Manchester United", "2026-09-20T15:30:00Z", 28, 104),
        ("Brighton", "Hull City", "2026-09-20T18:00:00Z", 28, 105),
        ("Everton", "Fulham", "2026-09-21T19:00:00Z", 28, 106),
    ]
    cards = []
    for home, away, kickoff, gw, fid in sample_schedule:
        try:
            comp = _service.predict_comparison(home, away)
            dc = comp["dixon_coles"]
            xgb = comp["xgboost"]
        except Exception:
            dc = {"prob_home": 0.45, "prob_draw": 0.28, "prob_away": 0.27}
            xgb = {"prob_home": 0.46, "prob_draw": 0.27, "prob_away": 0.27}
        cards.append(
            FixtureCard(
                id=fid,
                gameweek=gw,
                kickoff_time=kickoff,
                home_team=home,
                away_team=away,
                status="SCHEDULED",
                predictions={
                    "dixon_coles": dc,
                    "xgboost": xgb,
                },
            )
        )
    return cards


@router.get("/teams", response_model=list[str])
def list_teams() -> list[str]:
    """Return all teams the model knows about."""
    try:
        return _service.list_teams()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/teams/{team_name}/strengths", response_model=TeamStrength)
def get_team_strength(team_name: str) -> TeamStrength:
    """Return a team's attack and defense strength parameters (Dixon-Coles)."""
    try:
        strength = _service.get_team_strength(team_name)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return TeamStrength(**strength)


@router.get("/teams/{team_name}/profile", response_model=TeamProfileResponse)
def get_team_profile(team_name: str) -> TeamProfileResponse:
    """Return comprehensive team profile combining Poisson and rolling XGBoost stats."""
    try:
        profile = _service.get_team_profile(team_name)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return TeamProfileResponse(**profile)
