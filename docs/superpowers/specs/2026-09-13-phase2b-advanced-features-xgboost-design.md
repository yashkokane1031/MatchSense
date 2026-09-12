# Phase 2B Design Specification: Advanced Features & XGBoost Classifier

> **Status**: Approved Design  
> **Date**: 2026-09-13  
> **Author**: Yash Kokane & Antigravity  
> **Scope**: Advanced Feature Engineering (Elo, Match Activity, xG Schema), Standalone XGBoost Predictor, Model Interface Decoupling, and Walk-Forward Benchmark Integration.

---

## 1. Executive Summary & Architecture

In Phase 1, MatchSense established the generative bivariate Poisson model (**Dixon-Coles**). In Phase 2A, a rigorous walk-forward cross-validation and evaluation harness was built and validated across 3 out-of-sample seasons (1,140 matches).

**Phase 2B** introduces the parallel discriminative machine learning model (**XGBoost**) alongside an expanded feature suite:
1. **Parallel Competing Classifier**: A standalone multi-class gradient boosted decision tree classifier ($H, D, A$) trained on tabular match features. It directly competes against Dixon-Coles and closing market odds across the exact same 1,140-match walk-forward cross-validation harness.
2. **Advanced Feature Engineering**:
   - **Custom Window-Anchored Elo Rating System**: Dynamic K-factor with margin-of-victory multiplier, home advantage ($H_{\text{elo}} = 65$), summer mean-reversion, and empirical $Q_{0.25}$ entry ratings for promoted clubs.
   - **Deterministic Rolling Match Activity**: 5-match rolling averages of shots, shots on target (SOT), shooting accuracy (SOT ratio), defensive permeability (shots conceded), and territorial pressure (corners).
   - **Isolated xG Schema**: Dedicated, separate columns for Understat expected goals (`xg_for`, `xg_against`, `xg_diff`) when cached; strictly separated from shot metrics to prevent signal contamination.
3. **Train/Serve Parity**: All 4-season training windows (both CV folds and sliding live production) anchor Elo at $R_0 = 1500$ at Window Start, eliminating historical information leakage.
4. **Clean Interface Decoupling**: `BasePredictor` decouples outcome probability forecasting (`predict_proba`, mandatory) from generative scoreline matrices (`predict_score_distribution`, optional), preserving honest modeling boundaries in the API layer.

---

## 2. Feature Engineering & Data Architecture

### 2.1 Universal Window-Anchored Elo Rating System (`ml/features/elo.py`)

#### Universal Window-Anchoring Principle
Elo is mathematically path-dependent. To guarantee exact information parity between Dixon-Coles (which has zero memory prior to its rolling 4-season window) and XGBoost, **all 4-season training windows anchor Elo to $R_0 = 1500$ at Season 1, Gameweek 1 of that window**.
- In Cross-Validation: Each of the 3 discrete folds initializes active teams to 1500 at the start of its 4-season training window.
- In Live Serving (Phase 3): Whenever the sliding 4-season window advances, Elo is re-anchored and computed forward across that same window.

#### Mathematical Formulation
For match $m$ between home team $i$ and away team $j$:
$$\hat{p}_{i} = \frac{1}{1 + 10^{(R_j - R_i - H_{\text{elo}}) / 400}}, \quad \hat{p}_{j} = 1 - \hat{p}_{i}$$
where $H_{\text{elo}} = 65$ Elo points (empirical Premier League home advantage).

Match outcome score $S_i$:
$$S_i = \begin{cases} 1.0 & \text{if Home Win} \\ 0.5 & \text{if Draw} \\ 0.0 & \text{if Away Win} \end{cases}$$

Margin-of-Victory dynamic K-factor:
$$K_{\text{effective}} = K_{\text{base}} \times M(\Delta g)$$
where $K_{\text{base}} = 24$, and the goal difference multiplier $M(\Delta g)$ follows the standard World Football Elo specification:
$$M(\Delta g) = \begin{cases} 1.0 & \text{if } |\Delta g| \le 1 \\ 1.5 & \text{if } |\Delta g| = 2 \\ \frac{11 + |\Delta g|}{8} & \text{if } |\Delta g| \ge 3 \end{cases}$$

