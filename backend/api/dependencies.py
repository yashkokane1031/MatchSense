"""Dependency injection for FastAPI routes.

Provides model references and access to ModelManager.
"""

from ml.models.base import BasePredictor


def get_model(name: str = "dixon_coles") -> BasePredictor:
    """Get the loaded model instance from ModelManager."""
    from backend.services.model_manager import model_manager

    return model_manager.get_model(name)


def set_model(model: BasePredictor | None, name: str = "dixon_coles") -> None:
    """Set model reference in ModelManager. Used by tests and lifespan."""
    from datetime import datetime, timezone
    from backend.services.model_manager import model_manager, ModelMetadata

    if model is not None:
        model_manager.set_model(
            name,
            model,
            ModelMetadata(version="manual_set", updated_at=datetime.now(timezone.utc)),
        )
