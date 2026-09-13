# MatchSense — Modern Frontend Dashboard Design Specification

> **Date**: 2026-09-13  
> **Status**: Approved Design  
> **Phase**: Phase 4 — Modern Frontend Dashboard  
> **Scope**: Next.js 15 App Router Web Application consuming the live MatchSense FastAPI Serving Layer  

---

## 1. Executive Summary & Design Principles

MatchSense provides an automated, dual-model Premier League prediction engine: a generative statistical model (Dixon-Coles bivariate Poisson with time-decay $\xi=0.005$ and low-scoring correlation $\rho$) and a discriminative ML model (XGBoost with rolling form, Elo, and fatigue). Phase 3 delivered a fault-isolated, automated ingestion and serving pipeline that hot-reloads models and serves dual predictions via FastAPI.

This specification designs the **Modern Frontend Dashboard** in `frontend/`, transforming the backend into an interactive, portfolio-grade web application.

### Key Architectural Tenets
1. **Decoupled Architecture**: The frontend is an independent Next.js application in `frontend/`, communicating with the FastAPI backend over HTTP (`NEXT_PUBLIC_API_URL`). It deploys independently to Vercel without coupling to the Python runtime.
2. **Structural Drift Prevention**: FastAPI's OpenAPI schema is introspected offline via `scripts/export_openapi.py` to compile `frontend/openapi.json`. `openapi-typescript` compiles that schema into `frontend/src/types/api.generated.ts`. Both files are committed to git, and CI enforces zero contract drift.
3. **Honest Dual-Model Presentation**: At no point in the UI will an unvalidated arithmetic average or "consensus" probability be rendered. Dixon-Coles and XGBoost are presented side-by-side with equal visual prominence and architecture badging (`Generative Poisson` vs. `Gradient Boosted Trees`).
4. **Transparent Staleness & Honest Research Sourcing**:
   - The `/models` page displays out-of-sample walk-forward benchmark tables from the frozen Phase 2A/2B evaluation suite (**2023–24, 2024–25, and 2025–26** test folds) with an explicit historical research snapshot banner.
   - If a model is degraded or held over from a prior training fold, the UI explicitly renders an `[As of YYYY-MM-DD · Retraining Pending]` badge rather than silently presenting stale data as live.

---

## 2. Technology Stack & Repository Structure

### 2.1 Technology Stack
* **Framework**: Next.js 15.x (App Router, React 19, TypeScript 5.x)
* **Styling**: Tailwind CSS v4 (Oxide engine, native CSS variables via `@theme` in `src/app/globals.css`)
* **UI & Accessibility Primitives**: Radix UI (`@radix-ui/react-tooltip`, `@radix-ui/react-popover`, `@radix-ui/react-tabs`) and `cmdk` for accessible, keyboard-navigable team comboboxes
* **Charts**:
  * **Recharts**: Reliability diagrams (calibration curves), Elo progression trajectories, and league attack-vs-defense scatter plots.
  * **Handcrafted SVG / CSS**: 5x5 Poisson score probability grid with Radix tooltips, and animated 3-segment probability split bars.
* **Contract Generation**: `openapi-typescript` reading from `frontend/openapi.json`.
* **Testing**: Vitest, React Testing Library, and Mock Service Worker (MSW).

