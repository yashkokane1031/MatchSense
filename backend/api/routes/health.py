"""Health check endpoint.

Returns model metadata, database connectivity, and system status.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from backend.api.dependencies import get_model
from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.models.schemas import Fixture
from backend.services.model_manager import model_manager

router = APIRouter()


class ModelStatus(BaseModel):
    loaded: bool
    version: str | None = None
    updated_at: str | None = None
    error: str | None = None


class FixtureFeedStatus(BaseModel):
    configured: bool
    upcoming_count: int = 0
    status: str  # "healthy", "empty", "missing_key"
    error: str | None = None


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    database_connected: bool
    fixtures_count: int = 0
    fixture_feed: FixtureFeedStatus | None = None
    models: dict[str, ModelStatus]
    message: str | None = None

    model_config = {"extra": "allow"}


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return API health status, database connection, fixture feed health, and model metadata."""
    db_connected = False
    fixtures_count = 0
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
            db_connected = True
            fixtures_count = session.query(Fixture).filter(
                Fixture.status.in_(["SCHEDULED", "TIMED"])
            ).count()
    except Exception:
        db_connected = False

    has_api_key = bool(settings.football_data_api_key and settings.football_data_api_key.strip())
    if not has_api_key:
        feed_status = "missing_key"
        feed_error = "FOOTBALL_DATA_API_KEY is not configured in environment"
    elif fixtures_count == 0:
        feed_status = "empty"
        feed_error = "No upcoming fixtures found in database; check external API ingestion"
    else:
        feed_status = "healthy"
        feed_error = None

    fixture_feed = FixtureFeedStatus(
        configured=has_api_key,
        upcoming_count=fixtures_count,
        status=feed_status,
        error=feed_error,
    )

    models_info = model_manager.is_healthy()
    models_dict = {
        name: ModelStatus(
            loaded=info.get("loaded", False),
            version=info.get("version"),
            updated_at=info.get("updated_at"),
            error=info.get("error"),
        )
        for name, info in models_info.items()
    }

    try:
        model = get_model()
        model_info = model.get_model_info() if hasattr(model, "get_model_info") else {}
        return HealthResponse(
            status="healthy",
            model_loaded=True,
            database_connected=db_connected,
            fixtures_count=fixtures_count,
            fixture_feed=fixture_feed,
            models=models_dict,
            **model_info,
        )
    except RuntimeError:
        return HealthResponse(
            status="degraded",
            model_loaded=False,
            database_connected=db_connected,
            fixtures_count=fixtures_count,
            fixture_feed=fixture_feed,
            models=models_dict,
            message="Model not loaded. Run the training pipeline first.",
        )