Rating update:
$$R_i \leftarrow R_i + K_{\text{effective}} (S_i - \hat{p}_i)$$
$$R_j \leftarrow R_j + K_{\text{effective}} (S_j - \hat{p}_j)$$

#### Season Boundary Transitions & Promoted Team Entry
- **Summer Mean-Reversion**: At each season boundary within the window, surviving teams undergo mean reversion:
  $$R_{\text{new}} = 0.75 R_{\text{old}} + 0.25 \times 1500$$
- **Empirical Promoted Entry**: Newly promoted teams joining at a summer transition are assigned an empirical entry rating derived dynamically from the surviving teams' post-reversion ratings:
  $$R_{\text{promoted}} = Q_{0.25}\big(\{R_{\text{surviving}}\}\big)$$
  (the 25th percentile of surviving teams, reflecting the empirical quality gap without hardcoded magic numbers).

#### Features Output per Match
- `home_elo`: Home team pre-match Elo rating.
- `away_elo`: Away team pre-match Elo rating.
- `elo_diff`: $(R_i + H_{\text{elo}}) - R_j$ (positive favors home team).
- `elo_prob_home`: Expected score $\hat{p}_i$.

---

### 2.2 Rolling Match Activity & Shot Quality (`ml/features/match_stats.py`)

Extracted deterministically from `football-data.co.uk` match records (`HS, AS, HST, AST, HC, AC`) across a rolling window ($N=5$ matches, strictly pre-match, resetting across seasons):
- **Attacking Volume & Accuracy**:
  - `rolling_shots_for`: Mean shots taken per match over last 5 games.
  - `rolling_sot_for`: Mean shots on target taken per match over last 5 games.
  - `rolling_sot_ratio`: $\frac{\text{rolling\_sot\_for}}{\text{rolling\_shots\_for} + 1e-5}$ (shooting accuracy).
- **Defensive Permeability**:
  - `rolling_shots_against`: Mean shots allowed per match over last 5 games.
  - `rolling_sot_against`: Mean shots on target allowed over last 5 games.
- **Territorial Pressure**:
  - `rolling_corners_for`: Mean corners earned per match over last 5 games.
  - `rolling_corners_against`: Mean corners conceded per match over last 5 games.

Symmetric columns are produced for both home and away teams: `home_rolling_shots_for`, `away_rolling_shots_for`, etc.

---

### 2.3 Understat xG Schema & Separation (`ml/features/xg.py`)

- **Strict Schema Boundary**: In-repo shot metrics and Understat xG metrics NEVER share column names or fall back into each other.
- When `data/raw/understat_matches.csv` is present, the pipeline extracts:
  - `home_rolling_xg_for`, `home_rolling_xg_against`, `home_rolling_xg_diff`
  - `away_rolling_xg_for`, `away_rolling_xg_against`, `away_rolling_xg_diff`
  where `rolling_xg_diff = rolling_xg_for - rolling_xg_against`.
- When absent, these columns are populated with `np.nan` (or omitted from the active feature list). XGBoost routes them natively without error.

---

### 2.4 Feature Pipeline Orchestration (`ml/features/pipeline.py`)

1. **Precomputation of Bounded Features**: Bounded lookback features (rolling form 5 matches, H2H last 10 meetings, rolling match stats 5 matches, rest days) are precomputed once chronologically across the full dataset.
2. **Window Elo Joining**: For any active 4-season window, Elo ratings are computed and joined on `(Date, HomeTeam, AwayTeam)`.
3. **Complete Feature Vector**: ~32 numerical features per match.
4. **Early-Season & Promoted Handling**: Missing values in rolling windows are passed as `np.nan`.

---

## 3. Model Architecture & Interface Contract

### 3.1 XGBoost Classifier (`ml/models/xgboost_model.py`)

