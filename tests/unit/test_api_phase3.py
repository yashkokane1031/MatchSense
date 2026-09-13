# tests/unit/test_api_phase3.py
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.api.main import app
from backend.core.database import Base, get_db
from backend.models.schemas import Fixture
from backend.services.model_manager import ModelMetadata, model_manager

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(test_engine)
TestSession = sessionmaker(bind=test_engine)


def override_get_db():
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db] = override_get_db


class MockDCModel:
    model_name = "dixon_coles"
    teams = ["Arsenal", "Chelsea"]
    home_advantage = 1.2502

    def predict_proba(self, home, away):
        return {"prob_home": 0.5412, "prob_draw": 0.2315, "prob_away": 0.2273}

    def predict_most_likely_score(self, home, away):
        return (2, 1)

    def predict_score_distribution(self, home, away):
        import numpy as np
        return np.array([[0.0521, 0.0683], [0.0352, 0.0412]])

    def get_team_strengths(self):
        return {"Arsenal": {"attack": 1.3421, "defense": 0.7812}}

    def get_model_info(self):
        return {"model_name": "dixon_coles", "home_advantage": 1.2502}


class MockXGBModel:
    model_name = "xgboost"
    teams = ["Arsenal", "Chelsea"]
    n_features = 70

    def predict_proba(self, home, away):
        return {"prob_home": 0.5284, "prob_draw": 0.2411, "prob_away": 0.2305}

    def predict_most_likely_score(self, home, away):
        return None

    def predict_score_distribution(self, home, away):
        return None

    def get_team_strengths(self):
        return None

    def get_team_profile(self, team):
        return {
            "current_elo": 1642.5,
            "rolling_sot": 6.2,
            "rolling_corners": 7.1,
            "recent_form_points": 13,
        }

    def get_model_info(self):
        return {"model_name": "xgboost", "n_features": 70}


@pytest.fixture(autouse=True)
def setup_models():
    # Set far future last_checked to avoid DB connection timeout in unit test
    model_manager._last_checked = 1e12
    model_manager.set_model(
        "dixon_coles",
        MockDCModel(),
        ModelMetadata(version="v_dc_1", updated_at=datetime(2026, 9, 13, 12, 0, 0, tzinfo=timezone.utc)),
    )
    model_manager.set_model(
        "xgboost",
        MockXGBModel(),
        ModelMetadata(version="v_xgb_1", updated_at=datetime(2026, 9, 13, 12, 0, 0, tzinfo=timezone.utc)),
    )


client = TestClient(app)


def test_head_to_head_default_and_model_param():
    resp_dc = client.post("/api/v1/predictions/head-to-head", json={"home_team": "Arsenal", "away_team": "Chelsea"})
    assert resp_dc.status_code == 200
    data_dc = resp_dc.json()
    assert data_dc["model"] == "dixon_coles"
    assert data_dc["prob_home"] == 0.5412

    resp_xgb = client.post("/api/v1/predictions/head-to-head?model=xgboost", json={"home_team": "Arsenal", "away_team": "Chelsea"})
    assert resp_xgb.status_code == 200
    data_xgb = resp_xgb.json()
    assert data_xgb["model"] == "xgboost"
    assert data_xgb["prob_home"] == 0.5284
    assert data_xgb["predicted_score"] is None


def test_compare_endpoint():
    resp = client.post("/api/v1/predictions/compare", json={"home_team": "Arsenal", "away_team": "Chelsea"})
    assert resp.status_code == 200
    data = resp.json()
    assert "dixon_coles" in data
    assert "xgboost" in data
    assert data["dixon_coles"]["prob_home"] == 0.5412
    assert data["xgboost"]["prob_home"] == 0.5284


def test_fixtures_upcoming_with_per_model_freshness():
    with TestSession() as session:
        f = Fixture(
            id=99901,
            season="2025-26",
            gameweek=29,
            kickoff_time=datetime.now(timezone.utc),
            home_team="Arsenal",
            away_team="Chelsea",
            status="SCHEDULED",
            precomputed_predictions={
                "dixon_coles": {
                    "model_version": "v_dc_1",
                    "computed_at": "2026-09-13T12:05:00+00:00",
                    "prob_home": 0.5412,
                    "prob_draw": 0.2315,
                    "prob_away": 0.2273,
                },
                "xgboost": {
                    "model_version": "v_old",  # Stale version! Should trigger on-the-fly recompute
                    "computed_at": "2020-01-01T00:00:00+00:00",
                    "prob_home": 0.1,
                    "prob_draw": 0.1,
                    "prob_away": 0.8,
                },
            },
        )
        session.add(f)
        session.commit()

    resp = client.get("/api/v1/fixtures/upcoming")
    assert resp.status_code == 200
    fixtures = resp.json()
    match = [m for m in fixtures if m["id"] == 99901][0]
    # Dixon-Coles was fresh -> served from cache
    assert match["predictions"]["dixon_coles"]["prob_home"] == 0.5412
    # XGBoost was stale -> dynamically recomputed from active MockXGBModel
    assert match["predictions"]["xgboost"]["prob_home"] == 0.5284


def test_team_profile_endpoint():
    resp = client.get("/api/v1/teams/Arsenal/profile")
    assert resp.status_code == 200
    data = resp.json()
    assert data["team"] == "Arsenal"
    assert data["dixon_coles"]["attack"] == 1.3421
    assert data["xgboost"]["current_elo"] == 1642.5


def test_health_endpoint():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "models" in data
    assert "dixon_coles" in data["models"]
    assert "xgboost" in data["models"]