### 2.2 Directory Structure
```
MatchSense/
├── backend/                   # FastAPI backend
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py      # Health endpoint with strict Pydantic HealthResponse
│   │   │   └── predictions.py # Prediction, fixture, and team endpoints
│   │   └── main.py            # App factory & route registration
├── ml/                        # ML modeling & evaluation pipelines
├── scripts/
│   └── export_openapi.py      # Offline OpenAPI schema exporter
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── openapi.json           # Committed OpenAPI JSON schema
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx     # Root shell: Header with HealthBadge, Nav, Footer
│   │   │   ├── globals.css    # Tailwind v4 @theme tokens, glassmorphic utilities
│   │   │   ├── page.tsx       # / -> Upcoming Gameweek fixtures & live hero
│   │   │   ├── simulator/
│   │   │   │   └── page.tsx   # /simulator -> Interactive H2H simulator
│   │   │   ├── teams/
│   │   │   │   ├── page.tsx   # /teams -> Premier League clubs directory & scatter plot
│   │   │   │   └── [team]/
│   │   │   │       └── page.tsx # /teams/[team] -> Attack/Defense & rolling stats
│   │   │   └── models/
│   │   │       └── page.tsx   # /models -> Walk-forward benchmarks & live health
│   │   ├── components/
│   │   │   ├── common/        # Navbar, HealthBadge, Footer, StatCard
│   │   │   ├── fixtures/      # FixtureCard, FixtureGrid, GameweekHero
│   │   │   ├── simulator/     # H2HSimulator, TeamSelector, ModelComparisonBlock, ScoreHeatmap, FeatureDiffTable
│   │   │   ├── teams/         # TeamCard, LeagueStrengthScatter, FormBadge, StrengthGauge
│   │   │   ├── models/        # CalibrationChart, BenchmarkTable, PipelineHealthCard, ArchitectureCard
│   │   │   └── ui/            # Accessible primitives (Tooltip, Popover, Combobox, Tabs, Badge)
│   │   ├── data/
│   │   │   └── benchmarks.json# Static evaluation report snapshot (Phases 2A/2B)
│   │   ├── lib/
│   │   │   ├── api.ts         # Typed API client with custom fetch & caching
│   │   │   ├── constants.ts   # Canonical team names, colors, crest slugs
│   │   │   └── utils.ts       # Percentage, odds, and date formatters
│   │   └── types/
│   │       ├── api.generated.ts # Auto-generated from openapi.json (source of truth)
│   │       └── index.ts       # Re-exported domain aliases derived from api.generated.ts
│   └── tests/
│       ├── unit/              # Math & component rendering tests
│       └── integration/       # Resilience matrix tests via MSW
```

---

## 3. Backend Contract Synchronization & OpenAPI Typegen

### 3.1 Backend Health Response Schema Hardening
To eliminate loose typing and hand-maintained interfaces, `backend/api/routes/health.py` is upgraded to use explicit Pydantic models:

```python
# backend/api/routes/health.py

class ModelStatus(BaseModel):
    loaded: bool
    version: str | None = None
    updated_at: str | None = None
    error: str | None = None

class HealthResponse(BaseModel):
    status: str  # "healthy" | "degraded"
    model_loaded: bool
    database_connected: bool
    models: dict[str, ModelStatus]
    message: str | None = None

@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    ...
```

### 3.2 Offline Introspection Script (`scripts/export_openapi.py`)
FastAPI registers all routes and Pydantic models synchronously during `create_app()`. Calling `app.openapi()` does **not** trigger the ASGI `lifespan` handler (which connects to Postgres and deserializes model artifacts). The script executes 100% offline without database access or environment credentials:

```python
# scripts/export_openapi.py
import json
from pathlib import Path
from backend.api.main import create_app

def export():
    app = create_app()
    schema = app.openapi()
    out_path = Path(__file__).resolve().parent.parent / "frontend" / "openapi.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
    print(f"Exported OpenAPI schema to {out_path}")

if __name__ == "__main__":
    export()
```

### 3.3 Typegen Pipeline & CI Verification
* **Generator Command**:
  `npm run typegen` $\rightarrow$ `python ../scripts/export_openapi.py && openapi-typescript openapi.json -o src/types/api.generated.ts`
* **CI Diff Check**:
  `npm run typegen:check` $\rightarrow$ `git diff --exit-code frontend/openapi.json frontend/src/types/api.generated.ts`
* **Domain Type Re-Exports (`frontend/src/types/index.ts`)**:
  Every type in the frontend is derived from `api.generated.ts`. Zero hand-written interfaces:
  ```typescript
  import type { components } from "./api.generated";

  export type FixtureCard = components["schemas"]["FixtureCard"];
  export type ComparePredictionResponse = components["schemas"]["ComparePredictionResponse"];
  export type ModelPredictionBlock = components["schemas"]["ModelPredictionBlock"];
  export type ScorePrediction = components["schemas"]["ScorePrediction"];
  export type TeamProfileResponse = components["schemas"]["TeamProfileResponse"];
  export type TeamStrength = components["schemas"]["TeamStrength"];
  export type HealthResponse = components["schemas"]["HealthResponse"];
  export type ModelStatus = components["schemas"]["ModelStatus"];
  ```

