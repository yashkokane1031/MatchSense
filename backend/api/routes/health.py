"""Health check endpoint.

Returns model metadata and system status. Useful for monitoring
and for the frontend to check if the API is ready.
"""

from fastapi import APIRouter

from backend.api.dependencies import get_model

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    """Return API health status and model metadata."""
    try:
        model = get_model()
        model_info = model.get_model_info()
        return {
            "status": "healthy",
            "model_loaded": True,
            **model_info,
        }
    except RuntimeError:
        return {
            "status": "degraded",
            "model_loaded": False,
            "message": "Model not loaded. Run the training pipeline first.",
        }
