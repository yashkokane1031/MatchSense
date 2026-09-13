# MatchSense — Phase 3: Live Serving & Automation Pipeline Specification

**Date**: 2026-09-13  
**Status**: APPROVED DESIGN  
**Scope**: Live External Ingestion, PostgreSQL Model Artifact Store, Decoupled Weekly Sync Pipeline, and Production Dual-Model Serving Layer.

---

## 1. Executive Summary & Goals

Phase 3 transitions MatchSense from an out-of-sample research and benchmarking environment into an automated, production-grade Premier League prediction service.

### Core Objectives
1. **Automated Weekly Synchronization**: Unattended pipeline executed via GitHub Actions cron every Tuesday at 03:00 UTC (after Monday night match finalization), ingesting new match box-scores, refitting models on the rolling 4-season window, and generating predictions for upcoming fixtures.
2. **Persistent, Ephemeral-Safe Model Store**: Database-native model artifact storage in PostgreSQL (`models` table) with single-query atomic hot-swapping, enabling stateless hosting (Render/Railway) to reload new models with zero downtime without local filesystem dependencies.
3. **Dual-Model Production Serving**: Serve `DixonColesModel` (generative Poisson) and `XGBoostPredictor` (discriminative gradient boosted trees) side-by-side with complete backward compatibility for existing single-model endpoints.
4. **Decoupled Transactional Safety**: Separate factual match data ingestion from ML model activation, and isolate model refits from each other, ensuring data freshness and healthy models are never blocked by numerical optimization anomalies in a single component.
5. **No Unvalidated Blending**: Pure side-by-side presentation of both benchmarked architectures; consensus/ensemble averaging remains strictly deferred to a formal Phase 2C evaluation suite.

---

## 2. Database Architecture & Schema Layer

PostgreSQL (Supabase) acts as the shared persistence layer between ephemeral GitHub Actions runners and cloud API container instances.

### 2.1 Model Artifact Store (`models` Table)

Stores serialized model binaries, configuration manifests, and walk-forward verification metadata:

```sql
CREATE TABLE models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(64) NOT NULL,              -- 'dixon_coles' | 'xgboost'
    version VARCHAR(64) NOT NULL,                 -- e.g. 'v202526_gw28_20260913_1400'
    artifact_bytes BYTEA NOT NULL,                -- zlib-compressed pickle payload (~1-2 MB)
    manifest JSONB NOT NULL,                      -- metrics, window range, parameters, audit scores
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Database-enforced invariant: exactly one active model per architecture
CREATE UNIQUE INDEX uq_active_model_per_name 
    ON models (model_name) 
    WHERE is_active = TRUE;

-- High-frequency polling index (< 1ms query cost)
CREATE INDEX idx_models_lookup 
    ON models (model_name, is_active, updated_at);
```

### 2.2 Upcoming Fixtures Store (`fixtures` Table)

Separates upcoming scheduled fixtures from completed ground-truth matches in `matches`:

```sql
CREATE TABLE fixtures (
    id INTEGER PRIMARY KEY,                       -- Football-Data.org external match ID
    season VARCHAR(10) NOT NULL,                  -- '2025-26'
    gameweek INTEGER NOT NULL,                    -- 1 to 38
    kickoff_time TIMESTAMPTZ NOT NULL,
    home_team VARCHAR(50) NOT NULL,               -- Canonical name
    away_team VARCHAR(50) NOT NULL,               -- Canonical name
    status VARCHAR(20) NOT NULL DEFAULT 'SCHEDULED', -- 'SCHEDULED' | 'TIMED' | 'POSTPONED' | 'FINISHED'
    precomputed_predictions JSONB NULL,           -- Cached per-model predictions: {"dixon_coles": {...}, "xgboost": {...}}
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_fixtures_upcoming 
    ON fixtures (status, kickoff_time);
```

---

## 3. Ingestion & Team Name Normalization

### 3.1 Ingestion-Time Canonical Name Resolution

To avoid silent join failures, `fixtures.home_team` and `fixtures.away_team` are normalized to MatchSense canonical names (`KNOWN_PL_TEAMS` standard) before database insertion.

