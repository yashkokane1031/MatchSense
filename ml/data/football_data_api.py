"""Football-Data.org API client for upcoming Premier League fixtures."""

from datetime import datetime, timezone
import logging
import requests

from ml.data.ingestion import normalize_football_data_org_name

logger = logging.getLogger(__name__)

BASE_URL = "https://api.football-data.org/v4"


class FootballDataClient:
    """Client for querying Football-Data.org Premier League endpoints."""

    def __init__(self, api_key: str = "", timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout
        self.headers = {"X-Auth-Token": api_key} if api_key else {}

    def get_scheduled_fixtures(self) -> list[dict]:
        """Fetch scheduled fixtures and return normalized fixture dictionaries."""
        url = f"{BASE_URL}/competitions/PL/matches?status=SCHEDULED"
        logger.info("Fetching scheduled fixtures from %s", url)
        resp = requests.get(url, headers=self.headers, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for m in data.get("matches", []):
            start_year = m.get("season", {}).get("startDate", "")[:4]
            end_year = m.get("season", {}).get("endDate", "")[2:4]
            season_label = (
                f"{start_year}-{end_year}"
                if start_year and end_year
                else "2025-26"
            )

            raw_kickoff = m.get("utcDate")
            kickoff_dt = (
                datetime.fromisoformat(raw_kickoff.replace("Z", "+00:00"))
                if raw_kickoff
                else datetime.now(timezone.utc)
            )

            results.append({
                "id": m["id"],
                "season": season_label,
                "gameweek": m.get("matchday", 1),
                "kickoff_time": kickoff_dt,
                "home_team": normalize_football_data_org_name(m["homeTeam"]["name"]),
                "away_team": normalize_football_data_org_name(m["awayTeam"]["name"]),
                "status": m.get("status", "SCHEDULED"),
            })
        return results
