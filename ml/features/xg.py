"""Understat xG feature extractor with strict schema separation."""

import pandas as pd


def compute_rolling_xg(
    understat_matches: pd.DataFrame | None,
    team: str,
    match_date: pd.Timestamp,
    season: str,
    window: int = 5,
) -> dict[str, float | None]:
    """Compute rolling xG metrics strictly prior to match_date.

    Produces separate, isolated columns: rolling_xg_for, rolling_xg_against, rolling_xg_diff.
    Returns None for all metrics if understat_matches is None or no prior matches exist.

    Args:
        understat_matches: Optional DataFrame with Date, Season, HomeTeam, AwayTeam, home_xg, away_xg.
        team: Team name to compute features for.
        match_date: Date of the match being predicted.
        season: Season label (e.g. '2024-25').
        window: Rolling match window size (default 5).

    Returns:
        Dict mapping metric names to rolling averages or None.
    """
    if understat_matches is None or understat_matches.empty:
        return {
            "rolling_xg_for": None,
            "rolling_xg_against": None,
            "rolling_xg_diff": None,
        }

    prior = understat_matches[
        (understat_matches["Season"] == season)
        & (understat_matches["Date"] < match_date)
        & ((understat_matches["HomeTeam"] == team) | (understat_matches["AwayTeam"] == team))
    ].sort_values("Date")

    if prior.empty:
        return {
            "rolling_xg_for": None,
            "rolling_xg_against": None,
            "rolling_xg_diff": None,
        }

    recent = prior.tail(window)
    xg_for_list: list[float] = []
    xg_against_list: list[float] = []

    for _, row in recent.iterrows():
        is_home = row["HomeTeam"] == team
        xgf = row["home_xg"] if is_home else row["away_xg"]
        xga = row["away_xg"] if is_home else row["home_xg"]
        if pd.notna(xgf):
            xg_for_list.append(float(xgf))
        if pd.notna(xga):
            xg_against_list.append(float(xga))

    mean_xgf = float(pd.Series(xg_for_list).mean()) if xg_for_list else None
    mean_xga = float(pd.Series(xg_against_list).mean()) if xg_against_list else None
    diff = (
        float(mean_xgf - mean_xga)
        if mean_xgf is not None and mean_xga is not None
        else None
    )

    return {
        "rolling_xg_for": mean_xgf,
        "rolling_xg_against": mean_xga,
        "rolling_xg_diff": diff,
    }
