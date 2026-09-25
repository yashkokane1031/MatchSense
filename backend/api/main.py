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
    """Initialize model manager at startup and log status."""
    from backend.services.model_manager import model_manager

    logger.info("Initializing ModelManager from database and local fallbacks...")
    model_manager.initialize_from_files_or_db()
    health_info = model_manager.is_healthy()
    logger.info("ModelManager initialized: %s", health_info)

    yield

    logger.info("App shutting down")


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

    # CORS — allow all origins for production and development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(health.router, prefix=settings.api_v1_prefix, tags=["Health"])
    app.include_router(predictions.router, prefix=settings.api_v1_prefix, tags=["Predictions"])

    return app


# Application instance for uvicorn
app = create_app()