---

## 4. Data Fetching & Caching Strategy

### 4.1 Endpoint Volatility & Revalidation Policies

| Endpoint | Method | Fetch Location | Caching Policy | Justification |
|---|---|---|---|---|
| `/fixtures/upcoming` | GET | Server Component (`/`) | `next: { revalidate: 60 }` | Match completions & score updates happen weekly/daily; 60s prevents cache stale without hammering API. |
| `/teams` | GET | Server Component (`/teams`, `/simulator`) | `next: { revalidate: 3600 }` | Premier League club names are static across a season; 1 hour prevents redundant queries. |
| `/teams/{team}/profile` | GET | Server Component (`/teams/[team]`) | `next: { revalidate: 300 }` | 5 minutes balances high edge cache hit rates with reflecting manual sync or Elo changes. |
| `/predictions/compare` | POST | Client Island (`/simulator`) | `cache: "no-store"` | User-driven interactive tool with in-memory memoization (`Map<string, ComparePredictionResponse>`). |
| `/health` | GET | Client Island (`HealthBadge`) | `cache: "no-store"` | Pings on tab focus (`window.addEventListener('focus')`) throttled to 30s. |

### 4.2 Status Tri-State Mapping
The frontend client normalizes connectivity and health into three unambiguous states:
1. `healthy` (Emerald): API reachable, DB connected, both models loaded (`● Models Live`).
2. `degraded` (Amber): API reachable, but reporting DB disconnection or missing model (`▲ System Degraded`).
3. `offline` (Rose): Network error, timeout, or HTTP 502/504 reaching the API (`✕ API Offline`).

---

## 5. Information Architecture & Route Specifications

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                         Root Layout                             │
  │    [MatchSense Logo]   [Fixtures] [Simulator] [Teams] [Models]   │
  │                        [● Models Live Badge]                   │
  └─────────────────────────────────────────────────────────────────┘
           │                   │                 │              │
           ▼                   ▼                 ▼              ▼
     Route 1: `/`     Route 2: `/simulator` Route 3: `/teams` Route 4: `/models`
  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────┐ ┌──────────────────┐
  │ Gameweek Hero   │ │ Matchup Combos  │ │ Attack vs   │ │ Architecture Exp │
  │                 │ │ (Home vs Away)  │ │ Defense     │ │                  │
  │ Fixture Cards   │ │                 │ │ Scatter     │ │ Walk-Forward     │
  │ (Dual Model     │ │ Side-by-Side    │ │             │ │ Benchmarks Table │
  │  Split Bars)    │ │ Comparison:     │ │ 20 Clubs    │ │ (Locked Folds)   │
  │                 │ │ • DC Poisson    │ │ Grid        │ │                  │
  │ Deep Dive Links │ │   (5x5 Heatmap) │ │             │ │ Calibration      │
  │ -> /simulator   │ │ • XGBoost       │ │ Club Profile│ │ Curves (Recharts)│
  │                 │ │   (Feature Diff)│ │ (/teams/[t])│ │ Live Health Card │
  └─────────────────┘ └─────────────────┘ └─────────────┘ └──────────────────┘
