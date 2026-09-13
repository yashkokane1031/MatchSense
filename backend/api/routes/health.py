"""Health check endpoint.

Returns model metadata, database connectivity, and system status.
"""

from fastapi import APIRouter
from sqlalchemy import text

from backend.api.dependencies import get_model
from backend.core.database import SessionLocal
from backend.services.model_manager import model_manager

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    """Return API health status, database connection, and model metadata."""
    db_connected = False
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
            db_connected = True
    except Exception:
        db_connected = False

    models_info = model_manager.is_healthy()

    try:
        model = get_model()
        model_info = model.get_model_info() if hasattr(model, "get_model_info") else {}
        return {
            "status": "healthy",
            "model_loaded": True,
            "database_connected": db_connected,
            "models": models_info,
            **model_info,
        }
    except RuntimeError:
        return {
            "status": "degraded",
            "model_loaded": False,
            "database_connected": db_connected,
            "models": models_info,
            "message": "Model not loaded. Run the training pipeline first.",
        }
