"""XGBoost match outcome predictor with window-anchored Elo and cold-start fallback."""

import logging
from typing import Any

import numpy as np
import pandas as pd
import xgboost as xgb

from ml.features.elo import compute_window_elo
from ml.features.pipeline import build_feature_matrix, build_match_features
from ml.models.base import BasePredictor

logger = logging.getLogger(__name__)

DEFAULT_XGB_PARAMS: dict[str, Any] = {
    "n_estimators": 120,
    "max_depth": 3,
    "learning_rate": 0.04,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "reg_alpha": 0.5,
    "reg_lambda": 1.0,
    "min_child_weight": 3,
    "random_state": 42,
    "objective": "multi:softprob",
    "num_class": 3,
    "eval_metric": "mlogloss",
}


class XGBoostPredictor(BasePredictor):
    """Discriminative match outcome predictor using regularized gradient-boosted trees."""

    def __init__(
        self,
        params: dict[str, Any] | None = None,
        precomputed_features: pd.DataFrame | None = None,
    ) -> None:
        merged = {**DEFAULT_XGB_PARAMS, **(params or {})}
        self.n_estimators = int(merged.pop("n_estimators", 120))
        self.params = merged
        self.booster: xgb.Booster | None = None
        self._feature_names: list[str] = []
        self._fitted_matches: pd.DataFrame | None = None
        self._final_elo: dict[str, float] = {}
        self._last_date: pd.Timestamp | None = None
        self._last_season: str | None = None
        self._all_seasons: list[str] = []
        self._precomputed_features: pd.DataFrame | None = precomputed_features
        self._precomputed_dict: dict[tuple[pd.Timestamp, str, str], dict[str, Any]] = {}
        self._fixtures_by_pair: dict[tuple[str, str], list[tuple[pd.Timestamp, dict[str, Any]]]] = {}
        if precomputed_features is not None:
            self._init_precomputed(precomputed_features)

    def _init_precomputed(self, df: pd.DataFrame) -> None:
        """Index precomputed bounded features for fast lookup during CV."""
        dates = pd.to_datetime(df["date"])
        homes = df["home_team"].astype(str)
        aways = df["away_team"].astype(str)
        records = df.to_dict(orient="records")
        for d, h, a, rec in zip(dates, homes, aways, records):
            ts = pd.Timestamp(d)
            clean_rec: dict[str, Any] = {str(k): v for k, v in rec.items()}
            self._precomputed_dict[(ts, h, a)] = clean_rec
            pair = (h, a)
            if pair not in self._fixtures_by_pair:
                self._fixtures_by_pair[pair] = []
            self._fixtures_by_pair[pair].append((ts, clean_rec))
        for pair in self._fixtures_by_pair:
            self._fixtures_by_pair[pair].sort(key=lambda x: x[0])

    @property
    def model_name(self) -> str:
        return "xgboost"

    @property
    def feature_names(self) -> list[str]:
        return list(self._feature_names)

    @property
    def teams(self) -> list[str]:
        return list(self._final_elo.keys())

    def get_model_info(self) -> dict[str, Any]:
        """Return model metadata for health endpoint and status reporting."""
        return {
            "model_name": self.model_name,
            "n_teams": len(self.teams),
            "n_features": len(self.feature_names),
            "n_estimators": self.n_estimators,
            "max_depth": self.params.get("max_depth", 3),
        }

    def fit(self, matches: pd.DataFrame) -> "XGBoostPredictor":
        """Fit XGBoost classifier on historical match window."""
        matches_sorted = matches.sort_values("Date").reset_index(drop=True)
        self._fitted_matches = matches_sorted
        self._last_date = pd.Timestamp(matches_sorted["Date"].max())
        self._last_season = str(matches_sorted["Season"].iloc[-1])
        self._all_seasons = sorted(matches_sorted["Season"].unique().tolist())

        # 1. Compute window-anchored Elo features
        elo_features, final_ratings = compute_window_elo(matches_sorted)
        self._final_elo = final_ratings

        # 2. Build full feature matrix
        if self._precomputed_dict:
            rows = []
            for _, r in matches_sorted.iterrows():
                key = (pd.Timestamp(r["Date"]), str(r["HomeTeam"]), str(r["AwayTeam"]))
                base_feat = dict(self._precomputed_dict.get(key, {}))
                if key in elo_features:
                    base_feat.update(elo_features[key])
                rows.append(base_feat)
            feat_df = pd.DataFrame(rows)
        else:
            feat_df = build_feature_matrix(matches_sorted, precomputed_elo=elo_features)

        # 3. Identify feature columns vs metadata/targets
        meta_cols = {
            "home_team",
            "away_team",
            "date",
            "season",
            "home_goals",
            "away_goals",
            "result",
        }
        feature_cols = [c for c in feat_df.columns if c not in meta_cols]
        self._feature_names = feature_cols

        # 4. Prepare x_mat and y
        x_mat = feat_df[feature_cols].copy()
        for col in x_mat.columns:
            x_mat[col] = pd.to_numeric(x_mat[col], errors="coerce").astype(float)

        target_map = {"H": 0, "D": 1, "A": 2}
        y = feat_df["result"].map(target_map).to_numpy(dtype=float)

        # 5. Fit XGBoost Booster directly via DMatrix
        dtrain = xgb.DMatrix(x_mat, label=y, missing=np.nan)
        self.booster = xgb.train(self.params, dtrain, num_boost_round=self.n_estimators)
        logger.info(
            "Fitted XGBoost booster on %d matches with %d features", len(x_mat), len(feature_cols)
        )
        return self

    def predict_proba(self, home_team: str, away_team: str) -> dict[str, float]:
        """Predict outcome probabilities for a match."""
        if self.booster is None or self._fitted_matches is None:
            # Unfitted fallback: uniform
            return {"prob_home": 1.0 / 3.0, "prob_draw": 1.0 / 3.0, "prob_away": 1.0 / 3.0}

        # Handle cold-start for teams with 0 matches in window
        surviving_elos = list(self._final_elo.values())
        promoted_baseline = (
            float(np.percentile(surviving_elos, 25)) if surviving_elos else 1450.0
        )

        home_in_window = home_team in self._final_elo
        away_in_window = away_team in self._final_elo

        # Build feature vector as of next match
        next_date = (self._last_date or pd.Timestamp.now()) + pd.Timedelta(days=1)
        current_season = self._last_season or "2024-25"

        raw_features = None
        if self._fixtures_by_pair and self._last_date is not None:
            fixtures = self._fixtures_by_pair.get((home_team, away_team), [])
            for fixture_date, fixture_rec in fixtures:
                if fixture_date > self._last_date:
                    raw_features = dict(fixture_rec)
                    break

        if raw_features is None:
            raw_features = build_match_features(
                matches=self._fitted_matches,
                home_team=home_team,
                away_team=away_team,
                match_date=next_date,
                season=current_season,
                all_seasons=self._all_seasons,
            )

        # Inject Elo features
        r_home = self._final_elo.get(home_team, promoted_baseline)
        r_away = self._final_elo.get(away_team, promoted_baseline)
        raw_features["home_elo"] = r_home
        raw_features["away_elo"] = r_away
        raw_features["elo_diff"] = (r_home + 65.0) - r_away
        dr = (r_home + 65.0) - r_away
        raw_features["elo_prob_home"] = float(1.0 / (1.0 + 10.0 ** (-dr / 400.0)))

        # If team has 0 matches in window, set rolling form/stats to NaN for native routing
        if not home_in_window:
            for k in list(raw_features.keys()):
                if k.startswith("home_") and k not in {"home_elo", "home_is_newly_promoted"}:
                    raw_features[k] = np.nan
        if not away_in_window:
            for k in list(raw_features.keys()):
                if k.startswith("away_") and k not in {"away_elo", "away_is_newly_promoted"}:
                    raw_features[k] = np.nan

        # Construct single-row DataFrame matching trained feature names exactly
        row_dict: dict[str, Any] = {}
        for col in self._feature_names:
            val = raw_features.get(col, np.nan)
            row_dict[col] = val

        x_test = pd.DataFrame([row_dict], columns=self._feature_names)
        for col in x_test.columns:
            x_test[col] = pd.to_numeric(x_test[col], errors="coerce").astype(float)
        dtest = xgb.DMatrix(x_test, missing=np.nan)
        raw_probs = self.booster.predict(dtest)[0]

        # Map to H, D, A
        p_h = float(raw_probs[0])
        p_d = float(raw_probs[1])
        p_a = float(raw_probs[2])
        total = p_h + p_d + p_a
        if total > 0:
            p_h, p_d, p_a = p_h / total, p_d / total, p_a / total
        else:
            p_h, p_d, p_a = 1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0

        return {"prob_home": p_h, "prob_draw": p_d, "prob_away": p_a}
