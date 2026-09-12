"""Window-anchored Elo rating engine with dynamic margin-of-victory and empirical promoted entry."""

import numpy as np
import pandas as pd


class EloEngine:
    """Computes dynamic soccer Elo ratings with home ground adjustment and mean reversion."""

    def __init__(
        self,
        k_base: float = 24.0,
        home_advantage: float = 65.0,
        reversion_weight: float = 0.75,
    ) -> None:
        self.k_base = k_base
        self.home_advantage = home_advantage
        self.reversion_weight = reversion_weight

    def expected_probabilities(self, r_home: float, r_away: float) -> tuple[float, float]:
        """Compute expected outcome score probabilities for home and away teams.

        Args:
            r_home: Pre-match rating of the home team.
            r_away: Pre-match rating of the away team.

        Returns:
            Tuple of (p_home, p_away).
        """
        dr = (r_home + self.home_advantage) - r_away
        p_home = 1.0 / (1.0 + 10.0 ** (-dr / 400.0))
        return float(p_home), float(1.0 - p_home)

    def margin_multiplier(self, goal_diff: int) -> float:
        """Dynamic multiplier based on margin of victory following World Football Elo specs."""
        diff = abs(goal_diff)
        if diff <= 1:
            return 1.0
        if diff == 2:
            return 1.5
        return float((11.0 + diff) / 8.0)

    def apply_season_transition(
        self,
        ratings: dict[str, float],
        promoted_teams: list[str] | None = None,
    ) -> dict[str, float]:
        """Apply inter-season mean-reversion and empirical Q0.25 promoted entry.

        Surviving teams undergo: R_new = reversion_weight * R_old + (1 - reversion_weight) * 1500.
        Promoted clubs enter at Q0.25 of post-reversion surviving ratings.

        Args:
            ratings: Team name to current rating dictionary.
            promoted_teams: Optional list of newly promoted clubs joining at this transition.

        Returns:
            Updated ratings dictionary.
        """
        new_ratings: dict[str, float] = {}
        for team, r in ratings.items():
            new_ratings[team] = self.reversion_weight * r + (1.0 - self.reversion_weight) * 1500.0

        if promoted_teams:
            surviving_vals = list(new_ratings.values())
            q25 = float(np.percentile(surviving_vals, 25)) if surviving_vals else 1450.0
            for p_team in promoted_teams:
                new_ratings[p_team] = q25

        return new_ratings


def compute_window_elo(
    matches: pd.DataFrame,
    k_base: float = 24.0,
    home_advantage: float = 65.0,
    reversion_weight: float = 0.75,
) -> tuple[dict[tuple[pd.Timestamp, str, str], dict[str, float]], dict[str, float]]:
    """Compute pre-match Elo features across an active training/evaluation window.

    Anchors active teams to 1500.0 at Season 1, Gameweek 1 of the window.

    Args:
        matches: DataFrame containing Date, Season, HomeTeam, AwayTeam, FTHG, FTAG, FTR.
        k_base: Base K-factor.
        home_advantage: Constant home field advantage added to home team's rating.
        reversion_weight: Summer mean-reversion dampening weight (0.75 standard).

    Returns:
        tuple of (match_features_dict, final_team_ratings).
        match_features_dict keys are (Date, HomeTeam, AwayTeam).
    """
    matches_sorted = matches.sort_values("Date").reset_index(drop=True)
    engine = EloEngine(
        k_base=k_base, home_advantage=home_advantage, reversion_weight=reversion_weight
    )

    ratings: dict[str, float] = {}
    match_features: dict[tuple[pd.Timestamp, str, str], dict[str, float]] = {}
    current_season: str | None = None

    for _, row in matches_sorted.iterrows():
        season = str(row["Season"])
        home = str(row["HomeTeam"])
        away = str(row["AwayTeam"])
        date = pd.Timestamp(row["Date"])

        # Detect season boundary
        if current_season is not None and season != current_season:
            surviving = set(ratings.keys())
            upcoming_season_matches = matches_sorted[matches_sorted["Season"] == season]
            season_teams = set(upcoming_season_matches["HomeTeam"]).union(
                set(upcoming_season_matches["AwayTeam"])
            )
            promoted = list(season_teams - surviving)
            ratings = engine.apply_season_transition(ratings, promoted_teams=promoted)

        current_season = season

        # Initialize any unseen team at 1500
        if home not in ratings:
            ratings[home] = 1500.0
        if away not in ratings:
            ratings[away] = 1500.0

        r_home = ratings[home]
        r_away = ratings[away]
        p_home, p_away = engine.expected_probabilities(r_home, r_away)

        match_features[(date, home, away)] = {
            "home_elo": r_home,
            "away_elo": r_away,
            "elo_diff": (r_home + home_advantage) - r_away,
            "elo_prob_home": p_home,
        }

        # Post-match update
        ftr = str(row["FTR"])
        fthg = int(row["FTHG"])
        ftag = int(row["FTAG"])
        if ftr == "H":
            s_home = 1.0
        elif ftr == "D":
            s_home = 0.5
        else:
            s_home = 0.0

        mult = engine.margin_multiplier(fthg - ftag)
        k_eff = k_base * mult
        ratings[home] = r_home + k_eff * (s_home - p_home)
        ratings[away] = r_away + k_eff * ((1.0 - s_home) - p_away)

    return match_features, ratings
