"""Dependency injection for FastAPI routes.

Provides model references and access to ModelManager.
"""

from ml.models.base import BasePredictor


def get_model(name: str | None = None) -> BasePredictor:
    """Get the loaded model instance from ModelManager."""
    from backend.services.model_manager import model_manager

    if name:
        m = model_manager.get_model(name)
        if m is not None:
            return m

    # Default to dixon_coles if available
    m = model_manager.get_model("dixon_coles")
    if m is not None:
        return m

    # Fallback to any loaded model
    for loaded_model in model_manager._models.values():
        if loaded_model is not None:
            return loaded_model

    raise RuntimeError("Model not loaded. Check MODEL_PATH configuration.")


def set_model(model: BasePredictor | None, name: str | None = None) -> None:
    """Set model reference in ModelManager. Used by tests and lifespan."""
    from datetime import datetime, timezone
    from backend.services.model_manager import model_manager, ModelMetadata

    if model is None:
        if name is not None:
            model_manager._models.pop(name, None)
            model_manager._metadata.pop(name, None)
        else:
            model_manager._models.clear()
            model_manager._metadata.clear()
        return

    model_name = name or getattr(model, "name", "dixon_coles")
    model_manager.set_model(
        model_name,
        model,
        ModelMetadata(version="manual_set", updated_at=datetime.now(timezone.utc)),
    )
