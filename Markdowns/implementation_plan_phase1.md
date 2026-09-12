# MatchSense — Phase 1 Implementation Plan

> **Scope**: Data pipeline → Dixon-Coles model → FastAPI → Basic tests → Docker Compose
> **Duration**: Weeks 1-3
> **Milestone**: A working, demoable Premier League match predictor

---

## Proposed Changes

### 1. Project Scaffolding

Set up the monorepo structure, `uv` project, and Docker Compose for local development.

#### [NEW] `matchsense/pyproject.toml`
Root project config for `uv`. Defines Python 3.12+, dependency groups:
- **core**: `pandas`, `numpy`, `scipy`, `sqlalchemy[asyncio]`, `alembic`, `psycopg2-binary`
- **ml**: `statsmodels`, `xgboost` (placeholder for Phase 2)
- **api**: `fastapi`, `uvicorn[standard]`, `pydantic>=2.0`
- **dev**: `pytest`, `pytest-cov`, `hypothesis`, `pandera`, `ruff`, `mypy`

#### [NEW] `matchsense/docker-compose.yml`
Services:
- `db`: PostgreSQL 16 (port 5432, volume-mounted data)
- `api`: FastAPI app (port 8000, depends on `db`)
- `.env.example` with `DATABASE_URL`, `FOOTBALL_DATA_API_KEY` placeholders

#### [NEW] `matchsense/.gitignore`
Standard Python gitignore + `data/raw/`, `data/processed/`, `.env`, `mlruns/`

#### [NEW] Directory skeleton
```
matchsense/
├── backend/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app factory
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── predictions.py
│   │   │   └── health.py
│   │   └── dependencies.py  # DB session, model loader
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Pydantic Settings
│   │   └── database.py      # SQLAlchemy engine + session
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # SQLAlchemy ORM models
│   └── services/
│       ├── __init__.py
│       └── prediction.py    # Prediction service (calls ML models)
├── ml/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── ingestion.py     # CSV downloader + parser
│   │   ├── schemas.py       # Pandera schemas
│   │   └── loader.py        # DB read/write helpers
│   ├── features/
│   │   ├── __init__.py
│   │   ├── form.py          # Recent form features
│   │   ├── h2h.py           # Head-to-head features
│   │   └── pipeline.py      # Feature orchestrator
│   ├── models/
│   │   ├── __init__.py
│   │   ├── dixon_coles.py   # Dixon-Coles implementation
│   │   └── base.py          # Abstract model interface
│   └── evaluation/
│       ├── __init__.py
│       └── metrics.py       # RPS, log-loss stubs
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_ingestion.py
│   │   ├── test_features.py
│   │   ├── test_dixon_coles.py
│   │   └── test_api.py
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_pipeline.py
│   ├── property/
│   │   ├── __init__.py
│   │   └── test_poisson_properties.py
│   └── conftest.py          # Shared fixtures
├── data/                    # gitignored
│   ├── raw/
│   └── processed/
├── scripts/
│   └── seed_data.py         # One-time data download script
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── README.md
└── .gitignore
```

---

### 2. Data Ingestion Pipeline

Download and parse football-data.co.uk CSVs into normalized PostgreSQL tables.

#### [NEW] `ml/data/ingestion.py`

**Data source**: `https://www.football-data.co.uk/mmz4281/{season}/E0.csv`
- Seasons: `2223`, `2324`, `2425`, `2526` (4 seasons)
- Each season CSV identified by two-digit year pairs (e.g., `2425` = 2024/25)

> [!IMPORTANT]
> **Why 4 seasons, not 7**: Promotion/relegation means 7 seasons produces ~45-55 distinct teams, not 20. Teams present for only 1 season get very few matches, yielding noisy MLE estimates for attack/defense strengths that look confident but aren't. The time-decay weighting (ξ ≈ 0.005/day) already discounts seasons 5-7 to near-zero influence anyway, so the information loss is negligible. 4 seasons gives ~28-30 distinct teams with reasonable sample sizes for all of them. Expanding to more history is a documented Phase 2 option if paired with regularization or hierarchical priors.

**Columns to extract** (verified from football-data.co.uk notes):