```python
FOOTBALL_DATA_ORG_NAME_MAP: dict[str, str] = {
    "Arsenal FC": "Arsenal",
    "Aston Villa FC": "Aston Villa",
    "AFC Bournemouth": "Bournemouth",
    "Brentford FC": "Brentford",
    "Brighton & Hove Albion FC": "Brighton",
    "Burnley FC": "Burnley",
    "Chelsea FC": "Chelsea",
    "Crystal Palace FC": "Crystal Palace",
    "Everton FC": "Everton",
    "Fulham FC": "Fulham",
    "Ipswich Town FC": "Ipswich",
    "Leeds United FC": "Leeds",
    "Leicester City FC": "Leicester",
    "Liverpool FC": "Liverpool",
    "Luton Town FC": "Luton",
    "Manchester City FC": "Manchester City",
    "Manchester United FC": "Manchester Utd",
    "Newcastle United FC": "Newcastle",
    "Nottingham Forest FC": "Nottingham Forest",
    "Sheffield United FC": "Sheffield Utd",
    "Southampton FC": "Southampton",
    "Tottenham Hotspur FC": "Tottenham",
    "West Ham United FC": "West Ham",
    "Wolverhampton Wanderers FC": "Wolverhampton",
}
```

Any unmapped team name logs a structured warning and passes through standard suffix stripping (`replace(" FC", "").replace("AFC ", "")`) to ensure clean onboarding of promoted teams.

---

## 4. Pipeline Execution & Decoupled Architecture

The weekly synchronization script (`scripts/sync_pipeline.py`) runs in an external orchestrator (GitHub Actions or local CLI) and decomposes operations into **three isolated database transactions**.

```
                ┌───────────────────────────────────────────┐
                │             WEEKLY CRON RUN               │
                │        (Tuesday 03:00 UTC Runner)         │
                └─────────────────────┬─────────────────────┘
                                      │
               ┌──────────────────────▼──────────────────────┐
               │    TRANSACTION 1 (Phase A: Ground Truth)    │
               │  - Ingest new completed matches -> matches  │
               │  - Ingest upcoming schedule -> fixtures     │
               │  - Mark completed fixtures as FINISHED      │
               │  - Score Gate 2B multi-GW audit             │
               │  - COMMIT (Historical facts are permanent)  │
               └──────────────┬──────────────────────────────┘
                              │
             ┌────────────────┴────────────────┐
             │                                 │
┌────────────▼────────────────┐   ┌────────────▼────────────────┐
│ TRANSACTION 2 (Phase B1: DC)│   │ TRANSACTION 3 (Phase B2: XGB│
│ - Slice rolling 4 seasons   │   │ - Slice rolling 4 seasons   │
│ - Fit Attempt 1 (warm-start)│   │ - Compute rolling features  │
│ - Fallback Attempt 2 (flat) │   │ - Fit 120 regularized trees │
│ - Validate Gate 2A bounds   │   │ - Validate Gate 2A probs    │
│ - Atomic swap: active model │   │ - Atomic swap: active model │
│ - Update fixtures[dc_preds] │   │ - Update fixtures[xgb_preds]│
│ - COMMIT                    │   │ - COMMIT                    │
└─────────────────────────────┘   └─────────────────────────────┘
  (Failure rolls back ONLY DC)      (Failure rolls back ONLY XGB)
```

### 4.1 Phase A: Factual Data Ingestion Transaction
1. **Fetch Match CSV**: Downloads active season `E0.csv` from `football-data.co.uk`. Filters new completed matches not yet in `matches`. Validates schema via Pandera.
2. **Fetch Scheduled Fixtures**: Calls Football-Data.org API (`GET /v4/competitions/PL/matches?status=SCHEDULED`). Normalizes club names.
3. **Commit Phase A**: Inserts new match box-scores into `matches`, upserts upcoming schedules into `fixtures`. `COMMIT`.
   - *Failure behavior*: If data sources fail or validate incorrectly, Phase A rolls back. No partial match data lands.

