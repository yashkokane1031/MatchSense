"""Data ingestion pipeline for football-data.co.uk CSVs.

Downloads, parses, normalizes, and validates Premier League match data
from football-data.co.uk CSV files. Handles team name inconsistencies
across seasons and date format variations.
"""

import logging
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

logger = logging.getLogger(__name__)

# football-data.co.uk CSV URL template
# Season codes: "2223" = 2022/23, "2324" = 2023/24, etc.
CSV_URL_TEMPLATE = "https://www.football-data.co.uk/mmz4281/{season_code}/E0.csv"

# 4 seasons: enough data, minimal team churn (~28-30 distinct teams)
DEFAULT_SEASONS: list[dict[str, str]] = [
    {"code": "2223", "label": "2022-23"},
    {"code": "2324", "label": "2023-24"},
    {"code": "2425", "label": "2024-25"},
    {"code": "2526", "label": "2025-26"},
]

# Columns to extract from CSV
COLUMNS_CORE = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]
COLUMNS_HALF_TIME = ["HTHG", "HTAG"]
COLUMNS_STATS = ["HS", "AS", "HST", "AST", "HC", "AC", "HF", "AF", "HY", "AY", "HR", "AR"]
COLUMNS_ODDS = ["AvgH", "AvgD", "AvgA", "B365H", "B365D", "B365A"]

# Team name normalization: maps football-data.co.uk names to canonical names.
# football-data.co.uk is mostly consistent, but handle known edge cases.
TEAM_NAME_MAP: dict[str, str] = {
    "Man United": "Manchester Utd",
    "Man City": "Manchester City",
    "Nott'm Forest": "Nottingham Forest",
    "Nottingham": "Nottingham Forest",
    "Sheffield United": "Sheffield Utd",
    "Spurs": "Tottenham",
    "Wolves": "Wolverhampton",
}


def normalize_team_name(name: str) -> str:
    """Normalize a team name to its canonical form.

    Args:
        name: Raw team name from the CSV.

    Returns:
        Canonical team name. If no mapping exists, returns the input unchanged.
    """
    return TEAM_NAME_MAP.get(name, name)


def download_season_csv(season_code: str, cache_dir: Path | None = None) -> str:
    """Download a season CSV from football-data.co.uk.

    Args:
        season_code: Two-digit season code (e.g., "2425" for 2024/25).
        cache_dir: Optional directory to cache downloaded CSVs. If the file
            already exists, it's read from cache instead of downloading.

    Returns:
        CSV content as string.

    Raises:
        requests.HTTPError: If the download fails.
    """
    if cache_dir:
        cache_path = cache_dir / f"E0_{season_code}.csv"
        if cache_path.exists():
            logger.info("Loading season %s from cache: %s", season_code, cache_path)
            return cache_path.read_text(encoding="utf-8", errors="replace")

    url = CSV_URL_TEMPLATE.format(season_code=season_code)
    logger.info("Downloading season %s from %s", season_code, url)

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    content = response.text

    if cache_dir:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = cache_dir / f"E0_{season_code}.csv"
        cache_path.write_text(content, encoding="utf-8")
        logger.info("Cached season %s to %s", season_code, cache_path)

    return content


def parse_season_csv(csv_content: str, season_label: str) -> pd.DataFrame:
    """Parse a football-data.co.uk CSV into a cleaned DataFrame.

    Handles both dd/mm/yy and dd/mm/yyyy date formats (CSVs are inconsistent
    across seasons). Normalizes team names and extracts relevant columns.

    Args:
        csv_content: Raw CSV string content.
        season_label: Human-readable season label (e.g., "2024-25").

    Returns:
        Cleaned DataFrame with standardized column names.
    """
    df = pd.read_csv(StringIO(csv_content), encoding="utf-8", on_bad_lines="skip")

    # Drop completely empty rows (some CSVs have trailing empty rows)
    df = df.dropna(how="all")

    # Select columns that exist in this CSV (some seasons lack certain stats)
    all_desired = COLUMNS_CORE + COLUMNS_HALF_TIME + COLUMNS_STATS + COLUMNS_ODDS
    available = [c for c in all_desired if c in df.columns]
    df = df[available].copy()

    # Parse dates — handle both dd/mm/yy and dd/mm/yyyy
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, format="mixed")

    # Normalize team names
    df["HomeTeam"] = df["HomeTeam"].apply(normalize_team_name)
    df["AwayTeam"] = df["AwayTeam"].apply(normalize_team_name)

    # Add season label
    df["Season"] = season_label

    # Ensure integer goals (sometimes parsed as float due to NaN rows)
    for col in ["FTHG", "FTAG"]:
        df[col] = df[col].astype(int)

    # Sort by date
    df = df.sort_values("Date").reset_index(drop=True)

    logger.info(
        "Parsed season %s: %d matches, %d unique teams",
        season_label,
        len(df),
        df["HomeTeam"].nunique() + df["AwayTeam"].nunique()
        - len(set(df["HomeTeam"]) & set(df["AwayTeam"])),
    )

    return df


def compute_implied_probabilities(df: pd.DataFrame) -> pd.DataFrame:
    """Compute bookmaker implied probabilities from decimal odds.

    Removes the overround (bookmaker margin) by normalizing:
        prob_i = (1/odds_i) / sum(1/all_odds)

    Args:
        df: DataFrame with AvgH, AvgD, AvgA columns (market average odds).

    Returns:
        DataFrame with added implied_prob_home, implied_prob_draw, implied_prob_away columns.
    """
    if not all(c in df.columns for c in ["AvgH", "AvgD", "AvgA"]):
        logger.warning("Odds columns not found, skipping implied probability calculation")
        df["implied_prob_home"] = None
        df["implied_prob_draw"] = None
        df["implied_prob_away"] = None
        return df

    # Raw implied probabilities (sum > 1 due to overround)
    raw_home = 1.0 / df["AvgH"]
    raw_draw = 1.0 / df["AvgD"]
    raw_away = 1.0 / df["AvgA"]

    # Normalize to remove overround
    total = raw_home + raw_draw + raw_away
    df["implied_prob_home"] = raw_home / total
    df["implied_prob_draw"] = raw_draw / total
    df["implied_prob_away"] = raw_away / total

    return df


def load_all_seasons(
    seasons: list[dict[str, str]] | None = None,
    cache_dir: Path | None = None,
) -> pd.DataFrame:
    """Download, parse, and combine all configured seasons.

    Args:
        seasons: List of season configs with 'code' and 'label' keys.
            Defaults to DEFAULT_SEASONS.
        cache_dir: Optional directory to cache downloaded CSVs.

    Returns:
        Combined DataFrame of all seasons, sorted by date.
    """
    if seasons is None:
        seasons = DEFAULT_SEASONS

    all_dfs: list[pd.DataFrame] = []
    for season in seasons:
        csv_content = download_season_csv(season["code"], cache_dir=cache_dir)
        df = parse_season_csv(csv_content, season["label"])
        df = compute_implied_probabilities(df)
        all_dfs.append(df)

    combined = pd.concat(all_dfs, ignore_index=True)
    combined = combined.sort_values("Date").reset_index(drop=True)

    unique_teams = sorted(set(combined["HomeTeam"]) | set(combined["AwayTeam"]))
    logger.info(
        "Loaded %d total matches across %d seasons with %d unique teams: %s",
        len(combined),
        len(seasons),
        len(unique_teams),
        ", ".join(unique_teams),
    )

    return combined