| Column | Meaning | Use |
|---|---|---|
| `Date` | Match date (dd/mm/yy) | Temporal ordering, time-decay |
| `HomeTeam` | Home team name | Team identification |
| `AwayTeam` | Away team name | Team identification |
| `FTHG` | Full-time home goals | Target variable |
| `FTAG` | Full-time away goals | Target variable |
| `FTR` | Full-time result (H/D/A) | Classification target |
| `HTHG/HTAG` | Half-time goals | Feature (momentum) |
| `HS/AS` | Shots | Feature |
| `HST/AST` | Shots on target | Feature |
| `HC/AC` | Corners | Feature |
| `HF/AF` | Fouls | Feature |
| `HY/AY` | Yellow cards | Feature |
| `HR/AR` | Red cards | Feature |
| `B365H/B365D/B365A` | Bet365 odds | Bookmaker baseline |
| `AvgH/AvgD/AvgA` | Market average odds | Bookmaker baseline (primary) |

**Logic**:
1. Download CSVs for configured seasons (with retry + caching)
2. Normalize team names (handle inconsistencies across seasons, e.g., "Man United" vs "Manchester Utd")
3. Parse dates (handle both `dd/mm/yy` and `dd/mm/yyyy` formats — CSVs are inconsistent)
4. Compute bookmaker implied probabilities: `prob = (1/odds) / sum(1/all_odds)` (removes overround)
5. Validate with Pandera schemas
6. Insert into PostgreSQL `matches` table via SQLAlchemy

#### [NEW] `ml/data/schemas.py`
Pandera `DataFrameSchema` for raw match data:
- `Date`: datetime, not null, monotonically increasing within season
- `HomeTeam` / `AwayTeam`: string, not null, must be in known teams set
- `FTHG` / `FTAG`: int >= 0
- `FTR`: category in {H, D, A}
- Goals consistency check: `FTR == H` iff `FTHG > FTAG`, etc.
- Odds: float > 1.0 (decimal odds), not null for the columns we use

#### [NEW] `backend/models/schemas.py`
SQLAlchemy ORM models:

```python
class Match(Base):
    id: int (PK)
    season: str           # e.g., "2024-25"
    date: date
    matchday: int         # optional, derived from ordering
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    result: str           # H/D/A
    home_shots: int | None
    away_shots: int | None
    home_shots_on_target: int | None
    away_shots_on_target: int | None
    home_corners: int | None
    away_corners: int | None
    home_fouls: int | None
    away_fouls: int | None
    home_yellows: int | None
    away_yellows: int | None
    home_reds: int | None
    away_reds: int | None
    avg_odds_home: float | None
    avg_odds_draw: float | None
    avg_odds_away: float | None

class Team(Base):
    id: int (PK)
    name: str (unique)
    canonical_name: str   # normalized name for matching
    
class Prediction(Base):
    id: int (PK)
    match_id: int (FK → Match, nullable for hypothetical)
    model_name: str       # "dixon_coles" or "xgboost"
    home_team: str
    away_team: str
    prob_home: float
    prob_draw: float
    prob_away: float
    predicted_score_home: int  # most likely score
    predicted_score_away: int
    score_distribution: JSON   # full probability matrix
    created_at: datetime
```

#### [NEW] `scripts/seed_data.py`
CLI script (callable via `uv run python scripts/seed_data.py`) that:
1. Creates DB tables via Alembic
2. Downloads all configured seasons
3. Validates and loads into PostgreSQL
4. Prints summary stats (matches per season, teams per season)

---

### 3. Feature Engineering

Build match-level features from historical data for both the Dixon-Coles model and future XGBoost.

#### [NEW] `ml/features/form.py`

**Recent form features** (computed per team, looking backward only — no data leakage):
- `points_last_5`: Points earned in last 5 matches (0-15)
- `goals_scored_last_5`: Goals scored in last 5
- `goals_conceded_last_5`: Goals conceded in last 5
- `wins_last_5`, `draws_last_5`, `losses_last_5`
- `goal_diff_last_5`: Goal difference in last 5
- `points_per_game_season`: Season-to-date PPG
- `goals_scored_avg_season`: Season-to-date goals scored per game
- `goals_conceded_avg_season`: Season-to-date goals conceded per game

**Home/away splits** (all features computed separately for home and away):
- `home_goals_scored_avg`, `home_goals_conceded_avg`
- `away_goals_scored_avg`, `away_goals_conceded_avg`
- `home_win_rate`, `away_win_rate`

**Temporal features**:
- `days_since_last_match`: Fatigue proxy (for both home and away team)
- `league_position`: Current league standing at time of match
- `matches_played`: How far into the season (early-season uncertainty)
- `is_newly_promoted`: Binary flag — team was not in PL the previous season

