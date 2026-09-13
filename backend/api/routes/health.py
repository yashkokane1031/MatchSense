"""Health check endpoint.

Returns model metadata, database connectivity, and system status.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from backend.api.dependencies import get_model
from backend.core.database import SessionLocal
from backend.services.model_manager import model_manager

router = APIRouter()


class ModelStatus(BaseModel):
    loaded: bool
    version: str | None = None
    updated_at: str | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    database_connected: bool
    models: dict[str, ModelStatus]
    message: str | None = None

    model_config = {"extra": "allow"}


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return API health status, database connection, and model metadata."""
    db_connected = False
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
            db_connected = True
    except Exception:
        db_connected = False

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
            models=models_dict,
            **model_info,
        )
    except RuntimeError:
        return HealthResponse(
            status="degraded",
            model_loaded=False,
            database_connected=db_connected,
            models=models_dict,
            message="Model not loaded. Run the training pipeline first.",
        )