### 4.2 Phase B1: Dixon-Coles Refit & Activation Transaction
1. **Slicing**: Extract the 4-season rolling window (1,520 matches) ending at latest match date.
2. **Two-Tier Optimizer Budget & Hypothesis Separation**:
   - **Attempt 1 (Warm-Start with Standard Budget)**:
     - *Hypothesis*: The objective surface has shifted slightly ($\le 1.3\%$) with the new gameweek(s); initializing from the prior active parameter vector yields fast, exact convergence in the same local basin.
     - *Initialization*: `warm_start_params` from the currently active model in `models` table, clipped to valid bounds.
     - *Budget*: `maxfun=50,000`, `maxiter=2,000`.
   - **Attempt 2 (Flat-Prior Reset with Doubled Budget)**:
     - *Trigger*: Attempt 1 fails to converge (`STOP: EXCEEDS LIMIT`), raises numerical error, or converges to a solution that violates Gate 2A bounds.
     - *Hypothesis*: The warm-start starting vector was trapped in an ill-conditioned local geometry, saddle point, or extreme parameter boundary.
     - *Initialization*: Completely discard the warm-start vector. Reset to the canonical symmetric flat prior ($\alpha_i = 1.0, \beta_i = 1.0, \gamma = 1.30, \rho = -0.05$).
     - *Budget*: Doubled ceiling: `maxfun=100,000`, `maxiter=4,000`.
3. **Gate 2A (Parameter Bounds Verification)**:
   - Verify $\gamma \in [1.05, 1.55]$, $\rho \in [-0.25, 0.25]$, $\alpha_i, \beta_i \in [0.15, 4.0]$, and $\alpha_{\text{ref}} \equiv 1.0$.
4. **Activation & Fixture Update**:
   - `UPDATE models SET is_active = FALSE WHERE model_name = 'dixon_coles';`
   - `INSERT INTO models (model_name, version, artifact_bytes, manifest, is_active) VALUES ('dixon_coles', ..., TRUE);`
   - Generate Dixon-Coles fixture predictions for scheduled matches.
   - Update `fixtures.precomputed_predictions = jsonb_set(coalesce(precomputed_predictions, '{}'), '{dixon_coles}', :dc_preds)`. `COMMIT`.
   - *Failure behavior*: If both Attempt 1 and Attempt 2 fail Gate 2A, Phase B1 rolls back. The previously active Dixon-Coles model remains active in `models`. A critical alert is logged.

### 4.3 Phase B2: XGBoost Refit & Activation Transaction
1. **Feature Update**: Recompute window-anchored Elo ($R_0 = 1500$) and rolling stats matrix across 1,520 rows.
2. **Model Refit**: Fit 120 regularized gradient-boosted trees over 70 features.
3. **Gate 2A (Probability Verification)**:
   - Verify non-empty predictions, no NaN/Inf, and individual match probabilities fall in $[0.01, 0.95]$.
4. **Activation & Fixture Update**:
   - `UPDATE models SET is_active = FALSE WHERE model_name = 'xgboost';`
   - `INSERT INTO models (model_name, version, artifact_bytes, manifest, is_active) VALUES ('xgboost', ..., TRUE);`
   - Generate XGBoost fixture predictions for scheduled matches.
   - Update `fixtures.precomputed_predictions = jsonb_set(coalesce(precomputed_predictions, '{}'), '{xgboost}', :xgb_preds)`. `COMMIT`.
   - *Failure behavior*: If refit fails or produces invalid probabilities, Phase B2 rolls back. The previously active XGBoost model remains active.

### 4.4 Multi-Gameweek Cadence & Gate 2B Out-of-Sample Audit

When runs skip due to CSV delays, international breaks, or holiday fixture congestion, two or more gameweeks arrive simultaneously. The system handles this gracefully:

#### Gate 2B Multi-Gameweek Audit
- Finds all completed matches in `matches` that correspond to unfinished fixture cards in `fixtures` (or matches since last sync).
- Groups them by gameweek: `audited_gws = sorted(new_matches['gameweek'].unique())`.
- For **each** gameweek $gw \in audited\_gws$:
  - Extracts the pre-kickoff predictions saved in `fixtures.precomputed_predictions`.
  - Calculates out-of-sample RPS and Accuracy for both Dixon-Coles and XGBoost against actual outcomes.
  - Appends the scored record to `manifest["audit_history"]`:
    ```json
    {
      "gameweek": 28,
      "n_matches": 10,
      "dixon_coles_rps": 0.1984,
      "xgboost_rps": 0.2012,
      "dixon_coles_acc": 0.6000,
      "xgboost_acc": 0.5000,
      "scored_at": "2026-09-13T03:05:12Z"
    }
    ```