- **Target Mapping**:
  - $y \in \{0, 1, 2\}$ mapped from `FTR`: `H` $\to 0$, `D` $\to 1$, `A` $\to 2$.
- **Objective & Objective Parameters**:
  - `objective = "multi:softprob"`
  - `num_class = 3`
  - `eval_metric = "mlogloss"`
- **Conservative Regularized Hyperparameters**:
  ```python
  DEFAULT_XGB_PARAMS = {
      "n_estimators": 120,
      "max_depth": 3,              # Shallow trees to prevent overfitting on 1,520 rows
      "learning_rate": 0.04,        # Conservative shrinkage
      "subsample": 0.8,            # 80% row subsample per boosting round
      "colsample_bytree": 0.8,     # 80% feature subsample per tree
      "reg_alpha": 0.5,            # L1 regularization
      "reg_lambda": 1.0,           # L2 regularization
      "min_child_weight": 3,       # Minimum sum of instance weight in a child
      "random_state": 42,          # Determinism
      "missing": np.nan,           # Native split-routing for cold-start / early-season NaN
  }
  ```
- **Cadence & Training Pool**:
  - Refits per gameweek in walk-forward CV on the rolling 1,520-match window, exactly matching Dixon-Coles's cadence.
  - Runtime per refit: $\approx 35\text{ms}$. Total 3-fold CV runtime (114 refits): $< 10\text{ seconds}$.

### 3.2 Cold-Start & Zero-Window History Handling
If a requested club has zero matches in the active training window (e.g. newly promoted club in Gameweek 1):
- `home_elo` or `away_elo` is assigned $Q_{0.25}(\{R_{\text{surviving}}\})$.
- All rolling stats (`rolling_shots_for`, `form_points`, etc.) are assigned `np.nan`, routing through XGBoost's trained default branch.
- H2H features are set to 0.
- Rest days is set to `np.nan`.
- `PredictionService` validates team names against `set(model.teams) | KNOWN_PL_TEAMS` (returning 404 for unrecognized clubs while permitting recognized promoted clubs).

---

### 3.3 `BasePredictor` Interface Decoupling (`ml/models/base.py`)

```python
class BasePredictor(ABC):
    @abstractmethod
    def fit(self, matches: pd.DataFrame) -> "BasePredictor":
        """Fit the model on historical match data."""
        ...

    @abstractmethod
    def predict_proba(self, home_team: str, away_team: str) -> dict[str, float]:
        """Predict outcome probabilities for a match.
        Mandatory for ALL models. Returns {'prob_home': ..., 'prob_draw': ..., 'prob_away': ...}.
        """
        ...

    def predict_score_distribution(
        self, home_team: str, away_team: str, max_goals: int = 8
    ) -> np.ndarray | None:
        """Predict joint score probability distribution.
        Optional. Returns None for discriminative classifiers.
        """
        return None

    def predict_most_likely_score(
        self, home_team: str, away_team: str
    ) -> tuple[int, int] | None:
        """Predict single most likely scoreline. Optional, defaults to None."""
        dist = self.predict_score_distribution(home_team, away_team)
        if dist is None:
            return None
        idx = np.unravel_index(dist.argmax(), dist.shape)
        return int(idx[0]), int(idx[1])

    def get_team_strengths(self) -> dict[str, dict[str, float]] | None:
        """Return attack/defense strengths.
        Optional. Returns None for models without alpha/beta parameter decomposition.
        """
        return None

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Human-readable model name."""
        ...
```

### 3.4 API Layer & Route Behavior
1. **Response Schema (`backend/models/schemas.py`)**:
   - `predicted_score: Optional[PredictedScore] = None`
   - `score_distribution: Optional[list[list[float]]] = None`
2. **Strengths Endpoint (`backend/api/routes/predictions.py`)**:
   - If `model.get_team_strengths() is None`, returns HTTP 404:
     `{"detail": "Active model 'xgboost' does not provide attack/defense parameter decompositions."}`
3. **Health Endpoint (`GET /api/v1/health`)**:
   - Dynamically reports `len(model.feature_names)` as `n_features`, never a hardcoded constant.
