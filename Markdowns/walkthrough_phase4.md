# MatchSense — Phase 4 Modern Frontend Dashboard Walkthrough

Phase 4 (**Modern Frontend Dashboard**) has been fully implemented, verified, and integrated with live backend services on branch `feature/phase4-frontend-dashboard`.

---

## 1. System Architecture & Components Delivered

The MatchSense frontend is a production-grade **Next.js 15 (App Router)** application located in `frontend/`, consuming the FastAPI live serving backend with 100% type-safe OpenAPI code generation and Tailwind CSS v4 design tokens:

```
frontend/
├── openapi.json                           # Offline schema introspection from FastAPI
├── package.json                           # Next.js 15, Tailwind v4, Radix, Vitest, MSW
├── tsconfig.json                          # TypeScript paths & strict bundler resolution
├── postcss.config.mjs                     # Tailwind CSS v4 PostCSS plugin
├── next.config.mjs                        # Next.js 15 production configuration
├── vitest.config.ts                       # Vitest + jsdom + ResizeObserver test runner
├── .github/workflows/frontend.yml         # GitHub Actions CI for drift check, tests, and build
├── src/
│   ├── app/
│   │   ├── globals.css                    # Tailwind v4 @theme tokens (Cyan vs. Violet)
│   │   ├── layout.tsx                     # Root layout with sticky Navbar & dark aesthetic
│   │   ├── page.tsx                       # Route 1: Upcoming Gameweek Fixtures Dashboard
│   │   ├── simulator/page.tsx             # Route 2: Interactive Head-to-Head Simulator
│   │   ├── teams/
│   │   │   ├── page.tsx                   # Route 3A: Premier League Club Directory & Scatter
│   │   │   └── [team]/page.tsx            # Route 3B: Club Deep-Dive Profile with Staleness Badge
│   │   └── models/page.tsx                # Route 4: Locked Evaluation Folds & Calibration Curves
│   ├── components/
│   │   ├── common/
│   │   │   ├── HealthBadge.tsx            # Tri-state API status badge (Models Live / Degraded / Offline)
│   │   │   ├── ModelProbabilityBar.tsx   # Dual-row horizontal stacked probability bar
│   │   │   └── Navbar.tsx                 # Sticky navigation header
│   │   ├── fixtures/
│   │   │   ├── FixtureCard.tsx            # Fixture card with dual-model probabilities & H2H link
│   │   │   ├── FixtureFilter.tsx          # Club search and dropdown filter
│   │   │   ├── FixtureGrid.tsx            # Interactive filtered fixtures grid
│   │   │   └── GameweekHero.tsx           # Matchweek header card with counts & model tags
│   │   ├── simulator/
│   │   │   ├── FeatureDiffTable.tsx       # XGBoost input differentials (Δ Elo, Form, SOT, Rest)
│   │   │   ├── ModelComparisonBlock.tsx   # Side-by-side Dixon-Coles vs. XGBoost cards
│   │   │   ├── ScoreHeatmap.tsx           # 5x5 Poisson score grid with relative sqrt scaling
│   │   │   └── TeamSelector.tsx           # Home/Away club pickers with instant swap
│   │   ├── teams/
│   │   │   └── LeagueStrengthScatter.tsx  # Recharts scatter plot (Attack α vs. Defense β)
│   │   └── models/
│   │       └── CalibrationChart.tsx       # Recharts reliability curves vs. ideal (y = x)
│   ├── data/
│   │   └── benchmarks.json                # Walk-forward benchmark metrics & calibration points
│   ├── hooks/
│   │   └── useHealthStatus.ts             # Health polling hook with 30s throttle & window focus reval
│   ├── lib/
│   │   ├── api.ts                         # Typed API client singleton with graceful degradation
│   │   ├── constants.ts                   # Premier League club metadata & colors
│   │   └── utils.ts                       # clsx + twMerge utility helper
│   └── types/
│       ├── api.generated.ts               # Auto-generated 100% from openapi.json via openapi-typescript
│       └── index.ts                       # Domain aliases (FixtureCard, ComparePredictionResponse, etc.)
└── tests/
    ├── setup.ts                           # Global test setup (ResizeObserver mock)
    ├── unit/
    │   ├── api.test.ts                    # API client resilience tests
    │   ├── FixtureCard.test.tsx           # Fixture card rendering and links
    │   ├── H2HSimulator.test.tsx          # Simulator URL hydration & compareMatch dispatch
    │   ├── HealthBadge.test.tsx           # Tri-state badge rendering
    │   ├── ModelProbabilityBar.test.tsx   # Probability bar formatting and math
    │   ├── ModelsPage.test.tsx            # Evaluation showcase and locked folds rendering
    │   ├── ScoreHeatmap.test.tsx          # Relative sqrt scaling and alpha bounding [0.08, 0.90]
    │   └── TeamProfile.test.tsx           # Team profile rendering and staleness transparency
    └── integration/
        └── resilience.test.tsx            # MSW integration tests covering all 5 matrix scenarios
```

