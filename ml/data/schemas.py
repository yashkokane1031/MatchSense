"""Pandera validation schemas for match data.

Validates data integrity at ingestion time: correct types, value ranges,
and consistency checks (e.g., FTR matches goal comparison).
"""

import pandera as pa
from pandera import Check, Column, DataFrameSchema

# All teams that have appeared in the Premier League in our 4-season window.
# Updated as new CSVs are ingested. Used for validation, not hard-coded restriction.
KNOWN_PL_TEAMS: set[str] = {
    "Arsenal",
    "Aston Villa",
    "Bournemouth",
    "Brentford",
    "Brighton",
    "Burnley",
    "Chelsea",
    "Coventry",
    "Crystal Palace",
    "Everton",
    "Fulham",
    "Hull",
    "Ipswich",
    "Leeds",
    "Leicester",
    "Liverpool",
    "Luton",
    "Manchester City",
    "Manchester Utd",
    "Newcastle",
    "Nottingham Forest",
    "Sheffield Utd",
    "Southampton",
    "Sunderland",
    "Tottenham",
    "West Ham",
    "Wolverhampton",
}


def _result_matches_goals(df: pa.typing.DataFrame) -> bool:
    """Check that FTR is consistent with FTHG/FTAG."""
    home_win = (df["FTHG"] > df["FTAG"]) == (df["FTR"] == "H")
    draw = (df["FTHG"] == df["FTAG"]) == (df["FTR"] == "D")
    away_win = (df["FTHG"] < df["FTAG"]) == (df["FTR"] == "A")
    return bool((home_win & draw & away_win).all())


raw_match_schema = DataFrameSchema(
    columns={
        "Date": Column(pa.DateTime, nullable=False),
        "HomeTeam": Column(str, nullable=False),
        "AwayTeam": Column(str, nullable=False),
        "FTHG": Column(int, Check.ge(0), nullable=False),
        "FTAG": Column(int, Check.ge(0), nullable=False),
        "FTR": Column(str, Check.isin(["H", "D", "A"]), nullable=False),
        "Season": Column(str, nullable=False),
    },
    # Optional columns — validated when present
    checks=[
        Check(
            _result_matches_goals,
            error="FTR does not match goal comparison (FTHG vs FTAG)",
        )
    ],
    coerce=True,
    strict=False,  # Allow extra columns (stats, odds)
)

# Schema for odds columns specifically
odds_schema = DataFrameSchema(
    columns={
        "AvgH": Column(float, Check.gt(1.0), nullable=True),
        "AvgD": Column(float, Check.gt(1.0), nullable=True),
        "AvgA": Column(float, Check.gt(1.0), nullable=True),
    },
    coerce=True,
    strict=False,
)
