"""Integration tests for the weekly synchronization pipeline engine."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import zlib
import numpy as np
import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base
from backend.models.schemas import Fixture, Match, ModelArtifact
from scripts.sync_pipeline import (
    run_phase_a_ingestion,
    run_phase_b1_dixon_coles,
    run_phase_b2_xgboost,
    score_gate_2b_audit,
)
from ml.data.season import derive_current_season as derive_current_season_import


@pytest.fixture
def test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield engine, session
    session.close()


def test_phase_a_ingestion(test_db):
    engine, session = test_db

    sample_csv = (
        "Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HTHG,HTAG,HS,AS,HST,AST,AvgH,AvgD,AvgA\n"
        "17/08/2024,Arsenal,Chelsea,2,1,H,1,0,12,8,5,3,1.80,3.60,4.20\n"
        "18/08/2024,Liverpool,Everton,3,0,H,2,0,15,4,7,1,1.45,4.50,7.00\n"
    )
    mock_fixtures = [
        {
            "id": 9901,
            "season": "2024-25",
            "gameweek": 2,
            "kickoff_time": "2024-08-24T14:00:00Z",
            "home_team": "Chelsea",
            "away_team": "Liverpool",
            "status": "SCHEDULED",
        }
    ]

    with patch("scripts.sync_pipeline.download_season_csv", return_value=sample_csv), \
         patch("scripts.sync_pipeline.FootballDataClient") as MockClient:
        instance = MockClient.return_value
        instance.get_scheduled_fixtures.return_value = mock_fixtures

        new_matches = run_phase_a_ingestion(session, api_key="test_key", season_code="2425", season_label="2024-25")

        assert len(new_matches) == 2
        matches_in_db = session.query(Match).all()
        assert len(matches_in_db) == 2

        fixtures_in_db = session.query(Fixture).all()
        assert len(fixtures_in_db) == 1
        assert fixtures_in_db[0].id == 9901
        assert fixtures_in_db[0].home_team == "Chelsea"


def test_decoupled_transactions_and_jsonb_partial_merge(test_db):
    engine, session = test_db

    # Seed an upcoming fixture
    fix = Fixture(
        id=7701,
        season="2025-26",
        gameweek=30,
        kickoff_time=datetime.now(timezone.utc),
        home_team="Arsenal",
        away_team="Chelsea",
        status="SCHEDULED",
        precomputed_predictions={},
    )
    session.add(fix)
    session.commit()

    # Simulate Phase B1 writing Dixon-Coles
    dc_payload = {
        "model_version": "v_dc_test",
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "prob_home": 0.55,
        "prob_draw": 0.25,
        "prob_away": 0.20,
    }
    success_b1 = run_phase_b1_dixon_coles(session, fixture_predictions={7701: dc_payload}, dry_run_only=True)
    assert success_b1 is True
    session.commit()

    # Verify Dixon-Coles written
    fix_after_b1 = session.query(Fixture).filter_by(id=7701).one()
    assert "dixon_coles" in fix_after_b1.precomputed_predictions
    assert fix_after_b1.precomputed_predictions["dixon_coles"]["prob_home"] == 0.55

    # Simulate Phase B2 writing XGBoost
    xgb_payload = {
        "model_version": "v_xgb_test",
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "prob_home": 0.53,
        "prob_draw": 0.27,
        "prob_away": 0.20,
    }
    success_b2 = run_phase_b2_xgboost(session, fixture_predictions={7701: xgb_payload}, dry_run_only=True)
    assert success_b2 is True
    session.commit()

    # Verify BOTH keys exist! Phase B2 did not overwrite Phase B1
    fix_after_b2 = session.query(Fixture).filter_by(id=7701).one()
    assert "dixon_coles" in fix_after_b2.precomputed_predictions
    assert "xgboost" in fix_after_b2.precomputed_predictions
    assert fix_after_b2.precomputed_predictions["dixon_coles"]["prob_home"] == 0.55
    assert fix_after_b2.precomputed_predictions["xgboost"]["prob_home"] == 0.53


def test_gate_2b_multi_gameweek_audit():
    completed_matches = [
        {"gameweek": 27, "home_team": "Arsenal", "away_team": "Chelsea", "result": "H"},
        {"gameweek": 28, "home_team": "Liverpool", "away_team": "Everton", "result": "D"},
    ]
    pre_match_preds = {
        ("Arsenal", "Chelsea"): {
            "dixon_coles": {"prob_home": 0.6, "prob_draw": 0.2, "prob_away": 0.2},
            "xgboost": {"prob_home": 0.5, "prob_draw": 0.3, "prob_away": 0.2},
        },
        ("Liverpool", "Everton"): {
            "dixon_coles": {"prob_home": 0.7, "prob_draw": 0.2, "prob_away": 0.1},
            "xgboost": {"prob_home": 0.6, "prob_draw": 0.2, "prob_away": 0.2},
        },
    }
    audit_results = score_gate_2b_audit(completed_matches, pre_match_preds)
    assert len(audit_results) == 2
    assert audit_results[0]["gameweek"] == 27
    assert audit_results[1]["gameweek"] == 28
    assert "dixon_coles_rps" in audit_results[0]
    assert "xgboost_rps" in audit_results[0]
    assert audit_results[0]["dixon_coles_acc"] == 1.0  # Arsenal won, DC predicted H


class MockRecoveryModel:
    call_count = 0

    def __init__(self, xi=0.005):
        self.xi = xi

    def fit(self, df, warm_start_params=None):
        MockRecoveryModel.call_count += 1
        if MockRecoveryModel.call_count == 1:
            # Attempt 1: fail convergence / bounds
            self._converged = False
            self._convergence_message = "Maximum function evaluations exceeded"
            self._home_advantage = 1.25
            self._rho = -0.13
            self._attack = {"Arsenal": 1.2, "Chelsea": 0.9}
            self._defense = {"Arsenal": 0.8, "Chelsea": 1.1}
        else:
            # Attempt 2: succeed
            self._converged = True
            self._convergence_message = "converged"
            self._home_advantage = 1.25
            self._rho = -0.13
            self._attack = {"Arsenal": 1.2, "Chelsea": 0.9}
            self._defense = {"Arsenal": 0.8, "Chelsea": 1.1}

    def get_model_info(self):
        return {"model_name": "dixon_coles", "home_advantage": self._home_advantage}

    def predict_proba(self, home, away):
        return {"prob_home": 0.5, "prob_draw": 0.25, "prob_away": 0.25}

    def predict_most_likely_score(self, home, away):
        return (2, 1)

    def predict_score_distribution(self, home, away):
        return np.zeros((3, 3))


def test_phase_b1_two_tier_recovery(test_db):
    engine, session = test_db
    MockRecoveryModel.call_count = 0

    # Create dummy matches DataFrame
    matches_df = pd.DataFrame([
        {"Date": "2024-08-17", "HomeTeam": "Arsenal", "AwayTeam": "Chelsea", "FTHG": 2, "FTAG": 1, "FTR": "H", "Season": "2024-25"},
        {"Date": "2024-08-24", "HomeTeam": "Chelsea", "AwayTeam": "Arsenal", "FTHG": 0, "FTAG": 1, "FTR": "A", "Season": "2024-25"},
    ])
    matches_df["Date"] = pd.to_datetime(matches_df["Date"])

    # Seed an active model artifact
    prior_artifact = ModelArtifact(
        model_name="dixon_coles",
        version="dc_old",
        is_active=True,
        manifest={"model_name": "dixon_coles"},
        artifact_bytes=zlib.compress(b"dummy_prior"),
    )
    session.add(prior_artifact)
    session.commit()

    with patch("scripts.sync_pipeline.DixonColesModel", MockRecoveryModel), \
         patch("pickle.loads", side_effect=Exception("Unpickle fallback")):
        ok = run_phase_b1_dixon_coles(session, matches_df=matches_df)
        assert ok is True
        assert MockRecoveryModel.call_count == 2  # Both Attempt 1 and Attempt 2 executed!

        # Verify new model activated and old model deactivated
        active = session.query(ModelArtifact).filter_by(model_name="dixon_coles", is_active=True).all()
        assert len(active) == 1
        assert active[0].version != "dc_old"

        old = session.query(ModelArtifact).filter_by(model_name="dixon_coles", version="dc_old").one()
        assert old.is_active is False


def test_phase_a_dynamic_season_from_api(test_db):
    """When season_code/label are None, Phase A derives them from the API response."""
    engine, session = test_db

    sample_csv = (
        "Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HTHG,HTAG,HS,AS,HST,AST,AvgH,AvgD,AvgA\n"
        "17/08/2026,Arsenal,Chelsea,2,1,H,1,0,12,8,5,3,1.80,3.60,4.20\n"
    )
    # API returns fixtures tagged as 2026-27 season
    mock_fixtures = [
        {
            "id": 5001,
            "season": "2026-27",
            "gameweek": 1,
            "kickoff_time": "2026-08-17T14:00:00Z",
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "status": "SCHEDULED",
        }
    ]

    with patch("scripts.sync_pipeline.download_season_csv", return_value=sample_csv), \
         patch("scripts.sync_pipeline.FootballDataClient") as MockClient:
        instance = MockClient.return_value
        instance.get_scheduled_fixtures.return_value = mock_fixtures

        # season_code=None, season_label=None → should derive from API
        new_matches = run_phase_a_ingestion(session, api_key="test_key")

        assert len(new_matches) == 1
        # The derived season should be "2026-27" from the API, not a hardcoded value
        assert new_matches[0]["season"] == "2026-27"

        fixtures_in_db = session.query(Fixture).all()
        assert len(fixtures_in_db) == 1
        assert fixtures_in_db[0].season == "2026-27"


def test_phase_a_api_down_falls_back_to_date(test_db):
    """When the API is unreachable, Phase A falls back to date-based season derivation."""
    engine, session = test_db

    sample_csv = (
        "Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HTHG,HTAG,HS,AS,HST,AST,AvgH,AvgD,AvgA\n"
        "17/08/2026,Arsenal,Chelsea,2,1,H,1,0,12,8,5,3,1.80,3.60,4.20\n"
    )

    with patch("scripts.sync_pipeline.download_season_csv", return_value=sample_csv), \
         patch("scripts.sync_pipeline.FootballDataClient") as MockClient, \
         patch("scripts.sync_pipeline.derive_current_season", wraps=derive_current_season_import) as spy:
        instance = MockClient.return_value
        instance.get_scheduled_fixtures.side_effect = ConnectionError("API offline")

        # Should not crash — falls back to date-math
        new_matches = run_phase_a_ingestion(session, api_key="test_key")

        # derive_current_season was called with api_season=None (API failed)
        spy.assert_called_once()
        call_kwargs = spy.call_args
        assert call_kwargs[1].get("api_season") is None or call_kwargs[0][0] is None


