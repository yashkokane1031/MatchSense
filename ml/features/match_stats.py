"""Rolling match statistics and shot quality feature extractor."""

import pandas as pd


def compute_match_stats_features(
    matches: pd.DataFrame,
    team: str,
    match_date: pd.Timestamp,
    season: str,
    window: int = 5,
) -> dict[str, float | None]:
    """Compute rolling shot and corner metrics strictly prior to match_date.

    Resets at season boundaries to prevent cross-division contamination.

    Args:
        matches: Full matches DataFrame.
        team: Team name to compute features for.
        match_date: Kickoff date of the match being predicted.
        season: Season label (e.g. '2024-25').
        window: Number of recent matches to consider (default 5).

    Returns:
        Dict mapping metric names to rolling averages or None if no prior matches exist.
    """
    prior = matches[
        (matches["Season"] == season)
        & (matches["Date"] < match_date)
        & ((matches["HomeTeam"] == team) | (matches["AwayTeam"] == team))
    ].sort_values("Date")

    if prior.empty:
        return {
            "rolling_shots_for": None,
            "rolling_shots_against": None,
            "rolling_sot_for": None,
            "rolling_sot_against": None,
            "rolling_sot_ratio": None,
            "rolling_corners_for": None,
            "rolling_corners_against": None,
        }

    recent = prior.tail(window)
    shots_for_list: list[float] = []
    shots_against_list: list[float] = []
    sot_for_list: list[float] = []
    sot_against_list: list[float] = []
    corners_for_list: list[float] = []
    corners_against_list: list[float] = []

    has_shots = "HS" in recent.columns and "AS" in recent.columns
    has_sot = "HST" in recent.columns and "AST" in recent.columns
    has_corners = "HC" in recent.columns and "AC" in recent.columns

    for _, row in recent.iterrows():
        is_home = row["HomeTeam"] == team

        if has_shots:
            sf = row["HS"] if is_home else row["AS"]
            sa = row["AS"] if is_home else row["HS"]
            if pd.notna(sf):
                shots_for_list.append(float(sf))
            if pd.notna(sa):
                shots_against_list.append(float(sa))

        if has_sot:
            sotf = row["HST"] if is_home else row["AST"]
            sota = row["AST"] if is_home else row["HST"]
            if pd.notna(sotf):
                sot_for_list.append(float(sotf))
            if pd.notna(sota):
                sot_against_list.append(float(sota))

        if has_corners:
            cf = row["HC"] if is_home else row["AC"]
            ca = row["AC"] if is_home else row["HC"]
            if pd.notna(cf):
                corners_for_list.append(float(cf))
            if pd.notna(ca):
                corners_against_list.append(float(ca))

    mean_sf = float(pd.Series(shots_for_list).mean()) if shots_for_list else None
    mean_sa = float(pd.Series(shots_against_list).mean()) if shots_against_list else None
    mean_sotf = float(pd.Series(sot_for_list).mean()) if sot_for_list else None
    mean_sota = float(pd.Series(sot_against_list).mean()) if sot_against_list else None
    mean_cf = float(pd.Series(corners_for_list).mean()) if corners_for_list else None
    mean_ca = float(pd.Series(corners_against_list).mean()) if corners_against_list else None

    sot_ratio = (
        float(mean_sotf / (mean_sf + 1e-5))
        if mean_sotf is not None and mean_sf is not None
        else None
    )

    return {
        "rolling_shots_for": mean_sf,
        "rolling_shots_against": mean_sa,
        "rolling_sot_for": mean_sotf,
        "rolling_sot_against": mean_sota,
        "rolling_sot_ratio": sot_ratio,
        "rolling_corners_for": mean_cf,
        "rolling_corners_against": mean_ca,
    }
