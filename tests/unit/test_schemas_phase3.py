# tests/unit/test_schemas_phase3.py
from datetime import datetime, timezone
import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.core.database import Base
from backend.models.schemas import Fixture, ModelArtifact


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionClass = sessionmaker(bind=engine)
    session = SessionClass()
    yield session
    session.close()


def test_model_artifact_orm(db_session: Session):
    model = ModelArtifact(
        model_name="dixon_coles",
        version="v202526_gw28_20260913_1400",
        artifact_bytes=b"dummy_bytes",
        manifest={"metrics": {"rps": 0.2007}},
        is_active=True,
    )
    db_session.add(model)
    db_session.commit()

    saved = db_session.query(ModelArtifact).filter_by(model_name="dixon_coles").first()
    assert saved is not None
    assert saved.version == "v202526_gw28_20260913_1400"
    assert saved.is_active is True
    assert saved.manifest["metrics"]["rps"] == 0.2007


def test_fixture_orm_default_jsonb(db_session: Session):
    fixture = Fixture(
        id=432101,
        season="2025-26",
        gameweek=29,
        kickoff_time=datetime.now(timezone.utc),
        home_team="Arsenal",
        away_team="Chelsea",
        status="SCHEDULED",
    )
    db_session.add(fixture)
    db_session.commit()

    saved = db_session.query(Fixture).filter_by(id=432101).first()
    assert saved is not None
    assert saved.home_team == "Arsenal"
    assert saved.status == "SCHEDULED"
    assert saved.precomputed_predictions == {} or saved.precomputed_predictions is None