- Marks audited fixture records as `status = 'FINISHED'`.

#### Dixon-Coles Warm-Start Across Multi-Gameweek Shifts
- **Window Shift $\le 30$ matches ($\le 3$ GWs)**: 98.0%+ of the log-likelihood data remains unchanged. Time decay $\xi = 0.0019$ operates continuously across match dates ($e^{-0.0019 \times 14} \approx 0.974$), preserving the convex neighborhood. Attempt 1 warm-start proceeds as normal.
- **Window Shift $> 40$ matches or Season Boundary**: If the active team roster changes (promoted/relegated teams appear) or an extended outage occurred, Attempt 1 automatically skips warm-start and routes directly to the flat prior.
- **Fail-Safe**: If any multi-gameweek warm-start fails, Attempt 2 flat-prior reset provides an unconditional 100k-eval guarantee.

---

## 5. Comprehensive Failure-Mode & Recovery Matrix

| Failure Mode | Detection Point | Transaction State | Recovery Action | Production Impact |
| :--- | :--- | :--- | :--- | :--- |
| **CSV Not Yet Published** | Phase A: 0 new matches found | Phase A commits 0 rows | Pipeline logs `INFO: Up to date`, skips refits, exits 0. | None. Existing models and predictions remain valid. |
| **Ingestion Network / Schema Error** | Phase A: Pandera validation error or HTTP 5xx | Phase A `ROLLBACK` | Log error, exit 1. Alert dispatched. | None. Prior match database untouched. Next run retries. |
| **Dixon-Coles Non-Convergence** | Phase B1: Attempt 1 & 2 fail or exceed budget | Phase B1 `ROLLBACK` (Phase A committed; Phase B2 proceeds) | Prior `is_active` DC model remains active. Alert logged. | Zero downtime. DC serves previous week's weights; XGBoost updates normally. |
| **Dixon-Coles Parameter Anomaly** | Phase B1: Gate 2A bounds check fails | Phase B1 `ROLLBACK` | Prior `is_active` DC model remains active. Alert logged. | Zero downtime. Untrusted parameter set discarded. |
| **XGBoost Fit / Probability Failure** | Phase B2: NaN probabilities or degenerate range | Phase B2 `ROLLBACK` (Phase A committed; Phase B1 committed) | Prior `is_active` XGBoost model remains active. Alert logged. | Zero downtime. DC updates normally; XGBoost serves previous weights. |
| **Database Blip During Serving** | FastAPI hot-path: 30s polling query fails | Read-only query timeout | Catch DB exception, retain existing in-memory models, log warning. | Zero downtime. API continues serving loaded models. `/health` reports `database_connected: false`. |
| **Cold-Start / Empty Database** | Container startup: `models` table empty | Initial startup | Fall back to loading local repository artifacts (`models/dixon_coles_weights.pkl`). | Service boots cleanly with Phase 2B validated weights. |

---

## 6. Production Serving Layer (`ModelManager`)

### 6.1 In-Memory Lifecycle & Polling (`backend/services/model_manager.py`)

FastAPI uses an in-memory `ModelManager` to avoid DB latency on the hot path while maintaining automatic synchronization:

- **Hot-Path Performance (< 0.01ms)**: Requests use loaded in-memory model references directly.
- **Timestamp Polling (30s TTL)**: On incoming requests, if `time.time() - last_checked > 30.0s`, execute:
  ```sql
  SELECT model_name, updated_at FROM models WHERE is_active = TRUE;
  ```
  If `updated_at > model_loaded_at`, fetch `artifact_bytes`, decompress with `zlib`, deserialize, and atomically replace the model pointer.
- **Independent Swapping**: Dixon-Coles and XGBoost are held in independent references (`_dc_model`, `_xgb_model`).
- **Offline Fallback**: If database connection is unavailable, `ModelManager` falls back to reading local `.pkl` files (`settings.model_path`, `settings.xgb_model_path`).

### 6.2 API Contracts

