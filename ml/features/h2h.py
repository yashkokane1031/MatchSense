"""Head-to-head feature engineering.

Computes historical H2H statistics between two teams, looking backward
across all available seasons (not limited to current season — H2H history
is cross-season by design, since the comparison is within the same division).
"""

import pandas as pd


def compute_h2h_features(
    matches: pd.DataFrame,
    home_team: str,
    away_team: str,
    before_date: pd.Timestamp,
    max_meetings: int = 10,
) -> dict[str, float | int | None]:
    """Compute head-to-head features between two teams.

    Looks at the last `max_meetings` encounters between the two teams,
    regardless of who was home/away in those historical matches.

    Args:
        matches: Full matches DataFrame.
        home_team: Home team for the match being predicted.
        away_team: Away team for the match being predicted.
        before_date: Only consider matches before this date.
        max_meetings: Maximum number of historical meetings to consider.

    Returns:
        Dict of H2H features.
    """
    # Find all meetings between these two teams (either home or away)
    mask = (
        (matches["Date"] < before_date)
        & (
            ((matches["HomeTeam"] == home_team) & (matches["AwayTeam"] == away_team))
            | ((matches["HomeTeam"] == away_team) & (matches["AwayTeam"] == home_team))
        )
    )
    h2h_matches = matches[mask].sort_values("Date", ascending=False).head(max_meetings)

    if len(h2h_matches) == 0:
        return _empty_h2h_features()

    # Count results from the perspective of home_team (in the current fixture)
    home_wins = 0
    draws = 0
    away_wins = 0
    home_team_goals = []
    away_team_goals = []

    for _, row in h2h_matches.iterrows():
        if row["HomeTeam"] == home_team:
            # home_team was actually at home in this historical match
            ht_goals = row["FTHG"]
            at_goals = row["FTAG"]
        else:
            # home_team was away in this historical match
            ht_goals = row["FTAG"]
            at_goals = row["FTHG"]

        home_team_goals.append(ht_goals)
        away_team_goals.append(at_goals)

        if ht_goals > at_goals:
            home_wins += 1
        elif ht_goals == at_goals:
            draws += 1
        else:
            away_wins += 1

    n = len(h2h_matches)
    return {
        "h2h_home_team_wins": home_wins,
        "h2h_draws": draws,
        "h2h_away_team_wins": away_wins,
        "h2h_home_team_goals_avg": sum(home_team_goals) / n,
        "h2h_away_team_goals_avg": sum(away_team_goals) / n,
        "h2h_total_matches": n,
    }


def _empty_h2h_features() -> dict[str, float | int | None]:
    """Return H2H features with all null values (no historical meetings)."""
    return {
        "h2h_home_team_wins": None,
        "h2h_draws": None,
        "h2h_away_team_wins": None,
        "h2h_home_team_goals_avg": None,
        "h2h_away_team_goals_avg": None,
        "h2h_total_matches": 0,
    }