```

### 5.1 Route 1: `/` (Upcoming Gameweek Fixtures)
* **Execution**: React Server Component (`src/app/page.tsx`).
* **Hero Banner (`<GameweekHero />`)**: Displays upcoming gameweek number, kickoff window countdown, and active model versions.
* **Filter Bar (`<FixtureFilter />`)**: Client island providing instantaneous client-side text filtering by team name.
* **Fixture Cards (`<FixtureCard />`)**:
  - Scheduled date and kickoff time in user's local timezone.
  - Home and Away club crests and canonical names.
  - **Dual-Model Split Bars (`<ModelProbabilityBar />`)**:
    - Row 1: Dixon-Coles Poisson `[ Home 48.2% | Draw 26.1% | Away 25.7% ]`
    - Row 2: XGBoost ML `[ Home 52.0% | Draw 24.5% | Away 23.5% ]`
  - **Deep Dive Button (`<DeepDiveButton />`)**: Links to `/simulator?home=Arsenal&away=Chelsea`.

### 5.2 Route 2: `/simulator` (Interactive Head-to-Head Simulator)
* **Execution**: Interactive Client Island (`src/app/simulator/page.tsx`).
* **URL Parameter Hydration**: On mount, reads `useSearchParams()`. If `?home=X&away=Y` are present and valid, sets combobox state and immediately invokes `api.compareMatch(home, away)`.
* **Combobox Selectors (`<TeamSelector />`)**: Built using Radix Popover + `cmdk` for search, arrow-key navigation, and ARIA semantics. Includes a 1-click swap button (`⇄`).
* **Comparison Workspace (`<ModelComparisonBlock />`)**:
  - **Dixon-Coles Card (Generative Poisson)**:
    - Probability split: Home Win %, Draw %, Away Win %.
    - Most likely score badge: e.g. `2 - 1` @ 11.4%.
    - **5x5 Score Probability Matrix (`<ScoreHeatmap />`)**: Described in Section 6.
  - **XGBoost Card (Discriminative ML)**:
    - Probability split: Home Win %, Draw %, Away Win %.
    - **Feature Differential Table (`<FeatureDiffTable />`)**:
      - Elo Rating differential ($\Delta \text{Elo}$)
      - Rolling 5-match form points & goal difference
      - Rolling shots on target & corners
      - Rest days differential (fatigue proxy)

### 5.3 Route 3: `/teams` & `/teams/[team]` (Club Directory & Profiles)
* **Directory (`/teams`)**:
  - **League Scatter Plot (`<LeagueStrengthScatter />` via Recharts)**: Plots attack strength ($\alpha$) on X-axis vs. defense strength ($\beta$) on Y-axis (inverted so better defense is higher) across all 20 clubs, quadrant-divided into Elite, High-Scoring, Defensive, and Underperforming.
  - Responsive grid of team cards with current Elo and attack/defense ratings.
* **Club Deep-Dive (`/teams/[team]`)**:
  - Attack rating gauge ($\alpha_i$, relative to $\mu=1.0$).
  - Defense rating gauge ($\beta_i$, relative to $\mu=1.0$).
  - Rolling form & shot metrics card.
  - Quick-action button: "Simulate Next Match" pre-populating `/simulator`.
  - **Staleness Badge**: If XGBoost was held over from a prior fold during weekly retraining, displays `[Stats as of YYYY-MM-DD · Retraining Pending]`.

### 5.4 Route 4: `/models` (Walk-Forward Benchmarks & Architecture Showcase)
* **Execution**: Server Component (`src/app/models/page.tsx`).
* **Honest Research Snapshot Banner**:
  > *"Out-of-sample walk-forward benchmark evaluated over 2023–24, 2024–25, and 2025–26 test folds. Historical research snapshot last evaluated: 2026-09-13."*
* **Static Data Source (`src/data/benchmarks.json`)**: Pre-compiled JSON containing the Phase 2A and 2B evaluation suite metrics (RPS, Brier, Log-Loss, Wilcoxon signed-rank p-values, calibration bin coordinates).
* **Evaluation Table (`<BenchmarkTable />`)**:
  - Side-by-side metric comparison across folds:
    - Fold 1 (2023–24)
    - Fold 2 (2024–25)
    - Fold 3 (2025–26)
    - Pooled 3-Season Metric
  - Benchmark targets: Dixon-Coles vs. XGBoost vs. Bookmaker Odds vs. Naive "Always Home" Baseline.
* **Reliability Diagrams (`<CalibrationChart />` via Recharts)**:
  - 10-bin calibration curve plotting predicted probability against observed empirical frequency with $y=x$ ideal calibration reference line.
* **Live Pipeline Health Card (`<PipelineHealthCard />`)**:
  - Sole dynamic client element on this page, fetching `GET /api/v1/health` to display live model hashes, database connection status, and hot-reload timestamps.

---

## 6. Visual Design System & Mathematical Visualizations

### 6.1 Design Tokens (`src/app/globals.css` via Tailwind v4 `@theme`)
```css
@theme {
  --color-background: #0a0d14;
  --color-surface-subtle: #111622;
  --color-surface-card: rgba(17, 22, 34, 0.75);
  --color-surface-elevated: #1a2234;
  --color-border-subtle: rgba(255, 255, 255, 0.08);

  /* Model Identity Accents (Cyan vs Violet) */
  --color-model-dixon: #0ea5e9;
  --color-model-dixon-glow: rgba(14, 165, 233, 0.25);
  --color-model-xgboost: #8b5cf6;
  --color-model-xgboost-glow: rgba(139, 92, 246, 0.25);

  /* Match Outcome Probabilities (Emerald vs Slate vs Amber) */
  --color-outcome-home: #10b981;
  --color-outcome-draw: #64748b;
  --color-outcome-away: #f59e0b;
}
```
*Hue Separation Guarantee*: Model identity (Cyan ~199°, Violet ~270°) and match outcomes (Emerald ~155°, Slate ~Neutral, Amber ~38°) have zero hue collision.

### 6.2 5x5 Poisson Score Heatmap Mathematics & Mechanics
Let $p_{ij}$ denote the probability of scoreline Home $i$, Away $j$ ($i, j \in \{0, 1, 2, 3, 4+\}$).  
Let $p_{\max} = \max_{a,b} p_{ab}$.

To ensure optimal contrast without clipping or inverting:
1. **Relative Max Square-Root Transfer**:
   $$s_{ij} = \sqrt{\frac{p_{ij}}{p_{\max}}} \in [0, 1]$$
2. **Bounded Alpha Channel**:
   $$\alpha_{ij} = 0.08 + 0.82 \cdot s_{ij} \in [0.08, 0.90]$$
3. **Background Style**:
   $$\text{backgroundColor} = \text{rgba}(14, 165, 233, \alpha_{ij})$$
4. **Visual Features**:
   - $p_{ij}=0 \implies \alpha=0.08$ (clean, visible baseline cell).
   - $p_{ij}=p_{\max} \implies \alpha=0.90$ (rich, non-saturated peak).
   - **Draw Diagonal Accentuation**: Cells $(0,0), (1,1), (2,2), (3,3), (4,4)$ feature a subtle dashed border (`border border-dashed border-slate-500/40`).
   - **Peak Score Glow**: Cell with $p_{\max}$ receives a glowing border (`ring-2 ring-amber-400 shadow-[0_0_12px_rgba(251,191,36,0.3)]`).
   - **Radix Tooltip**: Focusable with `tabIndex={0}`. Displays:
     `Arsenal 2 – 1 Chelsea: 11.4% probability (Implied odds: 8.77)`.

### 6.3 Monospace Tabular Figures
All numeric probability outputs use `font-mono tabular-nums tracking-tight` to prevent digit jitter during 400ms width transitions:
`transition: width 400ms cubic-bezier(0.16, 1, 0.3, 1)`.

---

## 7. Resilience, Degradation & Staleness Matrix

| Scenario | Health Badge | Gameweek View (`/`) | H2H Simulator (`/simulator`) | Team Profile (`/teams/[team]`) |
|---|---|---|---|---|
| **1. Nominal (All Healthy)** | `● Models Live` (Emerald) | Full dual-model probability bars rendered | Dual cards (Poisson heatmap + XGBoost features) active | Full attack/defense ratings + rolling form |
| **2. Partial Model Outage** (e.g. XGBoost Gate 2A failed, DC live) | `▲ System Degraded` (Amber) | DC bar rendered; XGBoost row shows `Retraining Pending` badge | DC card active; XGBoost card displays friendly fallback alert | DC attack/defense active; XGBoost stats show `[As of YYYY-MM-DD · Retraining Pending]` badge |
| **3. Models Initializing** (`503 Service Unavailable`) | `▲ System Degraded` (Amber) | Fixture kickoffs & club names displayed; probabilities show `Initializing` | Alert: *"Models initializing after weekly sync. Predictions updating shortly."* | Club metadata displayed with placeholder strength bars |
| **4. API Offline / Network Drop** (Fetch throws / 502 / 504) | `✕ API Offline` (Rose) | Serves edge-cached SSR snapshot if available; banner indicates stale data | Inline warning banner with manual `[Retry]` action | Serves edge-cached SSR snapshot if available |
| **5. Invalid Team Param** (`404 Not Found`) | `● Models Live` | N/A | Combobox resets to default pair (Arsenal vs Chelsea) with warning toast | Redirects to `/teams` directory with error toast |

---

## 8. Verification & Testing Plan

### 8.1 Automated CI Checks
1. **Contract Drift Check**:
   `npm run typegen:check` verifies `git diff --exit-code frontend/openapi.json frontend/src/types/api.generated.ts`.
2. **TypeScript Compilation**:
   `npm run typecheck` (`tsc --noEmit`) ensures 100% type safety across all components and API calls.
3. **Production Build**:
   `npm run build` verifies SSR page generation, static bundle creation, and zero client-server boundary errors.

### 8.2 Unit Tests (`frontend/tests/unit/`)
* `ScoreHeatmap.test.tsx`:
  - Asserts exactly 25 cells are rendered in 5x5 layout.
  - Validates calculated alpha values are strictly within $[0.08, 0.90]$ across zero, low (0.5%), moderate (4%), and high (15%+) probabilities.
  - Asserts max probability cell receives peak styling and draw diagonal has dashed border.
* `ModelProbabilityBar.test.tsx`:
  - Asserts Home, Draw, and Away percentages sum to 100% $\pm 0.1\%$.
  - Asserts zero probability renders cleanly without width negative underflow.
* `H2HSimulator.test.tsx`:
  - Asserts `home` and `away` URL query parameters hydrate into combobox state on initial mount.
  - Asserts changing a combobox updates URL via shallow routing without page reload.

### 8.3 Resilience Integration Tests (`frontend/tests/integration/resilience.test.tsx`)
Using Mock Service Worker (MSW) to intercept `/api/v1/*` requests and test all 4 failure scenarios in the resilience matrix:
1. **Scenario 1 (Nominal)**: Returns 200 OK with valid dual-model payloads. Asserts `● Models Live` renders and both model cards are active.
2. **Scenario 2 (Partial Model Outage)**: Returns Dixon-Coles active, XGBoost 503. Asserts `▲ System Degraded` renders, DC heatmap displays, and XGBoost displays the transparent staleness badge `[As of YYYY-MM-DD · Retraining Pending]`.
3. **Scenario 3 (503 Service Unavailable)**: Returns 503 on `/health` and `/predictions/compare`. Asserts "Models initializing after weekly sync" alert appears without crashing the page.
4. **Scenario 4 (Network Offline)**: Network request throws `NetworkError`. Asserts `✕ API Offline` badge renders and manual retry button is present.

---

## 9. Deliverables & Acceptance Criteria

1. `backend/api/routes/health.py` upgraded with strict `HealthResponse` Pydantic model.
2. `scripts/export_openapi.py` generating `frontend/openapi.json` offline.
3. Next.js 15 app scaffolded in `frontend/` with Tailwind v4, Radix UI, Recharts, and `api.generated.ts`.
4. All four routes implemented:
   - `/`: Upcoming gameweek fixtures with dual-model probability bars.
   - `/simulator`: Interactive H2H predictor with 5x5 Poisson score heatmap and XGBoost feature diff table.
   - `/teams` & `/teams/[team]`: League scatter plot and club profile with staleness transparency.
   - `/models`: Walk-forward benchmarks over 2023–24, 2024–25, 2025–26 folds with calibration curve and live health.
5. All automated unit and resilience integration tests passing.
6. Clean Git commit and zero contract drift in CI.
