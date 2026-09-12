"""Feature pipeline orchestrator.

Combines form, H2H, temporal, match statistics, and separated xG features
into a single feature vector per match.
Handles edge cases (newly promoted teams, early-season data scarcity) and
enforces strict temporal ordering to prevent data leakage.
"""

import logging

import pandas as pd

from ml.features.form import (
    compute_form_features,
    compute_home_away_splits,
    compute_season_features,
    compute_temporal_features,
)
from ml.features.h2h import compute_h2h_features
from ml.features.match_stats import compute_match_stats_features
from ml.features.xg import compute_rolling_xg

logger = logging.getLogger(__name__)


def build_match_features(
    matches: pd.DataFrame,
    home_team: str,
    away_team: str,
    match_date: pd.Timestamp,
    season: str,
    all_seasons: list[str],
    form_window: int = 5,
    understat_matches: pd.DataFrame | None = None,
    precomputed_elo: dict[tuple[pd.Timestamp, str, str], dict[str, float]] | None = None,
) -> dict[str, float | int | bool | None]:
    """Build the complete feature vector for a single match.

    All features use ONLY data from before match_date (leakage prevention).
    Form features reset at season boundaries (no cross-division carryover).

    Args:
        matches: Full historical matches DataFrame.
        home_team: Home team name.
        away_team: Away team name.
        match_date: Date of the match being predicted.
        season: Season label for the match (e.g., "2024-25").
        all_seasons: Ordered list of all season labels.
        form_window: Number of recent matches for form features.
        understat_matches: Optional DataFrame with Understat match-level xG.
        precomputed_elo: Optional precomputed window-anchored Elo features.

    Returns:
        Flat dict of all features for this match.
    """
    features: dict[str, float | int | bool | None] = {}

    # Home team features (prefixed with "home_")
    home_form = compute_form_features(matches, home_team, match_date, season, form_window)
    for k, v in home_form.items():
        features[f"home_{k}"] = v

    home_season = compute_season_features(matches, home_team, match_date, season)
    for k, v in home_season.items():
        features[f"home_{k}"] = v

    home_splits = compute_home_away_splits(matches, home_team, match_date, season)
    for k, v in home_splits.items():
        features[f"home_team_{k}"] = v

    home_temporal = compute_temporal_features(
        matches, home_team, match_date, season, all_seasons
    )
    for k, v in home_temporal.items():
        features[f"home_{k}"] = v

    home_match_stats = compute_match_stats_features(
        matches, home_team, match_date, season, form_window
    )
    for k, v in home_match_stats.items():
        features[f"home_{k}"] = v

    home_xg = compute_rolling_xg(
        understat_matches, home_team, match_date, season, form_window
    )
    for k, v in home_xg.items():
        features[f"home_{k}"] = v

    # Away team features (prefixed with "away_")
    away_form = compute_form_features(matches, away_team, match_date, season, form_window)
    for k, v in away_form.items():
        features[f"away_{k}"] = v

    away_season = compute_season_features(matches, away_team, match_date, season)
    for k, v in away_season.items():
        features[f"away_{k}"] = v

    away_splits = compute_home_away_splits(matches, away_team, match_date, season)
    for k, v in away_splits.items():
        features[f"away_team_{k}"] = v

    away_temporal = compute_temporal_features(
        matches, away_team, match_date, season, all_seasons
    )
    for k, v in away_temporal.items():
        features[f"away_{k}"] = v

    away_match_stats = compute_match_stats_features(
        matches, away_team, match_date, season, form_window
    )
    for k, v in away_match_stats.items():
        features[f"away_{k}"] = v

    away_xg = compute_rolling_xg(
        understat_matches, away_team, match_date, season, form_window
    )
    for k, v in away_xg.items():
        features[f"away_{k}"] = v

    # Head-to-head features (no prefix — symmetric)
    h2h = compute_h2h_features(matches, home_team, away_team, match_date)
    features.update(h2h)

    # Window-anchored Elo features (if supplied)
    if precomputed_elo is not None:
        elo_key = (match_date, home_team, away_team)
        if elo_key in precomputed_elo:
            features.update(precomputed_elo[elo_key])

    return features


def build_feature_matrix(
    matches: pd.DataFrame,
    form_window: int = 5,
    understat_matches: pd.DataFrame | None = None,
    precomputed_elo: dict[tuple[pd.Timestamp, str, str], dict[str, float]] | None = None,
) -> pd.DataFrame:
    """Build feature vectors for ALL matches in the dataset.

    Processes matches in chronological order, computing features for each
    match using only prior data.

    Args:
        matches: Full matches DataFrame, sorted by date.
        form_window: Number of recent matches for form features.
        understat_matches: Optional DataFrame with Understat match-level xG.
        precomputed_elo: Optional precomputed window-anchored Elo features.

    Returns:
        DataFrame where each row has the features for one match, plus
        the target columns (FTHG, FTAG, FTR).
    """
    matches_sorted = matches.sort_values("Date").reset_index(drop=True)
    all_seasons = sorted(matches_sorted["Season"].unique().tolist())
    rows = []

    for _, match in matches_sorted.iterrows():
        features = build_match_features(
            matches=matches_sorted,
            home_team=str(match["HomeTeam"]),
            away_team=str(match["AwayTeam"]),
            match_date=pd.Timestamp(match["Date"]),
            season=str(match["Season"]),
            all_seasons=all_seasons,
            form_window=form_window,
            understat_matches=understat_matches,
            precomputed_elo=precomputed_elo,
        )

        # Add identifiers and targets
        features["home_team"] = match["HomeTeam"]
        features["away_team"] = match["AwayTeam"]
        features["date"] = match["Date"]
        features["season"] = match["Season"]
        if "FTHG" in match and pd.notna(match["FTHG"]):
            features["home_goals"] = match["FTHG"]
        if "FTAG" in match and pd.notna(match["FTAG"]):
            features["away_goals"] = match["FTAG"]
        if "FTR" in match and pd.notna(match["FTR"]):
            features["result"] = match["FTR"]

        rows.append(features)

    result_df = pd.DataFrame(rows)
    logger.info(
        "Built feature matrix: %d matches, %d features", len(result_df), len(result_df.columns)
    )
    return result_df
