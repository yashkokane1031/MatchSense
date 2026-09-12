"""Tests for the FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from backend.api.dependencies import set_model
from backend.api.main import app


@pytest.fixture
def client(fitted_model):
    """Test client with a pre-loaded model."""
    with TestClient(app) as c:
        set_model(fitted_model)
        yield c
    set_model(None)


@pytest.fixture
def client_no_model():
    """Test client with no model loaded."""
    with TestClient(app) as c:
        set_model(None)
        yield c
        set_model(None)


class TestHealthEndpoint:
    def test_health_with_model(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] is True
        assert data["model_name"] == "dixon_coles"

    def test_health_without_model(self, client_no_model):
        response = client_no_model.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["model_loaded"] is False


class TestPredictionEndpoints:
    def test_head_to_head_valid(self, client):
        response = client.post(
            "/api/v1/predictions/head-to-head",
            json={"home_team": "Arsenal", "away_team": "Liverpool"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["home_team"] == "Arsenal"
        assert data["away_team"] == "Liverpool"
        assert 0 <= data["prob_home"] <= 1
        assert 0 <= data["prob_draw"] <= 1
        assert 0 <= data["prob_away"] <= 1
        total = data["prob_home"] + data["prob_draw"] + data["prob_away"]
        assert abs(total - 1.0) < 0.02
        assert data["model"] == "dixon_coles"
        assert isinstance(data["score_distribution"], list)

    def test_head_to_head_unknown_team(self, client):
        response = client.post(
            "/api/v1/predictions/head-to-head",
            json={"home_team": "Arsenal", "away_team": "Nonexistent FC"},
        )
        assert response.status_code == 404
        assert "Unknown team" in response.json()["detail"]

    def test_head_to_head_promoted_team(self, client):
        """Newly promoted team in KNOWN_PL_TEAMS should succeed with promoted prior."""
        response = client.post(
            "/api/v1/predictions/head-to-head",
            json={"home_team": "Arsenal", "away_team": "Ipswich"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["home_team"] == "Arsenal"
        assert data["away_team"] == "Ipswich"
        assert 0 <= data["prob_home"] <= 1
        assert data["prob_home"] > data["prob_away"]

    def test_head_to_head_no_model(self, client_no_model):
        response = client_no_model.post(
            "/api/v1/predictions/head-to-head",
            json={"home_team": "Arsenal", "away_team": "Liverpool"},
        )
        assert response.status_code == 503


class TestTeamEndpoints:
    def test_list_teams(self, client):
        response = client.get("/api/v1/teams")
        assert response.status_code == 200
        teams = response.json()
        assert isinstance(teams, list)
        assert len(teams) > 0
        assert teams == sorted(teams)  # Should be alphabetically sorted

    def test_team_strengths(self, client):
        response = client.get("/api/v1/teams/Arsenal/strengths")
        assert response.status_code == 200
        data = response.json()
        assert data["team"] == "Arsenal"
        assert data["attack"] > 0
        assert data["defense"] > 0

    def test_team_strengths_unknown(self, client):
        response = client.get("/api/v1/teams/Nonexistent/strengths")
        assert response.status_code == 404


class TestXGBoostApiEndpoints:
    @pytest.fixture
    def xgb_client(self, sample_matches):
        from ml.models.xgboost_model import XGBoostPredictor
        model = XGBoostPredictor()
        # Add basic stats columns if not present
        matches = sample_matches.copy()
        for col in ["HS", "AS", "HST", "AST", "HC", "AC"]:
            if col not in matches.columns:
                matches[col] = 10
        model.fit(matches)
        with TestClient(app) as c:
            set_model(model)
            yield c
        set_model(None)

    def test_xgboost_health(self, xgb_client):
        response = xgb_client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["model_name"] == "xgboost"
        assert data["n_features"] > 10

    def test_xgboost_head_to_head_nullable_scoreline(self, xgb_client):
        response = xgb_client.post(
            "/api/v1/predictions/head-to-head",
            json={"home_team": "Arsenal", "away_team": "Chelsea"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "xgboost"
        assert 0 <= data["prob_home"] <= 1
        assert data["predicted_score"] is None
        assert data["score_distribution"] is None

    def test_xgboost_strengths_returns_404(self, xgb_client):
        response = xgb_client.get("/api/v1/teams/Arsenal/strengths")
        assert response.status_code == 404
        assert "does not provide attack/defense parameter decompositions" in response.json()["detail"]

    def test_xgboost_distinguishes_promoted_from_fake(self, xgb_client):
        # Known promoted team in KNOWN_PL_TEAMS with 0 matches in window should succeed
        resp_promoted = xgb_client.post(
            "/api/v1/predictions/head-to-head",
            json={"home_team": "Arsenal", "away_team": "Ipswich"},
        )
        assert resp_promoted.status_code == 200
        assert resp_promoted.json()["prob_home"] > 0

        # Unknown / fake team must return 404
        resp_fake = xgb_client.post(
            "/api/v1/predictions/head-to-head",
            json={"home_team": "Arsenal", "away_team": "Atlantis United"},
        )
        assert resp_fake.status_code == 404
        assert "Unknown team" in resp_fake.json()["detail"]