---

## 2. Live Runtime Integration & Offline Snapshot Resolution

### 2.1 Issue Diagnosis
When accessing `http://localhost:3000`, the frontend initially rendered:
> *Operating offline: displaying historical research snapshot. Predictions are frozen.*

Investigation uncovered three factors:
1. **Database Unavailability & TCP Hang**: Docker was not yet started, causing synchronous PostgreSQL connection attempts on Windows to stall for ~15–20s. Next.js server-side rendering timed out and fell back to the research snapshot.
2. **Model Deserialization State**: In [`backend/services/model_manager.py`](file:///d:/Yash%20Kokane/Projects/MatchSense/backend/services/model_manager.py), Dixon-Coles was saved as a serialized state dictionary rather than a model instance.
3. **Local XGBoost Artifact**: `data/models/xgboost_latest.pkl` had not yet been generated in the local workspace.

### 2.2 Fixes Applied
- **ModelManager Resiliency**: Updated `backend/services/model_manager.py` to reconstruct `DixonColesModel` instances from state dictionaries dynamically.
- **XGBoost Artifact Generation**: Fitted and generated `data/models/xgboost_latest.pkl` using historical training data.
- **Dynamic Fixtures Fallback**: Updated `list_upcoming_fixtures` in [`backend/api/routes/predictions.py`](file:///d:/Yash%20Kokane/Projects/MatchSense/backend/api/routes/predictions.py) to catch database connectivity exceptions and dynamically evaluate upcoming matches with active ML models.
- **Docker PostgreSQL & Migrations**:
  - Started PostgreSQL container via `docker compose up -d db`.
  - Ran database schema migrations via `uv run alembic upgrade head` (bringing schema up to `a1b2c3d4e5f6, phase3_models_and_fixtures`).

### 2.3 Result
- `/api/v1/health` reports `status: "healthy"`, `model_loaded: true`, and `database_connected: true`.
- Both `dixon_coles` and `xgboost` report `loaded: true`.
- The frontend status badge displays **"Models Live"** (green dot).
- The amber offline snapshot banner is completely removed, serving live gameweek predictions.

### 2.4 Comprehensive Premier League Team Alias Normalization
- **Issue**: Selecting matches like *Manchester United vs Manchester City* or *Tottenham Hotspur vs Arsenal* returned `HTTP 404: Unknown team` because the frontend uses long club names (e.g. `"Manchester United"`) while the ML models were indexed using historical short names (e.g. `"Manchester Utd"`).
- **Resolution**:
  - Implemented `canonicalize_team_name` and `TEAM_ALIASES` in [`backend/services/prediction.py`](file:///d:/Yash%20Kokane/Projects/MatchSense/backend/services/prediction.py), mapping all official club names, abbreviations, and informal nicknames (e.g., *Man United, Spurs, Wolves, Man City*) to their canonical training keys.
  - Expanded `PREMIER_LEAGUE_TEAMS` in [`frontend/src/lib/constants.ts`](file:///d:/Yash%20Kokane/Projects/MatchSense/frontend/src/lib/constants.ts) to include *Wolverhampton Wanderers* and canonical alias keys.
  - Refined simulator error handling in [`frontend/src/app/simulator/page.tsx`](file:///d:/Yash%20Kokane/Projects/MatchSense/frontend/src/app/simulator/page.tsx) to surface actual API error details if a request fails rather than falsely declaring the backend offline.
  - Verified across multiple live Premier League matchups (Manchester Derby, North London Derby, Liverpool vs Wolves), returning HTTP 200 with Dixon-Coles most likely scorelines, 5x5 Poisson score distributions, and XGBoost feature differentials.

---

## 3. Key Architectural Invariants & Verified Solutions

### 3.1 Zero-Cost Offline OpenAPI Type Generation
- `scripts/export_openapi.py` introspects FastAPI's schema using `create_app().openapi()` without instantiating database connections or model lifespans.
- `openapi-typescript` generates `frontend/src/types/api.generated.ts` in **68ms**.
- `npm run typegen:check` guarantees zero schema drift in CI before tests or builds run.

### 3.2 Strictly Bounded Mathematical Visualizations
- **Poisson Score Heatmap**: Individual cell probability $p_{ij}$ is scaled relative to the maximum cell probability $p_{\max}$:
  $$s_{ij} = \sqrt{\frac{\max(0, p_{ij})}{p_{\max}}} \in [0, 1]$$
  $$\alpha_{ij} = 0.08 + 0.82 \cdot \min(1, s_{ij}) \in [0.08, 0.90]$$
  - Tested in [`tests/unit/ScoreHeatmap.test.tsx`](file:///d:/Yash%20Kokane/Projects/MatchSense/frontend/tests/unit/ScoreHeatmap.test.tsx): guaranteed to never saturate or exceed 0.90 alpha, lifting subtle scorelines into view while preserving the peak cell.
- **Model Separation**:
  - Dixon-Coles is highlighted in **Cyan** (`#0ea5e9`).
  - XGBoost is highlighted in **Violet** (`#8b5cf6`).
  - Strict side-by-side display without synthetic consensus blending.

### 3.3 Transparent Staleness Labeling & Locked Benchmark Folds
- **Locked Evaluation Folds**: Route `/models` strictly showcases out-of-sample walk-forward evaluation across test seasons:
  - **2023–24**, **2024–25**, and **2025–26** (with 2019–20 through 2022–23 training history).
- **Staleness Transparency**: Team profiles display explicit badges:
  - `[Stats as of 2026-09-13 · Retraining Pending]` if retraining is delayed or a partial outage is active.
  - `[Live Fold Active]` under nominal conditions.

---

## 4. Test & Verification Summary

### 4.1 Frontend Test Suite (18/18 Passed)
Running `npm run test` executes both unit and integration suites:

| Test File | Test Cases | Status | Description |
|---|---|---|---|
| `tests/unit/api.test.ts` | 2 | **PASS** | 200 Healthy response & fetch drop fallback |
| `tests/unit/HealthBadge.test.tsx` | 3 | **PASS** | Healthy, Degraded, and Offline badge states |
| `tests/unit/ModelProbabilityBar.test.tsx` | 2 | **PASS** | Format percentages and zero probability safe handling |
| `tests/unit/ScoreHeatmap.test.tsx` | 2 | **PASS** | Bounded alpha $\in [0.08, 0.90]$ & 25-cell grid render |
| `tests/unit/FixtureCard.test.tsx` | 1 | **PASS** | Teams rendering & URL query parameter linking |
| `tests/unit/H2HSimulator.test.tsx` | 1 | **PASS** | URL search parameter hydration (`?home=...&away=...`) |
| `tests/unit/TeamProfile.test.tsx` | 1 | **PASS** | Club profile and staleness indicator rendering |
| `tests/unit/ModelsPage.test.tsx` | 1 | **PASS** | Walk-forward benchmark and locked test folds |
| `tests/integration/resilience.test.tsx` | 5 | **PASS** | All 5 MSW degradation matrix scenarios |

### 4.2 Backend Regression Guard (103/103 Passed)
Running `uv run pytest tests/unit/ -v` verifies that all **103 backend unit tests** pass without regression:
- Health and model manager tests
- Dixon-Coles Poisson formulation and $\tau$-correction
- XGBoost walk-forward validation and feature pipelines
- Statistical significance tests (Wilcoxon and McNemar)
- Database ORM schemas and JSONB column defaults

### 4.3 Next.js 15 Production Build
Executing `npm run build` succeeds with zero errors:
- `ƒ /` (Server component, dynamic upcoming fixtures)
- `○ /simulator` (Prerendered client island, H2H simulator)
- `ƒ /teams` (Server component, club directory & scatter plot)
- `ƒ /teams/[team]` (Server component, club profile & ratings)
- `ƒ /models` (Server component, evaluation benchmarks & calibration)

---

## 5. Git Commit History on `feature/phase4-frontend-dashboard`

```
f3ab129 feat: add Coventry City and Sunderland promoted team support to backend and frontend
3c47453 fix(frontend): deduplicate club names in dropdowns using Proxy lookup for aliases
a46eb19 feat: add comprehensive Premier League team alias normalization to prediction service and frontend
46b6a4d fix(backend): support Dixon-Coles state-dict deserialization and dynamic fixture predictions
c104edd chore: update knowledge graph and progress tracking for Phase 4
efcdc95 ci: add frontend integration tests and GitHub Actions workflow
15338ea feat(frontend): implement walk-forward benchmark showcase and calibration chart
7dc7621 feat(frontend): implement teams directory and deep-dive profile views
0b8a27f feat(frontend): implement interactive head-to-head simulator with URL hydration
410a211 feat(frontend): implement upcoming gameweek fixtures view
e4f6a71 feat(frontend): implement ScoreHeatmap with relative sqrt scaling and ModelProbabilityBar
6cae37a feat(frontend): implement typed api client, useHealthStatus hook and Navbar
1bbb917 feat(frontend): scaffold Next.js 15 app with Tailwind v4 and openapi typegen
2448ea1 feat: add typed HealthResponse schema and offline openapi exporter
15b37c7 chore: add .superpowers and frontend build artifacts to .gitignore
```