> [!IMPORTANT]
> **Season-boundary rule**: All rolling/form features (`points_last_5`, `goals_scored_last_5`, etc.) **reset to null/default at the start of each season**. No cross-division carryover — a team's Championship form is not comparable to Premier League form. For a team's first N matches of a season (where N < window size), the feature is computed from however many PL matches are available that season (e.g., after 3 matches, `points_last_5` uses only those 3). If a team is newly promoted and has 0 PL matches, form features are null and the `is_newly_promoted` flag is set. This is an explicit design decision, not an accident of loop ordering.

#### [NEW] `ml/features/h2h.py`

**Head-to-head features** (looking backward across all available seasons):
- `h2h_home_wins`: Number of times home team beat away team (max last 10 meetings)
- `h2h_draws`: Number of draws
- `h2h_away_wins`: Number of times away team won
- `h2h_home_goals_avg`: Average goals scored by home team in H2H
- `h2h_away_goals_avg`: Average goals scored by away team in H2H
- `h2h_total_matches`: Number of historical meetings available

#### [NEW] `ml/features/pipeline.py`

Feature orchestrator that:
1. Takes a match (home_team, away_team, date) and historical match data
2. Calls `form.py` and `h2h.py` to compute feature vectors
3. Returns a flat dictionary of features for that match
4. Handles edge cases: first match of season (insufficient history), newly promoted teams (no PL H2H)
5. Implements `build_feature_matrix(matches_df) → DataFrame` for batch processing

> [!IMPORTANT]
> **Data leakage prevention**: All features are computed using ONLY data from before the match date. The pipeline must enforce strict temporal ordering. This is critical for walk-forward evaluation correctness in Phase 2.

---

### 4. Dixon-Coles Model

The core statistical model. This is the most technically challenging component.

#### [NEW] `ml/models/base.py`

Abstract base class for all models:
```python
class BasePredictor(ABC):
    @abstractmethod
    def fit(self, matches: pd.DataFrame) -> "BasePredictor": ...
    
    @abstractmethod
    def predict_proba(self, home: str, away: str) -> dict:
        """Returns {prob_home, prob_draw, prob_away}"""
        ...
    
    @abstractmethod
    def predict_score_distribution(self, home: str, away: str, max_goals: int = 10) -> np.ndarray:
        """Returns (max_goals+1, max_goals+1) probability matrix"""
        ...
    
    def predict_most_likely_score(self, home: str, away: str) -> tuple[int, int]:
        dist = self.predict_score_distribution(home, away)
        idx = np.unravel_index(dist.argmax(), dist.shape)
        return int(idx[0]), int(idx[1])
```

#### [NEW] `ml/models/dixon_coles.py`

**Model parameters** (estimated via MLE using `scipy.optimize.minimize`):
- `alpha_i` — attack strength for team `i` (one per team, ~27-29 params across 4 seasons of PL teams)
- `beta_i` — defense strength for team `i` (one per team, ~27-29 params)  
- `gamma` — home advantage factor (1 param)
- `rho` — Dixon-Coles low-score correction parameter (1 param)

**Total**: ~58-60 parameters for ~28-30 distinct teams across 4 seasons.

**Dixon-Coles correction function** (the key innovation over basic Poisson):
```
τ(x, y, λ, μ, ρ):
    if x == 0 and y == 0: return 1 - λ*μ*ρ
    if x == 0 and y == 1: return 1 + λ*ρ
    if x == 1 and y == 0: return 1 + μ*ρ
    if x == 1 and y == 1: return 1 - ρ
    else: return 1
```
This corrects the joint probability for low-scoring games (0-0, 0-1, 1-0, 1-1) where the independence assumption breaks down.

**Scoring rates**:
- `λ = alpha_home * beta_away * gamma` (home team expected goals)
- `μ = alpha_away * beta_home` (away team expected goals)

**Log-likelihood** (to maximize):
```
L = Σ_matches [ w(t) * log(τ(x,y,λ,μ,ρ) * Poisson(x;λ) * Poisson(y;μ)) ]
```
Where `w(t) = exp(-ξ * (T - t))` is the time-decay weight (ξ ≈ 0.005 per day, tunable).

**Identifiability constraint**: Fix one team's attack strength as the reference value (`alpha_ref = 1.0`). This team is dropped from the free parameter vector entirely.

