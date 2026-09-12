"""Tests for the FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from backend.api.dependencies import set_model
from backend.api.main import app


@pytest.fixture
def client(fitted_model):
    """Test client with a pre-loaded model."""
    set_model(fitted_model)
    with TestClient(app) as c:
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
