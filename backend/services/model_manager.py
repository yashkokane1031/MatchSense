"""ModelManager for zero-downtime hot-reloading of ML models from PostgreSQL."""

from dataclasses import dataclass
from datetime import datetime, timezone
import logging
from pathlib import Path
import pickle
import time
from typing import Any
import zlib

from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.models.schemas import ModelArtifact
from ml.models.base import BasePredictor

logger = logging.getLogger(__name__)


@dataclass
class ModelMetadata:
    """Metadata tracking loaded model version, active timestamps, and manifests."""
    version: str
    updated_at: datetime
    manifest: dict[str, Any] | None = None


class ModelManager:
    """Manages hot-reloading in-memory models backed by PostgreSQL artifacts."""

    def __init__(self, polling_interval_seconds: float = 30.0):
        self.polling_interval = polling_interval_seconds
        self._last_checked = 0.0
        self._models: dict[str, BasePredictor] = {}
        self._metadata: dict[str, ModelMetadata] = {}

    def set_model(self, name: str, model: BasePredictor, meta: ModelMetadata) -> None:
        """Register or atomically swap an in-memory model reference."""
        self._models[name] = model
        self._metadata[name] = meta

    def get_model(self, name: str = "dixon_coles") -> BasePredictor:
        """Retrieve active in-memory model, checking polling TTL first."""
        self.check_and_reload()
        if name not in self._models:
            raise RuntimeError(f"Model '{name}' not loaded in ModelManager.")
        return self._models[name]

    def get_metadata(self, name: str = "dixon_coles") -> ModelMetadata | None:
        """Retrieve active model metadata, checking polling TTL first."""
        self.check_and_reload()
        return self._metadata.get(name)

    def is_healthy(self) -> dict[str, Any]:
        """Return loaded status and versions for health checks."""
        result = {}
        for name in ["dixon_coles", "xgboost"]:
            if name in self._models:
                meta = self._metadata[name]
                info = getattr(self._models[name], "get_model_info", lambda: {})()
                result[name] = {
                    "loaded": True,
                    "version": meta.version,
                    "loaded_at": meta.updated_at.isoformat(),
                    **info,
                }
            else:
                result[name] = {
                    "loaded": False,
                    "version": None,
                    "loaded_at": None,
                }
        return result

    def check_and_reload(self) -> None:
        """Poll DB if TTL expired, fetching newer artifact bytes and deserializing."""
        now = time.time()
        if now - self._last_checked < self.polling_interval:
            return
        self._last_checked = now

        try:
            with SessionLocal() as session:
                active_rows = session.query(ModelArtifact).filter_by(is_active=True).all()
                for row in active_rows:
                    current_meta = self._metadata.get(row.model_name)
                    row_updated_at = row.updated_at
                    if row_updated_at.tzinfo is None:
                        row_updated_at = row_updated_at.replace(tzinfo=timezone.utc)

                    if current_meta is None or row_updated_at > current_meta.updated_at:
                        logger.info(
                            "Hot-reloading model '%s' from version %s to %s",
                            row.model_name,
                            current_meta.version if current_meta else "None",
                            row.version,
                        )
                        decompressed = zlib.decompress(row.artifact_bytes)
                        model_instance = pickle.loads(decompressed)
                        self.set_model(
                            row.model_name,
                            model_instance,
                            ModelMetadata(
                                version=row.version,
                                updated_at=row_updated_at,
                                manifest=row.manifest,
                            ),
                        )
        except Exception as e:
            logger.warning(
                "Failed to poll models table for hot-reload: %s. Continuing with cached instances.",
                e,
            )

    def initialize_from_files_or_db(self) -> None:
        """Startup hook: attempt DB reload, falling back to local files."""
        self.check_and_reload()

        if "dixon_coles" not in self._models:
            dc_path = Path(settings.model_path)
            if dc_path.exists():
                logger.info("Loading Dixon-Coles from local fallback file: %s", dc_path)
                try:
                    with open(dc_path, "rb") as f:
                        model = pickle.load(f)
                    self.set_model(
                        "dixon_coles",
                        model,
                        ModelMetadata(
                            version="local_file",
                            updated_at=datetime.now(timezone.utc),
                        ),
                    )
                except Exception as e:
                    logger.warning("Could not load local Dixon-Coles file: %s", e)

        if "xgboost" not in self._models:
            xgb_path = Path(getattr(settings, "xgb_model_path", "data/models/xgboost_latest.pkl"))
            if xgb_path.exists():
                logger.info("Loading XGBoost from local fallback file: %s", xgb_path)
                try:
                    with open(xgb_path, "rb") as f:
                        model = pickle.load(f)
                    self.set_model(
                        "xgboost",
                        model,
                        ModelMetadata(
                            version="local_file",
                            updated_at=datetime.now(timezone.utc),
                        ),
                    )
                except Exception as e:
                    logger.warning("Could not load local XGBoost file: %s", e)


model_manager = ModelManager(polling_interval_seconds=30.0)
