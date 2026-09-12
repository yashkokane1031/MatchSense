"""Database loader utilities for matches.

Provides functions to save match DataFrames to the database
and load matches from the database into DataFrames for training and feature engineering.
"""

import logging

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.schemas import Match

logger = logging.getLogger(__name__)


def save_matches_to_db(session: Session, df: pd.DataFrame) -> int:
    """Save match records from a DataFrame into the database.

    Skips matches that already exist (by season, date, home_team, away_team).

    Args:
        session: Active SQLAlchemy session.
        df: DataFrame of parsed and validated match records.

    Returns:
        Number of newly inserted match records.
    """
    inserted = 0

    for _, row in df.iterrows():
        match_date = row["Date"].date() if hasattr(row["Date"], "date") else row["Date"]

        # Check existing match
        stmt = select(Match).where(
            Match.season == row["Season"],
            Match.date == match_date,
            Match.home_team == row["HomeTeam"],
            Match.away_team == row["AwayTeam"],
        )
        existing = session.execute(stmt).scalar_one_or_none()
        if existing is not None:
            continue

        def _get_int(val):
            return int(val) if pd.notna(val) else None

        def _get_float(val):
            return float(val) if pd.notna(val) else None

        match = Match(
            season=str(row["Season"]),
            date=match_date,
            home_team=str(row["HomeTeam"]),
            away_team=str(row["AwayTeam"]),
            home_goals=int(row["FTHG"]),
            away_goals=int(row["FTAG"]),
            result=str(row["FTR"]),
            ht_home_goals=_get_int(row.get("HTHG")),
            ht_away_goals=_get_int(row.get("HTAG")),
            home_shots=_get_int(row.get("HS")),
            away_shots=_get_int(row.get("AS")),
            home_shots_on_target=_get_int(row.get("HST")),
            away_shots_on_target=_get_int(row.get("AST")),
            home_corners=_get_int(row.get("HC")),
            away_corners=_get_int(row.get("AC")),
            home_fouls=_get_int(row.get("HF")),
            away_fouls=_get_int(row.get("AF")),
            home_yellows=_get_int(row.get("HY")),
            away_yellows=_get_int(row.get("AY")),
            home_reds=_get_int(row.get("HR")),
            away_reds=_get_int(row.get("AR")),
            avg_odds_home=_get_float(row.get("AvgH")),
            avg_odds_draw=_get_float(row.get("AvgD")),
            avg_odds_away=_get_float(row.get("AvgA")),
        )
        session.add(match)
        inserted += 1

    session.commit()
    logger.info("Saved %d new matches to database", inserted)
    return inserted


def load_matches_from_db(
    session: Session, season: str | None = None
) -> pd.DataFrame:
    """Load matches from database into a pandas DataFrame.

    Returns DataFrame standardized to column names used by feature pipeline
    and Dixon-Coles model: Date, HomeTeam, AwayTeam, FTHG, FTAG, FTR, Season, etc.

    Args:
        session: Active SQLAlchemy session.
        season: Optional season filter (e.g. "2024-25").

    Returns:
        DataFrame sorted by Date.
    """
    stmt = select(Match)
    if season:
        stmt = stmt.where(Match.season == season)
    stmt = stmt.order_by(Match.date.asc())

    matches = session.execute(stmt).scalars().all()
    if not matches:
        return pd.DataFrame()

    records = []
    for m in matches:
        records.append({
            "Date": pd.to_datetime(m.date),
            "HomeTeam": m.home_team,
            "AwayTeam": m.away_team,
            "FTHG": m.home_goals,
            "FTAG": m.away_goals,
            "FTR": m.result,
            "Season": m.season,
            "HTHG": m.ht_home_goals,
            "HTAG": m.ht_away_goals,
            "HS": m.home_shots,
            "AS": m.away_shots,
            "HST": m.home_shots_on_target,
            "AST": m.away_shots_on_target,
            "HC": m.home_corners,
            "AC": m.away_corners,
            "HF": m.home_fouls,
            "AF": m.away_fouls,
            "HY": m.home_yellows,
            "AY": m.away_yellows,
            "HR": m.home_reds,
            "AR": m.away_reds,
            "AvgH": m.avg_odds_home,
            "AvgD": m.avg_odds_draw,
            "AvgA": m.avg_odds_away,
        })

    df = pd.DataFrame(records)
    df = df.sort_values("Date").reset_index(drop=True)
    return df
