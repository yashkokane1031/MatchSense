"""Dynamic Premier League season identification.

Single source of truth for determining the active PL season.

Priority order:
  1. API-reported season (from Football-Data.org fixtures response) — authoritative.
  2. Date-based fallback — PL seasons run Aug–May, so:
       month >= 8 → {year}/{year+1}
       month <  8 → {year-1}/{year}

The API path is primary because the date rule can be wrong during
early August (before the season's first match) or late May/June
(after the final whistle but before month < 8 flips).
"""

from datetime import datetime, timezone


def _season_code_from_start_year(start_year: int) -> str:
    """Convert a season start year to the 4-digit code used by football-data.co.uk.

    Example: 2026 → "2627"
    """
    return f"{start_year % 100:02d}{(start_year + 1) % 100:02d}"


def _season_label_from_start_year(start_year: int) -> str:
    """Convert a season start year to a human-readable label.

    Example: 2026 → "2026-27"
    """
    return f"{start_year}-{(start_year + 1) % 100:02d}"


def _start_year_from_code(code: str) -> int:
    """Convert a 4-digit season code back to a full start year.

    Example: "2627" → 2026 (assumes 21st century for codes where first two digits < 50)
    """
    first_two = int(code[:2])
    century = 2000 if first_two < 50 else 1900
    return century + first_two


def derive_season_from_date(now: datetime | None = None) -> tuple[str, str]:
    """Derive the active PL season from the system date.

    This is the **fallback** path — used only when the API-reported
    season is unavailable.

    Args:
        now: Override for the current datetime (for deterministic testing).

    Returns:
        (season_code, season_label) — e.g. ("2627", "2026-27").
    """
    if now is None:
        now = datetime.now(timezone.utc)

    # PL seasons kick off mid-August (typically Aug 11–18).
    # In the offline fallback path, early August (Aug 1–14) safely remains
    # attributed to the prior season so we don't attempt to ingest fixtures
    # or CSVs before they exist.
    if now.month > 8 or (now.month == 8 and now.day >= 15):
        start_year = now.year
    else:
        start_year = now.year - 1

    return _season_code_from_start_year(start_year), _season_label_from_start_year(start_year)


def derive_current_season(
    api_season: tuple[str, str] | None = None,
    now: datetime | None = None,
) -> tuple[str, str]:
    """Return (season_code, season_label) for the active PL season.

    Uses the API-reported season as the authoritative answer when available.
    Falls back to date-based derivation when the API data is absent.

    Args:
        api_season: Optional (season_code, season_label) extracted from
            Football-Data.org's fixture response. When provided and non-empty,
            this is treated as ground truth — the API knows which season its
            own fixtures belong to.
        now: Override for the current datetime (used by the fallback path
            and for deterministic testing).

    Returns:
        (season_code, season_label) — e.g. ("2627", "2026-27").
    """
    if api_season is not None:
        code, label = api_season
        if code and label:
            return code, label

    return derive_season_from_date(now)


def derive_training_window(
    current_code: str,
    window_size: int = 4,
) -> list[dict[str, str]]:
    """Return the N-season sliding window ending at current_code.

    Args:
        current_code: 4-digit code of the current season (e.g. "2627").
        window_size: Number of seasons in the training window.

    Returns:
        List of {"code": ..., "label": ...} dicts, oldest first.

    Example:
        derive_training_window("2627", 4)
        → [
            {"code": "2324", "label": "2023-24"},
            {"code": "2425", "label": "2024-25"},
            {"code": "2526", "label": "2025-26"},
            {"code": "2627", "label": "2026-27"},
          ]
    """
    start_year = _start_year_from_code(current_code)
    seasons = []
    for i in range(window_size - 1, -1, -1):
        y = start_year - i
        seasons.append({
            "code": _season_code_from_start_year(y),
            "label": _season_label_from_start_year(y),
        })
    return seasons
