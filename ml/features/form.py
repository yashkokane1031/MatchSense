"""Recent form and temporal feature engineering.

Computes per-team rolling statistics using ONLY data from before the match date.
All features reset at season boundaries — no cross-division carryover.

Season-boundary rule:
- Rolling windows start fresh at the beginning of each season
- For a team's first N matches of a season (N < window), the feature uses
  however many PL matches are available that season
- Newly promoted teams with 0 PL matches get null form features
"""

import pandas as pd


def compute_form_features(
    matches: pd.DataFrame,
    team: str,
    before_date: pd.Timestamp,
    season: str,
    window: int = 5,
) -> dict[str, float | None]:
    """Compute recent form features for a team.

    Uses ONLY matches from the same season, before the given date.
    This enforces season-boundary reset and prevents data leakage.

    Args:
        matches: Full matches DataFrame.
        team: Team name to compute features for.
        before_date: Only consider matches strictly before this date.
        season: Current season label (e.g., "2024-25").
        window: Number of recent matches to consider.

    Returns:
        Dict of form features. Values are None if insufficient data.
    """
    # Filter: same season, before date, team involved
    mask = (
        (matches["Season"] == season)
        & (matches["Date"] < before_date)
        & ((matches["HomeTeam"] == team) | (matches["AwayTeam"] == team))
    )
    team_matches = matches[mask].sort_values("Date", ascending=False)

    if len(team_matches) == 0:
        return _empty_form_features()

    # Take the last `window` matches (or fewer if early in season)
    recent = team_matches.head(window)

    # Compute points, goals for each match
    points_list = []
    goals_scored_list = []
    goals_conceded_list = []
    results_list = []  # W/D/L

    for _, row in recent.iterrows():
        if row["HomeTeam"] == team:
            gs = row["FTHG"]
            gc = row["FTAG"]
            result = "W" if row["FTR"] == "H" else ("D" if row["FTR"] == "D" else "L")
        else:
            gs = row["FTAG"]
            gc = row["FTHG"]
            result = "W" if row["FTR"] == "A" else ("D" if row["FTR"] == "D" else "L")

        points_list.append(3 if result == "W" else (1 if result == "D" else 0))
        goals_scored_list.append(gs)
        goals_conceded_list.append(gc)
        results_list.append(result)

    n = len(recent)
    return {
        "points_last_n": sum(points_list),
        "goals_scored_last_n": sum(goals_scored_list),
        "goals_conceded_last_n": sum(goals_conceded_list),
        "goal_diff_last_n": sum(goals_scored_list) - sum(goals_conceded_list),
        "wins_last_n": results_list.count("W"),
        "draws_last_n": results_list.count("D"),
        "losses_last_n": results_list.count("L"),
        "matches_available": n,
    }


def compute_season_features(
    matches: pd.DataFrame,
    team: str,
    before_date: pd.Timestamp,
    season: str,
) -> dict[str, float | None]:
    """Compute season-to-date aggregate features for a team.

    Args:
        matches: Full matches DataFrame.
        team: Team name.
        before_date: Only consider matches before this date.
        season: Current season label.

    Returns:
        Dict of season-aggregate features.
    """
    mask = (
        (matches["Season"] == season)
        & (matches["Date"] < before_date)
        & ((matches["HomeTeam"] == team) | (matches["AwayTeam"] == team))
    )
    team_matches = matches[mask]

    if len(team_matches) == 0:
        return {
            "points_per_game_season": None,
            "goals_scored_avg_season": None,
            "goals_conceded_avg_season": None,
            "matches_played": 0,
        }

    total_points = 0
    total_gs = 0
    total_gc = 0

    for _, row in team_matches.iterrows():
        if row["HomeTeam"] == team:
            gs, gc = row["FTHG"], row["FTAG"]
            pts = 3 if row["FTR"] == "H" else (1 if row["FTR"] == "D" else 0)
        else:
            gs, gc = row["FTAG"], row["FTHG"]
            pts = 3 if row["FTR"] == "A" else (1 if row["FTR"] == "D" else 0)
        total_points += pts
        total_gs += gs
        total_gc += gc

    n = len(team_matches)
    return {
        "points_per_game_season": total_points / n,
        "goals_scored_avg_season": total_gs / n,
        "goals_conceded_avg_season": total_gc / n,
        "matches_played": n,
    }