4. **Live Elo Caching**:
   - In `backend/services/prediction.py`, Elo is computed once on startup / model load and cached in memory for $O(1)$ lookups.

---

## 4. Walk-Forward CV & Multi-Model Evaluation

### 4.1 Walk-Forward Cross-Validation (`ml/evaluation/walk_forward.py`)
- Seamlessly evaluates `XGBoostPredictor` via `run_walk_forward_cv(model_factory=lambda: XGBoostPredictor(), ...)` across the 3 out-of-sample seasons: `2023-24`, `2024-25`, `2025-26` (1,140 total test matches).
- Evaluates against the exact same 4 baselines: Naive Home, Uniform, Historic, and Closing Market Implied Probabilities.

### 4.2 Multi-Model Head-to-Head Comparison (`ml/evaluation/report.py` & `scripts/evaluate.py`)
CLI option: `python scripts/evaluate.py --model {dixon_coles,xgboost,all}` (defaults to `all`).

When `--model all` is executed:
1. **Model vs. Market Scorecard**:
   - Reported per model, highlighting $\Delta\text{RPS} = \text{Model} - \text{Market}$ ($+$ means market is better).
2. **Direct Model vs. Model Comparison (XGBoost vs. Dixon-Coles)**:
   - Evaluates $\Delta\text{RPS} = \text{RPS}_{\text{XGBoost}} - \text{RPS}_{\text{DixonColes}}$.
   - **Mandated Table Header & Caption**:
     `diff_RPS (XGB - DC) [negative = XGBoost better]`
   - Includes an explicit `Better` column (`XGBoost`, `Dixon-Coles`, or `Tied / Not Significant`) alongside the Wilcoxon signed-rank $p$-value (per-fold primary + pooled caveat).
   - McNemar test comparing binary prediction accuracy between XGBoost and Dixon-Coles.
3. **Calibration Breakdown**:
   - Full 10-bin reliability tables for Home, Draw, Away outcomes for both models, including match counts $|B_m|$ per bin.
4. **Financial Simulation**:
   - Flat Staking and Quarter-Kelly simulation against closing odds for both models under identical batch constraints (5% bet cap, 25% gameweek exposure cap).

---

## 5. Verification Plan & Sanity Gates

### 5.1 Automated Sanity Gates
Before signing off on Phase 2B, the following 5 gates must be satisfied:
- **Gate 1 (Mathematical Invariants)**:
  For all test matches, $\sum_{c \in \{H, D, A\}} P(c) = 1.0 \pm 10^{-5}$ and $P(c) \ge 0$.
- **Gate 2 (RPS Sanity Range)**:
  Pooled XGBoost RPS across 1,140 test matches must fall in $[0.180, 0.240]$ (consistent with Dixon-Coles Phase 2A gate).
- **Gate 3 (Cold-Start Safety)**:
  Unit tests verify that `predict_proba()` on an unknown or newly promoted team with zero prior matches in the window succeeds using $Q_{0.25}$ Elo and `np.nan` routing.
- **Gate 4 (Execution Budget)**:
  3-fold walk-forward cross-validation for XGBoost completes in $< 30$ seconds.
- **Gate 5 (Regression Guard)**:
  All 81 existing unit, property, and integration tests continue to pass without regression.

### 5.2 Test Coverage Strategy
- `tests/unit/test_elo.py`: Tests Elo mathematical formulas, margin of victory multipliers, season boundary reversion, $Q_{0.25}$ promoted entry, and window-anchoring.
- `tests/unit/test_match_stats.py`: Tests rolling shots/SOT/corners, temporal lookback isolation, and season resets.
- `tests/unit/test_xgboost_model.py`: Tests target encoding, training flow, probability output, feature importance, and cold-start fallback.
- `tests/integration/test_multi_model_cv.py`: Tests full walk-forward CV execution comparing Dixon-Coles and XGBoost.
- `tests/unit/test_api.py`: Tests updated schema, nullable score distributions, 404 for strengths on XGBoost, and dynamic feature count.
