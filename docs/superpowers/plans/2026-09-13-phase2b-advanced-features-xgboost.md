# Phase 2B Implementation Plan: Advanced Features & XGBoost Classifier

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Phase 2B advanced feature pipeline (window-anchored Elo, rolling match stats, separated xG schema), decouple `BasePredictor`, build the regularized multi-class `XGBoostPredictor` with zero-window cold-start fallback, update API endpoints, and expand the walk-forward evaluation harness to benchmark XGBoost vs Dixon-Coles vs market closing lines.

**Architecture:** A pure window-anchored Elo rating engine and rolling shot/corner extractor feed into `FeaturePipeline`. `BasePredictor` decouples outcome probability forecasting (`predict_proba`) from scoreline generation. `XGBoostPredictor` implements `BasePredictor` wrapping `xgboost.XGBClassifier(objective="multi:softprob")` with conservative regularized hyperparameters and native NaN routing. The walk-forward CV harness evaluates both models across 1,140 matches, reporting direct $\Delta\text{RPS}$ with unambiguous sign labeling and sanity gates.

**Tech Stack:** Python 3.12, `uv`, `xgboost>=2.0`, `scipy`, `pandas`, `fastapi`, `pydantic`, `pytest`.

**Spec:** [docs/superpowers/specs/2026-09-13-phase2b-advanced-features-xgboost-design.md](file:///d:/Yash%20Kokane/Projects/MatchSense/docs/superpowers/specs/2026-09-13-phase2b-advanced-features-xgboost-design.md)

---

## Global Constraints

- **Elo Window Anchoring**: Every 4-season training window anchors Elo to $R_0 = 1500$ at Season 1, GW1 of that window. Reversion at summer break: $R_{\text{new}} = 0.75 R_{\text{old}} + 0.25 \times 1500$. Promoted entry: $Q_{0.25}(\{R_{\text{surviving}}\})$.
- **Strict Schema Boundary**: In-repo shot metrics and Understat xG metrics NEVER share column names or fall back into each other.
- **`BasePredictor` Decoupling**: `predict_proba` is mandatory. `predict_score_distribution` and `get_team_strengths` return `None` by default.
- **Cold-Start vs Invalid**: Known clubs with zero matches in the window succeed via $Q_{0.25}$ Elo and `np.nan` rolling stats; fake club names return HTTP 404.
- **Unambiguous Direction**: Direct model comparison defines $\Delta\text{RPS} = \text{XGBoost} - \text{DixonColes}$, with explicit header `diff_RPS (XGB - DC) [negative = XGBoost better]` and an explicit `Better` column.
- **Sanity Gate 2 Range**: Pooled XGBoost RPS $\in [0.180, 0.240]$.

---

## Tasks

### Task 1: Environment & Dependency Setup

**Files:**
- Modify: `pyproject.toml`
- Test: CLI verification via `uv sync` and Python import check

**Interfaces:**
- Produces: `xgboost>=2.0` available in the active environment

- [ ] **Step 1: Update pyproject.toml to declare xgboost**

Add `"xgboost>=2.0"` to the dependencies array in `pyproject.toml`.

- [ ] **Step 2: Run uv sync to install xgboost**

Run: `uv sync`
Expected: Resolves and installs `xgboost` into `.venv`.

- [ ] **Step 3: Verify import and version**

Run: `uv run python -c "import xgboost; print(xgboost.__version__)"`
Expected: Prints version `2.x.x` without error.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "build: add xgboost dependency for Phase 2B"
```

---

### Task 2: Window-Anchored Elo Rating System (`ml/features/elo.py`)

**Files:**
- Create: `ml/features/elo.py`
- Test: `tests/unit/test_elo.py`

**Interfaces:**
- Consumes: Historical matches DataFrame (`Date`, `Season`, `HomeTeam`, `AwayTeam`, `FTHG`, `FTAG`, `FTR`).
- Produces:
  - `EloEngine(k_base=24.0, home_advantage=65.0, reversion_weight=0.75)`
  - `compute_window_elo(matches: pd.DataFrame, window_seasons: int = 4) -> tuple[dict[tuple[pd.Timestamp, str, str], dict[str, float]], dict[str, float]]`
  - Output features: `home_elo`, `away_elo`, `elo_diff`, `elo_prob_home`

- [ ] **Step 1: Write unit tests for Elo formulas and window anchoring**

Create `tests/unit/test_elo.py`:
```python
import numpy as np
import pandas as pd
import pytest

from ml.features.elo import EloEngine, compute_window_elo


def test_elo_win_probability_formula():
    engine = EloEngine(home_advantage=65.0)
    # Equal ratings: home team has advantage of 65 points
    p_home, p_away = engine.expected_probabilities(1500.0, 1500.0)
    assert p_home > 0.50
    assert p_home + p_away == pytest.approx(1.0)

    # 400 point difference favoring away team
    p_home_underdog, p_away_favorite = engine.expected_probabilities(1100.0, 1500.0)
    assert p_away_favorite > p_home_underdog


def test_margin_of_victory_multiplier():
    engine = EloEngine()
    assert engine.margin_multiplier(1) == 1.0
    assert engine.margin_multiplier(2) == 1.5
    assert engine.margin_multiplier(3) == pytest.approx(14.0 / 8.0)
    assert engine.margin_multiplier(4) == pytest.approx(15.0 / 8.0)


def test_summer_mean_reversion_and_promoted_entry():
    engine = EloEngine(reversion_weight=0.75)
    ratings = {
        "Arsenal": 1700.0,
        "Chelsea": 1600.0,
        "Everton": 1400.0,
        "Wolves": 1300.0,
    }
    reverted = engine.apply_season_transition(ratings, promoted_teams=["Luton"])
    # 0.75 * 1700 + 0.25 * 1500 = 1275 + 375 = 1650
    assert reverted["Arsenal"] == pytest.approx(1650.0)
    # Promoted team enters at 25th percentile of surviving post-reversion ratings
    surviving_ratings = [reverted[t] for t in ratings]
    expected_q25 = float(np.percentile(surviving_ratings, 25))
    assert reverted["Luton"] == pytest.approx(expected_q25)


def test_compute_window_elo_anchors_at_1500():
    matches = pd.DataFrame([
        {"Date": pd.Timestamp("2020-09-12"), "Season": "2020-21", "HomeTeam": "Arsenal", "AwayTeam": "Fulham", "FTHG": 3, "FTAG": 0, "FTR": "H"},
        {"Date": pd.Timestamp("2020-09-19"), "Season": "2020-21", "HomeTeam": "Arsenal", "AwayTeam": "West Ham", "FTHG": 2, "FTAG": 1, "FTR": "H"},
        {"Date": pd.Timestamp("2021-08-14"), "Season": "2021-22", "HomeTeam": "Arsenal", "AwayTeam": "Chelsea", "FTHG": 0, "FTAG": 2, "FTR": "A"},
    ])
    match_features, final_ratings = compute_window_elo(matches)
    # First match should have Arsenal and Fulham at 1500.0
    key1 = (pd.Timestamp("2020-09-12"), "Arsenal", "Fulham")
    assert match_features[key1]["home_elo"] == 1500.0
    assert match_features[key1]["away_elo"] == 1500.0
    assert match_features[key1]["elo_diff"] == 65.0  # (1500 + 65) - 1500
    # Arsenal won, rating increased for match 2
    key2 = (pd.Timestamp("2020-09-19"), "Arsenal", "West Ham")
    assert match_features[key2]["home_elo"] > 1500.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_elo.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'ml.features.elo'`

- [ ] **Step 3: Implement ml/features/elo.py**

Create `ml/features/elo.py`:
```python
"""Window-anchored Elo rating engine with margin-of-victory and empirical promoted entry."""

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
        """Compute expected outcome score probabilities for home and away teams."""
        dr = (r_home + self.home_advantage) - r_away
        p_home = 1.0 / (1.0 + 10.0 ** (-dr / 400.0))
        return float(p_home), float(1.0 - p_home)

    def margin_multiplier(self, goal_diff: int) -> float:
        """Dynamic multiplier based on margin of victory."""
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
        """Apply inter-season mean-reversion and empirical Q0.25 promoted entry."""
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

    Returns:
        tuple of (match_features_dict, final_team_ratings).
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
            # Revert surviving teams
            surviving = set(ratings.keys())
            # Promoted teams in the new season
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_elo.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add ml/features/elo.py tests/unit/test_elo.py
git commit -m "feat(features): implement window-anchored Elo rating engine"
```

---

### Task 3: Rolling Match Activity & Shot Quality (`ml/features/match_stats.py`)

**Files:**
- Create: `ml/features/match_stats.py`
- Test: `tests/unit/test_match_stats.py`

**Interfaces:**
- Consumes: Historical matches DataFrame (`Date`, `Season`, `HomeTeam`, `AwayTeam`, `HS`, `AS`, `HST`, `AST`, `HC`, `AC`).
- Produces: `compute_match_stats_features(matches: pd.DataFrame, team: str, match_date: pd.Timestamp, season: str, window: int = 5) -> dict[str, float | None]`
- Output features: `rolling_shots_for`, `rolling_shots_against`, `rolling_sot_for`, `rolling_sot_against`, `rolling_sot_ratio`, `rolling_corners_for`, `rolling_corners_against`.

- [ ] **Step 1: Write unit tests for match activity and shot metrics**

Create `tests/unit/test_match_stats.py`:
```python
import numpy as np
import pandas as pd
import pytest

from ml.features.match_stats import compute_match_stats_features


@pytest.fixture
def sample_match_data():
    return pd.DataFrame([
        {"Date": pd.Timestamp("2024-08-17"), "Season": "2024-25", "HomeTeam": "Arsenal", "AwayTeam": "Wolves", "HS": 18, "AS": 9, "HST": 6, "AST": 3, "HC": 8, "AC": 2},
        {"Date": pd.Timestamp("2024-08-24"), "Season": "2024-25", "HomeTeam": "Aston Villa", "AwayTeam": "Arsenal", "HS": 11, "AS": 14, "HST": 4, "AST": 5, "HC": 3, "AC": 6},
        {"Date": pd.Timestamp("2024-08-31"), "Season": "2024-25", "HomeTeam": "Arsenal", "AwayTeam": "Brighton", "HS": 12, "AS": 16, "HST": 4, "AST": 5, "HC": 4, "AC": 7},
    ])


def test_match_stats_returns_nan_for_zero_history(sample_match_data):
    stats = compute_match_stats_features(sample_match_data, "Arsenal", pd.Timestamp("2024-08-17"), "2024-25")
    assert stats["rolling_shots_for"] is None
    assert stats["rolling_sot_for"] is None
    assert stats["rolling_sot_ratio"] is None


def test_match_stats_averages_over_prior_matches(sample_match_data):
    stats = compute_match_stats_features(sample_match_data, "Arsenal", pd.Timestamp("2024-08-31"), "2024-25", window=5)
    # Arsenal shots: 18 (home vs Wolves), 14 (away vs Villa) -> mean = 16.0
    assert stats["rolling_shots_for"] == pytest.approx(16.0)
    # Arsenal SOT: 6, 5 -> mean = 5.5
    assert stats["rolling_sot_for"] == pytest.approx(5.5)
    # SOT ratio: 5.5 / 16.0 = 0.34375
    assert stats["rolling_sot_ratio"] == pytest.approx(5.5 / 16.0, abs=1e-3)
    # Corners: 8, 6 -> mean = 7.0
    assert stats["rolling_corners_for"] == pytest.approx(7.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_match_stats.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'ml.features.match_stats'`

- [ ] **Step 3: Implement ml/features/match_stats.py**

Create `ml/features/match_stats.py`:
```python
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

    Returns:
        dict mapping metric names to rolling average values (or None if no history).
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

    for _, row in recent.iterrows():
        is_home = row["HomeTeam"] == team
        sf = row["HS"] if is_home else row["AS"]
        sa = row["AS"] if is_home else row["HS"]
        sotf = row["HST"] if is_home else row["AST"]
        sota = row["AST"] if is_home else row["HST"]
        cf = row["HC"] if is_home else row["AC"]
        ca = row["AC"] if is_home else row["HC"]

        if pd.notna(sf):
            shots_for_list.append(float(sf))
        if pd.notna(sa):
            shots_against_list.append(float(sa))
        if pd.notna(sotf):
            sot_for_list.append(float(sotf))
        if pd.notna(sota):
            sot_against_list.append(float(sota))
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_match_stats.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add ml/features/match_stats.py tests/unit/test_match_stats.py
git commit -m "feat(features): add rolling shot and match activity feature extractor"
```

---

### Task 4: Separated Understat xG Schema & Feature Pipeline Integration (`ml/features/xg.py`, `ml/features/pipeline.py`)

**Files:**
- Create: `ml/features/xg.py`
- Modify: `ml/features/pipeline.py`
- Modify: `tests/unit/test_features.py`

**Interfaces:**
- Produces:
  - `compute_rolling_xg(understat_df: pd.DataFrame | None, team: str, match_date: pd.Timestamp, season: str, window: int = 5) -> dict[str, float | None]`
  - `build_match_features(...)` updated with `home_` and `away_` match stats and optional xG metrics.
  - `build_feature_matrix(...)` updated with shot metrics and window-anchored Elo joining.

- [ ] **Step 1: Add unit tests to tests/unit/test_features.py for new match stats and xG schema isolation**

In `tests/unit/test_features.py`, append tests to `TestFeaturePipeline`:
1. `test_build_match_features_includes_rolling_shots_and_corners`: asserts that `home_rolling_shots_for`, `away_rolling_shots_for`, and corner metrics are included in the returned dictionary without modifying or breaking existing form/H2H keys.
2. `test_xg_schema_isolation`: asserts that `home_rolling_xg_for/against/diff` are `None` when Understat data is absent, and that they never share names or mingle with `rolling_sot_for`.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_features.py::TestFeaturePipeline::test_build_match_features_includes_rolling_shots_and_corners -v`
Expected: FAIL due to missing shot/corner keys.

- [ ] **Step 3: Implement ml/features/xg.py**

Create `ml/features/xg.py`:
```python
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

    Returns separate columns: rolling_xg_for, rolling_xg_against, rolling_xg_diff.
    Returns None for all if understat_matches is None or history is empty.
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
```

- [ ] **Step 4: Update ml/features/pipeline.py to orchestrate match stats and Elo**

Update `ml/features/pipeline.py` to:
1. Import `compute_match_stats_features` from `ml.features.match_stats`.
2. Import `compute_rolling_xg` from `ml.features.xg`.
3. In `build_match_features`, append `home_rolling_shots_for`, `away_rolling_shots_for`, corners, etc.
4. Support passing precomputed Elo features or dynamically computing them.

- [ ] **Step 5: Run tests to verify all feature tests pass**

Run: `uv run pytest tests/unit/test_features.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add ml/features/xg.py ml/features/pipeline.py tests/unit/test_features.py
git commit -m "feat(features): integrate match stats and isolated xG schema into pipeline"
```

---

### Task 5: `BasePredictor` Decoupling & XGBoost Classifier (`ml/models/base.py`, `ml/models/xgboost_model.py`)

**Files:**
- Modify: `ml/models/base.py`
- Create: `ml/models/xgboost_model.py`
- Test: `tests/unit/test_xgboost_model.py`

**Interfaces:**
- Consumes: Matches DataFrame, `FeaturePipeline`, `EloEngine`.
- Produces: `XGBoostPredictor(BasePredictor)`:
  - `fit(matches: pd.DataFrame)`
  - `predict_proba(home_team: str, away_team: str) -> dict[str, float]`
  - `predict_score_distribution(...) -> None`
  - `get_team_strengths() -> None`
  - `feature_names: list[str]`

- [ ] **Step 1: Write unit tests for BasePredictor decoupling and XGBoostPredictor**

Create `tests/unit/test_xgboost_model.py`:
```python
import numpy as np
import pandas as pd
import pytest

from ml.models.base import BasePredictor
from ml.models.xgboost_model import XGBoostPredictor


@pytest.fixture
def mock_training_data():
    np.random.seed(42)
    teams = ["Arsenal", "Chelsea", "Liverpool", "Man City"]
    records = []
    dates = pd.date_range("2023-08-11", periods=60, freq="7D")
    for i, d in enumerate(dates):
        h, a = np.random.choice(teams, size=2, replace=False)
        fthg = np.random.poisson(1.5)
        ftag = np.random.poisson(1.1)
        ftr = "H" if fthg > ftag else ("D" if fthg == ftag else "A")
        records.append({
            "Date": d,
            "Season": "2023-24",
            "HomeTeam": h,
            "AwayTeam": a,
            "FTHG": fthg,
            "FTAG": ftag,
            "FTR": ftr,
            "HS": fthg + 8,
            "AS": ftag + 6,
            "HST": fthg + 3,
            "AST": ftag + 2,
            "HC": 5,
            "AC": 4,
        })
    return pd.DataFrame(records)


def test_xgboost_predictor_satisfies_base_interface():
    model = XGBoostPredictor()
    assert isinstance(model, BasePredictor)
    assert model.model_name == "xgboost"
    assert model.predict_score_distribution("Arsenal", "Chelsea") is None
    assert model.get_team_strengths() is None


def test_xgboost_fit_and_predict_proba(mock_training_data):
    model = XGBoostPredictor()
    model.fit(mock_training_data)
    assert len(model.feature_names) > 10

    probs = model.predict_proba("Arsenal", "Chelsea")
    assert "prob_home" in probs
    assert "prob_draw" in probs
    assert "prob_away" in probs
    assert probs["prob_home"] + probs["prob_draw"] + probs["prob_away"] == pytest.approx(1.0, abs=1e-4)


def test_xgboost_cold_start_fallback_for_promoted_team(mock_training_data):
    model = XGBoostPredictor()
    model.fit(mock_training_data)
    # "Luton" has zero matches in mock_training_data
    probs = model.predict_proba("Arsenal", "Luton")
    assert probs["prob_home"] > 0
    assert probs["prob_away"] > 0
    assert probs["prob_home"] + probs["prob_draw"] + probs["prob_away"] == pytest.approx(1.0, abs=1e-4)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_xgboost_model.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'ml.models.xgboost_model'`

- [ ] **Step 3: Update ml/models/base.py to decouple scoreline & strengths**

Make `predict_score_distribution`, `predict_most_likely_score`, and `get_team_strengths` concrete methods returning `None` by default on `BasePredictor`.

- [ ] **Step 4: Implement ml/models/xgboost_model.py**

Create `ml/models/xgboost_model.py`:
- Target encoding: `H` $\to 0$, `D` $\to 1$, `A` $\to 2$.
- Feature construction per match with Elo, match stats, form, H2H, days rest.
- `DEFAULT_XGB_PARAMS`: `max_depth=3`, `learning_rate=0.04`, `n_estimators=120`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_alpha=0.5`, `reg_lambda=1.0`, `missing=np.nan`.
- Promoted club cold start fallback: $Q_{0.25}$ Elo, `np.nan` for rolling stats, 0 for H2H.

- [ ] **Step 5: Run tests to verify it passes**

Run: `uv run pytest tests/unit/test_xgboost_model.py -v`
Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add ml/models/base.py ml/models/xgboost_model.py tests/unit/test_xgboost_model.py
git commit -m "feat(models): implement regularized XGBoostPredictor with cold-start safety"
```

---

### Task 6: API Layer & Route Updates (`backend/models/schemas.py`, `backend/services/prediction.py`, `tests/unit/test_api.py`)

**Files:**
- Modify: `backend/models/schemas.py`
- Modify: `backend/services/prediction.py`
- Modify: `backend/api/routes/predictions.py`
- Test: `tests/unit/test_api.py`

**Interfaces:**
- Produces:
  - `PredictionResponse` with nullable `predicted_score` and `score_distribution`.
  - `GET /api/v1/teams/{team}/strengths` returns 404 when model doesn't support $\{\alpha, \beta\}$.
  - Cold-start handling for real promoted teams vs 404 for invalid teams.
  - Dynamic `n_features` in health endpoint.

- [ ] **Step 1: Write unit tests for API route behavior with XGBoost**

In `tests/unit/test_api.py`, add tests for:
1. Nullable `predicted_score` and `score_distribution` when an `XGBoostPredictor` is active.
2. `GET /api/v1/teams/Arsenal/strengths` returns 404 when `XGBoostPredictor` is active.
3. Distinguishing real promoted team (`Luton`) which succeeds via fallback vs fake team (`Fictional FC`) which returns 404.
4. `GET /api/v1/health` dynamically reports `n_features`.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_api.py -v`
Expected: FAIL.

- [ ] **Step 3: Update schemas and prediction service**

1. In `backend/models/schemas.py`, set:
   ```python
   predicted_score: PredictedScore | None = None
   score_distribution: list[list[float]] | None = None
   ```
2. In `backend/services/prediction.py`:
   - Safely populate `predicted_score` and `score_distribution` if not None.
   - Cache window-anchored Elo at startup / load.
3. In `backend/api/routes/predictions.py`:
   - Check `get_team_strengths()`. If None, raise `HTTPException(status_code=404, detail="Active model does not provide parameter strengths")`.
4. In `backend/api/routes/health.py`:
   - Return dynamic `n_features`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_api.py -v`
Expected: ALL API tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/models/schemas.py backend/services/prediction.py backend/api/routes/ tests/unit/test_api.py
git commit -m "feat(api): support optional score distributions and dynamic feature counts for XGBoost"
```

---

### Task 7: Walk-Forward CV & Multi-Model Evaluation Report (`ml/evaluation/walk_forward.py`, `ml/evaluation/report.py`, `scripts/evaluate.py`)

**Files:**
- Modify: `ml/evaluation/walk_forward.py`
- Modify: `ml/evaluation/report.py`
- Modify: `scripts/evaluate.py`
- Modify: `tests/unit/test_walk_forward.py`
- Create: `tests/integration/test_multi_model_cv.py`

**Interfaces:**
- Produces:
  - `python scripts/evaluate.py --model all`
  - Comparative Markdown report `reports/model_comparison_evaluation.md` with:
    - Model vs Market table.
    - Model vs Model table with mandated header `diff_RPS (XGB - DC) [negative = XGBoost better]` and explicit `Better` column.
    - Automated Sanity Gates 1 to 5 validation.

- [ ] **Step 1: Verify test_walk_forward.py generalizes to XGBoost**

Add `test_walk_forward_execution_with_xgboost(synthetic_seasons_data)` to `tests/unit/test_walk_forward.py`, asserting that `run_walk_forward_cv` executes identically with `model_factory=lambda: XGBoostPredictor()` without model-specific leakage or crashes.

Run: `uv run pytest tests/unit/test_walk_forward.py -v`
Expected: Both tests pass (Dixon-Coles and XGBoost).

- [ ] **Step 2: Write integration test for multi-model walk-forward CV**

Create `tests/integration/test_multi_model_cv.py`:
```python
import pandas as pd
import pytest

from ml.evaluation.walk_forward import run_walk_forward_cv
from ml.models.dixon_coles import DixonColesPredictor
from ml.models.xgboost_model import XGBoostPredictor


def test_walk_forward_cv_runs_both_models():
    # Load raw historical data
    matches = pd.read_csv("data/raw/E0_2223.csv")  # synthetic or sample slice
    # Verify both models run through walk_forward_cv without exception
```

- [ ] **Step 2: Update report.py and scripts/evaluate.py**

1. In `ml/evaluation/report.py`, add `generate_model_comparison_report(dc_report, xgb_report)`.
2. Ensure the direct comparison table header is strictly:
   `diff_RPS (XGB - DC) [negative = XGBoost better]`
   and includes a `Better` column.
3. In `scripts/evaluate.py`, add `--model {dixon_coles,xgboost,all}` argument (defaulting to `all`).
4. Validate Gates 1–5 in `scripts/evaluate.py`.

- [ ] **Step 3: Run evaluation benchmark**

Run: `uv run python scripts/evaluate.py --model all`
Expected:
- Runs Dixon-Coles across 3 folds (1,140 matches).
- Runs XGBoost across 3 folds (1,140 matches).
- Evaluates Gates 1–5.
- Writes `reports/model_comparison_evaluation.md`.

- [ ] **Step 4: Run complete test suite and linters**

Run:
```bash
uv run pytest
uv run ruff check .
uv run mypy backend/ ml/
```
Expected: 0 errors across all checks.

- [ ] **Step 5: Commit**

```bash
git add ml/evaluation/walk_forward.py ml/evaluation/report.py scripts/evaluate.py tests/integration/test_multi_model_cv.py reports/model_comparison_evaluation.md
git commit -m "feat(eval): add multi-model walk-forward comparison and benchmark report"
```