def compute_home_away_splits(
    matches: pd.DataFrame,
    team: str,
    before_date: pd.Timestamp,
    season: str,
) -> dict[str, float | None]:
    """Compute home vs away performance splits.

    Args:
        matches: Full matches DataFrame.
        team: Team name.
        before_date: Only consider matches before this date.
        season: Current season label.

    Returns:
        Dict of home/away split features.
    """
    season_mask = (matches["Season"] == season) & (matches["Date"] < before_date)

    # Home matches
    home_mask = season_mask & (matches["HomeTeam"] == team)
    home_matches = matches[home_mask]

    # Away matches
    away_mask = season_mask & (matches["AwayTeam"] == team)
    away_matches = matches[away_mask]

    result: dict[str, float | None] = {}

    if len(home_matches) > 0:
        result["home_goals_scored_avg"] = home_matches["FTHG"].mean()
        result["home_goals_conceded_avg"] = home_matches["FTAG"].mean()
        result["home_win_rate"] = (home_matches["FTR"] == "H").mean()
    else:
        result["home_goals_scored_avg"] = None
        result["home_goals_conceded_avg"] = None
        result["home_win_rate"] = None

    if len(away_matches) > 0:
        result["away_goals_scored_avg"] = away_matches["FTAG"].mean()
        result["away_goals_conceded_avg"] = away_matches["FTHG"].mean()
        result["away_win_rate"] = (away_matches["FTR"] == "A").mean()
    else:
        result["away_goals_scored_avg"] = None
        result["away_goals_conceded_avg"] = None
        result["away_win_rate"] = None

    return result


def compute_temporal_features(
    matches: pd.DataFrame,
    team: str,
    match_date: pd.Timestamp,
    season: str,
    all_seasons: list[str],
) -> dict[str, float | int | bool | None]:
    """Compute temporal features: fatigue, league position, promotion status.

    Args:
        matches: Full matches DataFrame.
        team: Team name.
        match_date: Date of the match being predicted.
        season: Current season label.
        all_seasons: List of all season labels in order.

    Returns:
        Dict of temporal features.
    """
    # Days since last match
    mask = (
        (matches["Date"] < match_date)
        & ((matches["HomeTeam"] == team) | (matches["AwayTeam"] == team))
    )
    prev_matches = matches[mask].sort_values("Date", ascending=False)

    if len(prev_matches) > 0:
        last_match_date = prev_matches.iloc[0]["Date"]
        days_since_last = (match_date - last_match_date).days
    else:
        days_since_last = None

    # Is newly promoted: team was not in PL the previous season
    season_idx = all_seasons.index(season) if season in all_seasons else -1
    if season_idx > 0:
        prev_season = all_seasons[season_idx - 1]
        prev_season_teams = set(
            matches[matches["Season"] == prev_season]["HomeTeam"]
        ) | set(matches[matches["Season"] == prev_season]["AwayTeam"])
        is_newly_promoted = team not in prev_season_teams
    else:
        # First season in dataset — can't determine promotion status
        is_newly_promoted = False

    return {
        "days_since_last_match": days_since_last,
        "is_newly_promoted": is_newly_promoted,
    }


def _empty_form_features() -> dict[str, float | None]:
    """Return form features with all null values (no data available)."""
    return {
        "points_last_n": None,
        "goals_scored_last_n": None,
        "goals_conceded_last_n": None,
        "goal_diff_last_n": None,
        "wins_last_n": None,
        "draws_last_n": None,
        "losses_last_n": None,
        "matches_available": 0,
    }