> [!WARNING]
> **Why not "normalize after each iteration"**: Mutating parameters inside the optimization loop, outside the objective function `scipy` is differentiating, fights L-BFGS-B's gradient assumptions. It can produce silent non-convergence — the optimizer still returns a result, but it's not the true MLE. This passes small synthetic tests (5 teams, 30 matches) but degrades at real scale. The reference-team approach is mathematically equivalent and optimization-safe.

**Implementation approach**:
1. Choose a reference team (e.g., alphabetically first, or most-matches team for stability). Fix `alpha_ref = 1.0`.
2. Pack remaining parameters into vector: `[alpha_2, ..., alpha_N, beta_1, ..., beta_N, gamma, rho]` (note: all betas are free, only one alpha is fixed)
3. Use `scipy.optimize.minimize` with `method='L-BFGS-B'` and bounds (`rho ∈ [-1, 1]`, `alpha/beta > 0.01`, `gamma > 0`)
4. Reference: [dashee87's implementation](https://dashee87.github.io/football/python/predicting-football-results-with-statistical-modelling-dixon-coles-and-time-weighting/) (verified accessible)

**Prediction**:
1. Compute `λ` and `μ` from fitted parameters
2. Build (max_goals+1 × max_goals+1) joint probability matrix applying Dixon-Coles correction
3. Sum matrix regions for P(H), P(D), P(A)
4. Argmax for most likely score

**Serialization**: Pickle the fitted parameter vector + team-to-index mapping. Store in `data/models/` and load into FastAPI at startup.

---

### 5. FastAPI REST API

#### [NEW] `backend/api/main.py`

FastAPI app with:
- CORS middleware (allow all origins for dev)
- Lifespan handler: load fitted Dixon-Coles model at startup
- Exception handlers for model not found, unknown team, etc.

#### [NEW] `backend/api/routes/predictions.py`

**Endpoints**:

```
GET /api/v1/predictions/next-gameweek
```
Returns predictions for all upcoming matches in the current gameweek.
Response:
```json
{
  "gameweek": 5,
  "season": "2025-26",
  "predictions": [
    {
      "home_team": "Arsenal",
      "away_team": "Liverpool",
      "prob_home": 0.42,
      "prob_draw": 0.28,
      "prob_away": 0.30,
      "predicted_score": {"home": 1, "away": 1},
      "score_distribution": [[0.05, 0.08, ...], ...],
      "model": "dixon_coles"
    }
  ]
}
```

```
POST /api/v1/predictions/head-to-head
Body: {"home_team": "Arsenal", "away_team": "Liverpool"}
```
Returns prediction for an arbitrary matchup.

```
GET /api/v1/teams
```
Returns list of all teams the model knows about.

```
GET /api/v1/teams/{team_name}/stats
```
Returns team's current form, recent results, model parameters (attack/defense strengths).

```
GET /api/v1/health
```
Health check — returns model version, last training date, number of matches in training set.

#### [NEW] `backend/core/config.py`

Pydantic `BaseSettings` for:
- `DATABASE_URL`
- `MODEL_PATH` (path to serialized Dixon-Coles model)
- `FOOTBALL_DATA_API_KEY` (for Phase 3)
- `LOG_LEVEL`

#### [NEW] `backend/services/prediction.py`

Service layer that:
1. Loads the fitted model from disk (or DB)
2. Validates team names against known teams
3. Calls `model.predict_proba()` and `model.predict_score_distribution()`
4. Formats response as Pydantic models

---

### 6. Database Layer

#### [NEW] `backend/core/database.py`
- SQLAlchemy async engine with `asyncpg`
- Session factory
- Alembic config for migrations

#### [NEW] `alembic/` directory
- Initial migration: create `matches`, `teams`, `predictions` tables
- Migration for any schema changes during development

> [!NOTE]
> Using async SQLAlchemy from the start even though Phase 1 is simple. Prevents a painful migration later when the API needs to handle concurrent prediction requests.

---

### 7. Testing

#### [NEW] `tests/unit/test_ingestion.py`
- Test CSV parsing with a fixture CSV (5-10 rows of real data)
- Test team name normalization
- Test date parsing handles both formats
- Test bookmaker implied probability calculation (verify overround removal)
- Test Pandera schema catches bad data (negative goals, missing required columns, inconsistent FTR)

#### [NEW] `tests/unit/test_features.py`
- Test form features with known data: manually construct 10-match history, verify `points_last_5` etc.
- Test H2H with known matchups
- Test edge cases: team's first match of season, newly promoted team with no PL history
- **Test data leakage prevention**: verify features for match on date D use only data before D
- **Test season-boundary reset**: verify `points_last_5` is null/partial for first matches of a new season (no carryover from previous season)
- **Test newly promoted team**: verify form features are null and `is_newly_promoted` is True for a team's first PL season

#### [NEW] `tests/unit/test_dixon_coles.py`
- Test tau correction function: verify all 5 branches return expected values
- Test parameter packing/unpacking roundtrip (with reference-team alpha excluded from vector)
- Test on small synthetic dataset (5 teams, 30 matches): verify model converges, probabilities sum to 1
- Test on medium synthetic dataset (25 teams, 500 matches): verify convergence at realistic scale — catches optimization bugs that pass on small data
- Test `predict_score_distribution` shape and sum-to-1 property
- Test serialization/deserialization roundtrip
- Test that reference team's alpha is exactly 1.0 after fitting
- Test that teams with few matches (<10) produce wider score distributions than well-sampled teams (no silent overconfidence)

#### [NEW] `tests/unit/test_api.py`
- Test all endpoints with FastAPI `TestClient`
- Test unknown team returns 404
- Test health endpoint returns model metadata
- Test H2H endpoint validates team names

#### [NEW] `tests/integration/test_pipeline.py`
- End-to-end: download 1 season CSV → validate → load into test DB → compute features → fit model → predict
- Uses a dedicated test database (Docker Compose test service)

#### [NEW] `tests/property/test_poisson_properties.py`
Hypothesis property-based tests:
- `∀ home, away: sum(score_distribution) ≈ 1.0` (within floating-point tolerance)
- `∀ home, away: 0 ≤ prob_home, prob_draw, prob_away ≤ 1`
- `∀ home, away: prob_home + prob_draw + prob_away ≈ 1.0`
- `∀ match: tau(x, y, λ, μ, ρ) > 0` (probabilities can't be negative)
- Score distribution is non-negative everywhere
- Symmetry: swapping home/away (and removing home advantage) should swap probabilities

#### [NEW] `tests/conftest.py`
Shared fixtures:
- Sample match DataFrame (20-30 real matches from a known season)
- Test database session (PostgreSQL in Docker)
- Fitted model fixture (pre-fitted on sample data for fast API tests)

---

### 8. Documentation (Basic)

#### [NEW] `README.md`
- Project description and motivation
- Architecture diagram (Mermaid)
- Quickstart: `docker compose up` → `uv run python scripts/seed_data.py` → `uv run uvicorn backend.api.main:app`
- API documentation link (auto-generated Swagger at `/docs`)
- Tech stack badges
- Phase roadmap (Phase 1 ✅, Phase 2 🔜, Phase 3 🔜)

---

## Open Questions

> [!IMPORTANT]
> **Project location**: Should the project live at `d:\Yash Kokane\Projects\MatchSense\` as a new directory alongside your other projects? Or do you have a different location in mind?

> [!IMPORTANT]
> **Python version**: The plan assumes Python 3.12+. Do you have Python 3.12 or later installed? If not, I can adjust to 3.11 or help install it.

> [!IMPORTANT]
> **PostgreSQL for Phase 1**: Docker Compose handles this for local dev, but do you have Docker Desktop installed and working on Windows? If not, we could use SQLite for Phase 1 (simpler setup, same SQLAlchemy code, swap to Postgres when deploying).

---

## Verification Plan

### Automated Tests
```bash
# Unit + integration + property tests
uv run pytest tests/ -v --cov=ml --cov=backend --cov-report=term-missing

# Type checking
uv run mypy backend/ ml/ --strict

# Linting
uv run ruff check .
```

### Manual Verification
1. `docker compose up` → PostgreSQL starts, API starts
2. `uv run python scripts/seed_data.py` → 4 seasons loaded (~1,520 matches)
3. `curl localhost:8000/api/v1/health` → returns model metadata
4. `curl -X POST localhost:8000/api/v1/predictions/head-to-head -d '{"home_team":"Arsenal","away_team":"Liverpool"}'` → returns sensible probabilities
5. Verify probabilities are plausible: top teams should have higher attack strengths, home advantage should be positive

### Smoke Test for Model Sanity
- Man City at home vs a bottom-half team → P(H) should be > 0.5
- Bottom-half team at home vs Man City → P(A) should be > P(H)
- Any matchup → P(H) + P(D) + P(A) ≈ 1.0
- Home advantage parameter γ > 1.0 (home teams score more on average)
