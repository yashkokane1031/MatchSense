"""Dependency injection for FastAPI routes.

Holds the global model reference and provides accessor functions.
Separated from main.py to avoid circular imports between routes and app.
"""

from ml.models.dixon_coles import DixonColesModel

# Global model reference, set during app startup
_model: DixonColesModel | None = None


def get_model() -> DixonColesModel:
    """Get the loaded model instance. Raises if model not loaded."""
    if _model is None:
        raise RuntimeError("Model not loaded. Check MODEL_PATH configuration.")
    return _model


def set_model(model: DixonColesModel | None) -> None:
    """Set the global model reference. Used by lifespan and tests."""
    global _model
    _model = model