#### 1. Single-Model Head-to-Head (Backward-Compatible)
`POST /api/v1/predictions/head-to-head?model=dixon_coles` (default: `dixon_coles`)
```json
{
  "home_team": "Arsenal",
  "away_team": "Chelsea",
  "prob_home": 0.5412,
  "prob_draw": 0.2315,
  "prob_away": 0.2273,
  "predicted_score": {"home": 2, "away": 1},
  "score_distribution": [[0.0521, 0.0683, 0.0352], "..."],
  "model": "dixon_coles"
}
```

`POST /api/v1/predictions/head-to-head?model=xgboost`
```json
{
  "home_team": "Arsenal",
  "away_team": "Chelsea",
  "prob_home": 0.5284,
  "prob_draw": 0.2411,
  "prob_away": 0.2305,
  "predicted_score": null,
  "score_distribution": null,
  "model": "xgboost"
}
```

#### 2. Multi-Model Comparison
`POST /api/v1/predictions/compare`
```json
{
  "home_team": "Arsenal",
  "away_team": "Chelsea",
  "dixon_coles": {
    "prob_home": 0.5412,
    "prob_draw": 0.2315,
    "prob_away": 0.2273,
    "predicted_score": {"home": 2, "away": 1},
    "score_distribution": [[0.0521, 0.0683], "..."]
  },
  "xgboost": {
    "prob_home": 0.5284,
    "prob_draw": 0.2411,
    "prob_away": 0.2305,
    "features": {
      "elo_diff": 84.5,
      "rolling_xg_diff": 0.42,
      "rolling_sot_diff": 2.1
    }
  }
}
```

#### 3. Upcoming Fixtures Feed
`GET /api/v1/fixtures/upcoming`
```json
[
  {
    "id": 432101,
    "gameweek": 29,
    "kickoff_time": "2026-03-21T15:00:00Z",
    "home_team": "Arsenal",
    "away_team": "Chelsea",
    "status": "SCHEDULED",
    "predictions": {
      "dixon_coles": {"prob_home": 0.5412, "prob_draw": 0.2315, "prob_away": 0.2273},
      "xgboost": {"prob_home": 0.5284, "prob_draw": 0.2411, "prob_away": 0.2305}
    }
  }
]
```

#### 4. Team Profiles
`GET /api/v1/teams/{team_name}/profile`
```json
{
  "team": "Arsenal",
  "dixon_coles": {
    "attack": 1.3421,
    "defense": 0.7812
  },
  "xgboost": {
    "current_elo": 1642.5,
    "rolling_sot": 6.2,
    "rolling_corners": 7.1,
    "recent_form_points": 13
  }
}
```

#### 5. Health & Metadata
`GET /api/v1/health`
```json
{
  "status": "healthy",
  "database_connected": true,
  "models": {
    "dixon_coles": {
      "loaded": true,
      "version": "v202526_gw28_20260913_1400",
      "loaded_at": "2026-09-13T14:02:15Z",
      "home_advantage": 1.2502
    },
    "xgboost": {
      "loaded": true,
      "version": "v202526_gw28_20260913_1400",
      "loaded_at": "2026-09-13T14:02:15Z",
      "n_features": 70
    }
  }
}
```

---

## 7. Verification & Testing Strategy

### 7.1 Automated Test Suite
- `tests/unit/test_api_phase3.py`:
  - Verify `POST /predictions/head-to-head` produces identical backward-compatible outputs for `?model=dixon_coles` and `?model=xgboost`.
  - Verify `POST /predictions/compare` nests both models correctly without consensus blending.
  - Verify `GET /fixtures/upcoming` returns scheduled matches with dual predictions.
  - Verify `GET /teams/{team}/profile` returns Poisson strengths alongside Elo and rolling features.
- `tests/unit/test_model_manager.py`:
  - Mock DB with newer timestamp triggers in-memory model replacement.
  - Mock DB failure ensures in-memory fallback continues serving uninterrupted.
- `tests/integration/test_sync_pipeline.py`:
  - Verify Phase A commits matches and fixture schedules even if Phase B1 refit fails.
  - Verify Phase B1 Attempt 1 (warm-start) vs Attempt 2 (flat-prior reset) on Gate 2A bounds violation.
  - Verify Gate 2B multi-gameweek audit scoring across skipped gameweek backlog.
  - Verify independent transaction commits: healthy XGBoost commits when Dixon-Coles aborts.

### 7.2 Regression Invariant
- All 99 existing unit, property, and integration tests must continue to pass with 0 regressions.
