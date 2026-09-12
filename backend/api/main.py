"""FastAPI application factory for MatchSense.

Loads the fitted Dixon-Coles model at startup via lifespan,
registers routes, and configures CORS for development.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.dependencies import set_model
from backend.api.routes import health, predictions
from backend.core.config import settings
from ml.models.dixon_coles import DixonColesModel

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Load the model at startup, clean up on shutdown."""
    model_path = Path(settings.model_path)
    if model_path.exists():
        logger.info("Loading model from %s", model_path)
        model = DixonColesModel.load(model_path)
        set_model(model)
        logger.info("Model loaded successfully: %s", model.get_model_info())
    else:
        logger.warning(
            "Model file not found at %s. Prediction endpoints will return errors. "
            "Run the training pipeline first: uv run python scripts/seed_data.py",
            model_path,
        )

    yield

    # Cleanup
    set_model(None)
    logger.info("Model unloaded")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="MatchSense API",
        description=(
            "Premier League match predictor using the Dixon-Coles model. "
            "Provides match outcome probabilities and score distributions."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS — allow all origins for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(health.router, prefix=settings.api_v1_prefix, tags=["Health"])
    app.include_router(predictions.router, prefix=settings.api_v1_prefix, tags=["Predictions"])

    return app


# Application instance for uvicorn
app = create_app()
