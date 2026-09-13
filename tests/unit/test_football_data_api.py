# tests/unit/test_football_data_api.py
from unittest.mock import MagicMock, patch
import pytest

from ml.data.football_data_api import FootballDataClient
from ml.data.ingestion import normalize_football_data_org_name


def test_normalize_football_data_org_names():
    assert normalize_football_data_org_name("Arsenal FC") == "Arsenal"
    assert normalize_football_data_org_name("Manchester United FC") == "Manchester Utd"
    assert normalize_football_data_org_name("Nottingham Forest FC") == "Nottingham Forest"
    assert normalize_football_data_org_name("Sheffield United FC") == "Sheffield Utd"
    assert normalize_football_data_org_name("Tottenham Hotspur FC") == "Tottenham"
    assert normalize_football_data_org_name("Wolverhampton Wanderers FC") == "Wolverhampton"
    # Unmapped team with suffix stripping
    assert normalize_football_data_org_name("Sunderland FC") == "Sunderland"


def test_football_data_client_fetch_scheduled():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "matches": [
            {
                "id": 501234,
                "season": {"startDate": "2025-08-15", "endDate": "2026-05-24"},
                "matchday": 29,
                "utcDate": "2026-03-21T15:00:00Z",
                "status": "SCHEDULED",
                "homeTeam": {"name": "Arsenal FC"},
                "awayTeam": {"name": "Chelsea FC"},
            }
        ]
    }

    with patch("requests.get", return_value=mock_resp):
        client = FootballDataClient(api_key="test_key")
        fixtures = client.get_scheduled_fixtures()
        assert len(fixtures) == 1
        assert fixtures[0]["id"] == 501234
        assert fixtures[0]["home_team"] == "Arsenal"
        assert fixtures[0]["away_team"] == "Chelsea"
        assert fixtures[0]["gameweek"] == 29
        assert fixtures[0]["season"] == "2025-26"
