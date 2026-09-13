# tests/unit/test_model_manager.py
from datetime import datetime, timezone
import pickle
from unittest.mock import MagicMock, patch
import zlib
import pytest

from backend.services.model_manager import ModelManager, ModelMetadata


class DummyModel:
    def __init__(self, name="dixon_coles", version="v1"):
        self.model_name = name
        self.version = version
        self.teams = ["Arsenal", "Chelsea"]

    def predict_proba(self, home, away):
        return {"prob_home": 0.5, "prob_draw": 0.3, "prob_away": 0.2}

    def get_model_info(self):
        return {"model_name": self.model_name, "version": self.version}


def test_model_manager_load_and_swap():
    # Polling interval large so it does not poll DB
    manager = ModelManager(polling_interval_seconds=3600.0)
    manager._last_checked = 1e12  # Far in future to avoid DB poll
    dummy_dc = DummyModel(name="dixon_coles", version="v1")
    manager.set_model("dixon_coles", dummy_dc, ModelMetadata(version="v1", updated_at=datetime.now(timezone.utc)))

    assert manager.get_model("dixon_coles").version == "v1"
    meta = manager.get_metadata("dixon_coles")
    assert meta is not None
    assert meta.version == "v1"

    # Swap to v2
    dummy_dc_v2 = DummyModel(name="dixon_coles", version="v2")
    manager.set_model("dixon_coles", dummy_dc_v2, ModelMetadata(version="v2", updated_at=datetime.now(timezone.utc)))
    assert manager.get_model("dixon_coles").version == "v2"


def test_model_manager_poll_database_trigger_reload():
    manager = ModelManager(polling_interval_seconds=0.0)  # force poll
    compressed_bytes = zlib.compress(pickle.dumps(DummyModel("dixon_coles", "v_db")))

    mock_row = MagicMock()
    mock_row.model_name = "dixon_coles"
    mock_row.version = "v_db"
    mock_row.artifact_bytes = compressed_bytes
    mock_row.manifest = {"manifest_key": "value"}
    mock_row.updated_at = datetime(2026, 9, 13, 15, 0, 0, tzinfo=timezone.utc)

    mock_session = MagicMock()
    mock_session.query.return_value.filter_by.return_value.all.return_value = [mock_row]

    mock_factory = MagicMock()
    mock_factory.return_value.__enter__.return_value = mock_session

    with patch("backend.services.model_manager.SessionLocal", mock_factory):
        manager.check_and_reload()
        loaded = manager.get_model("dixon_coles")
        assert loaded.version == "v_db"
        assert manager.get_metadata("dixon_coles").version == "v_db"
