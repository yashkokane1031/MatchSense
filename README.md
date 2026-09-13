# MatchSense ⚽

> **Dual-Architecture Premier League Predictive Engine & Live Operational Dashboard**  
> Pairing a generative Bivariate Poisson process (Dixon-Coles) with regularized gradient-boosted trees (XGBoost), featuring walk-forward statistical verification, automated fixture ingestion, and zero-downtime model serving.

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15.2-black.svg)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%2B-336791.svg)](https://www.postgresql.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0%2B-eb6100.svg)](https://xgboost.readthedocs.io/)
[![Pytest](https://img.shields.io/badge/Pytest-142%20passed-brightgreen.svg)](tests/)
[![Vitest](https://img.shields.io/badge/Vitest-18%20passed-brightgreen.svg)](frontend/tests/)
[![uv](https://img.shields.io/badge/uv-fast%20packaging-purple.svg)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Overview

**MatchSense** is an end-to-end, production-grade football analytics and prediction platform for the English Premier League. Built around the foundational insight that no single mathematical framework captures both match dynamics and complex non-linear feature interactions, MatchSense runs two fundamentally distinct architectures side-by-side:

1. **Generative Modeling (Dixon-Coles)**: Estimates latent attack and defense parameters through maximum likelihood estimation (MLE) over a bivariate Poisson process, adjusted for low-scoring match interdependence and exponential time-decay.
2. **Discriminative Learning (XGBoost)**: Evaluates a ~70-dimensional feature space covering window-anchored dynamic Elo ratings, rolling expected goals (xG), shot quality metrics, fatigue/rest differentials, and form trajectories.

Every prediction is served live through a high-performance **FastAPI** backend and visualized in an interactive **Next.js 15** dark-glassmorphic dashboard.

### Core Engineering Principles
- **No Fabricated Numbers**: Strictly rejects synthetic fallback values or mock numbers. When features are uncomputable (e.g. newly promoted clubs or missing external feeds), the platform fails visibly with honest UI states.
- **Strict Temporal Isolation**: Features are engineered using *only* matches strictly prior to match kickoff. Rolling statistics reset at season boundaries to avoid cross-division contamination.
- **Operational Guardrails**: Automated Gate 2A threshold verification, Gate 2B out-of-sample prediction audits, and two-pass regularization to prevent optimizer boundary collapse.
- **Decoupled Zero-Downtime Serving**: PostgreSQL-backed binary model artifacts hot-reloaded into memory without restarting API workers or dropping active requests.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Data Pipeline
        FDA["Football-Data.org API"] -->|Scheduled Fixtures| SYNC["scripts/sync_pipeline.py"]
        FDC["football-data.co.uk CSVs"] -->|Historical Results| SYNC
        SYNC -->|Validation| PAN["Pandera Schema Enforcement"]
        PAN -->|Committed Phase A| PG[("PostgreSQL 16 Database")]
    end

    subgraph Model Training and Invariants
        PG --> LOAD["ml/data/loader.py"]
        LOAD --> DC_FIT["Dixon-Coles MLE Fit"]
        DC_FIT --> P2_CHECK{"Boundary Collapse?"}
        P2_CHECK -->|Yes| PASS2["Pass 2: Bayesian Shrinkage Prior"]
        P2_CHECK -->|No| G2A_DC["Gate 2A Parameter Validation"]
        PASS2 --> G2A_DC
        
        LOAD --> FEAT["ml/features/pipeline.py"]
        FEAT --> ELO["Window-Anchored Elo"]
        FEAT --> FORM["Form and Rest Windows"]
        FEAT --> XGB_FIT["XGBoost Booster Training"]
        XGB_FIT --> G2A_XGB["Gate 2A Probabilities Sanity"]

        G2A_DC -->|Phase B1 Pass| ARTIFACTS[("Model Artifacts Table")]
        G2A_XGB -->|Phase B2 Pass| ARTIFACTS
        ARTIFACTS -->|Atomic jsonb_set| FIXTURES[("Fixtures Table")]
    end

    subgraph Live Serving Layer
        ARTIFACTS -->|Hot Reload TTL| MM["ModelManager In-Memory"]
        FIXTURES --> PREDS["PredictionService"]
        MM --> PREDS
        PREDS --> API["FastAPI REST API"]
        API --> HEALTH["GET /api/v1/health"]
        API --> FIX_EP["GET /api/v1/fixtures/upcoming"]
        API --> H2H_EP["POST /api/v1/predictions/compare"]
        API --> TEAM_EP["GET /api/v1/teams/:team/profile"]
    end

    subgraph Frontend Application
        API --> NEXT["Next.js 15 App Router"]
        NEXT --> DASHBOARD["/ (Upcoming Fixture Cards)"]
        NEXT --> SIMULATOR["/simulator (H2H Matrix and Heatmap)"]
        NEXT --> BENCHMARK["/models (Walk-Forward Benchmark)"]
        NEXT --> PROFILES["/teams/:team (Team Profiles and Staleness)"]
    end
```

---

## 🧮 Mathematical & Algorithmic Foundations

### 1. Dixon-Coles Bivariate Poisson Process

Expected goals for home team $i$ facing away team $j$ are expressed as:
$$\lambda_{ij} = \alpha_i \beta_j \gamma$$
$$\mu_{ij} = \alpha_j \beta_i$$

Where:
- $\alpha_i > 0$: Attack strength of team $i$
- $\beta_j > 0$: Defensive vulnerability of team $j$
- $\gamma > 0$: Home ground advantage factor
- $\xi = 0.005$: Exponential time-decay rate, weighting each historical match by $w(t) = e^{-\xi (t_{\max} - t)}$

Joint score probabilities $P(X=x, Y=y)$ incorporate the low-score coupling factor $\tau_{x,y}$:
$$P(X=x, Y=y) = \tau_{x,y}(\lambda, \mu, \rho) \cdot \frac{\lambda^x e^{-\lambda}}{x!} \cdot \frac{\mu^y e^{-\mu}}{y!}$$

$$\tau_{x,y}(\lambda, \mu, \rho) = \begin{cases}
1 - \lambda \mu \rho & x=0, y=0 \\
1 + \lambda \rho & x=0, y=1 \\
1 + \mu \rho & x=1, y=0 \\
1 - \rho & x=1, y=1 \\
1 & \text{otherwise}
\end{cases}$$

#### Two-Pass Small-Sample Shrinkage Regularization
In multi-season sliding windows (e.g. 2026-27), newly promoted clubs with few matches (e.g. Coventry, Hull) risk optimizer boundary collapse ($\alpha \to 0.01$ or $\beta \to 0.01$). MatchSense prevents this using an autonomous **two-pass MLE framework**:
1. **Pass 1**: Unconstrained joint MLE optimization with convergence monitoring.
2. **Boundary Detection**: Identifies any team pinned against boundary thresholds ($\le 0.02$).
3. **Pass 2 (Reduced Parameter Space)**: Pinned teams are shrunk toward empirical league priors using Bayesian shrinkage ($k=10$ match equivalent):
   $$\theta_{\text{shrunk}} = \frac{n \cdot \theta_{\text{mle}} + k \cdot \theta_{\text{prior}}}{n + k}$$
   These values are locked and excluded from the solver parameter vector. The optimizer solves Pass 2 over only the remaining active teams and shared parameters ($\gamma, \rho$), ensuring that shared league parameters are not warped by small-sample teams.

---

### 2. Regularized XGBoost Tree Ensemble

The discriminative model classifies match outcomes ($y \in \{\text{Home}, \text{Draw}, \text{Away}\}$) using regularized gradient-boosted decision trees (`multi:softprob`).

- **Window-Anchored Dynamic Elo**: Elo ratings updated chronologically across historical match windows ($K=20$), initialized at $1500$, with a $+65.0$ home ground advantage rating boost.
- **Feature Vector (~70 Dimensions)**:
  - **Recent Form**: Points, goal difference, goals scored/conceded, and win/draw/loss counts over rolling 5-match windows.
  - **Match Dynamics**: Rolling shots on target (SOT) for/against, SOT ratio, rolling corners.
  - **Fatigue & Rest**: Exact rest days between matches (`days_since_last_match`).
  - **Head-to-Head**: Historical matchup points and goal averages over prior encounters.
  - **Contextual Signals**: Newly promoted indicator, season index, home/away win splits.
- **Native Cold-Start Routing**: Teams with zero history in the active season are assigned baseline Elo ratings while form/shot metrics are routed as `np.nan` into XGBoost's native missing-value tree branches.

---

## 🛡️ Operational Safeguards & Gatekeeper Architecture

| Gate | Stage | Condition | Failure Action |
|---|---|---|---|
| **Gate 2A (Dixon-Coles)** | Post-Fit | $\gamma \in [1.05, 1.55]$, $\rho \in [-0.25, 0.25]$, $\alpha, \beta \in [0.15, 4.0]$ | Abort activation, rollback transaction, retain previous model |
| **Gate 2A (XGBoost)** | Post-Fit | $\sum P \in [0.98, 1.02]$, $P_k \in [0.0, 1.0]$ | Abort activation, rollback transaction, retain previous model |
| **Gate 2B (Audit)** | Pre-Retrain | Multi-gameweek out-of-sample RPS & Brier evaluation on frozen predictions | Logs drift alert if RPS degrades $>15\%$ against historical baseline |
| **Health Guard** | Live Serving | Database connection + fixture feed configuration + fixture table count | Decoupled `/health` flags degraded ingestion even if DB is connected |

---

## ⚡ Live Synchronization Pipeline (`sync_pipeline.py`)

The weekly sync engine executes a decoupled multi-phase ingestion workflow:

1. **Phase A (Immediate Commit)**:
   - Queries Football-Data.org API for scheduled fixtures (Gameweek 4 through 38).
   - Ingests latest completed match results from football-data.co.uk CSVs into PostgreSQL `matches`.
   - Upserts all 342 upcoming fixtures into PostgreSQL `fixtures` table.
2. **Gate 2B Audit**: Evaluates frozen pre-match predictions against recently completed matches.
3. **Phase B1 (Dixon-Coles Optimization)**:
   - Fits Dixon-Coles on active sliding window (4 seasons, 1,170 matches).
   - Tier 1 warm-start optimization $\to$ Tier 2 flat-prior fallback if un-converged.
   - Applies Two-Pass Shrinkage if boundary collapse is detected.
   - Validates Gate 2A and serializes compressed binary artifact into `models`.
   - Precomputes score distributions and probabilities for all 342 scheduled fixtures.
4. **Phase B2 (XGBoost Optimization)**:
   - Builds complete feature matrix across historical window.
   - Trains Booster with L1/L2 regularization (`reg_alpha=0.5`, `reg_lambda=1.0`).
   - Validates Gate 2A and saves binary artifact.
   - Performs atomic `jsonb_set` updates for XGBoost predictions across all 342 fixtures.

---

## 💻 Interactive Dashboard & Simulator

Built with **Next.js 15 (App Router)**, **React 19**, and **Tailwind CSS**:

- **Gameweek Schedule Hub (`/`)**: Displays all scheduled Premier League gameweek fixtures with real-time kickoff timestamps, status badges, and dual-model outcome probability bars.
- **Head-to-Head Simulator (`/simulator`)**:
  - Live team selection with one-click swap.
  - Interactive **5×5 Bivariate Goal Probability Heatmap** truncated to 0–4 goals per side, correctly accounting for tail probability mass.
  - **Honest Match Differentials Table**: Elo difference, rolling 5-match form points difference, shots-on-target difference, and rest days differential.
- **Model Benchmark Showcase (`/models`)**:
  - Historical walk-forward backtest results across locked folds.
  - Evaluates Brier Score, Ranked Probability Score (RPS), Log-Loss, and Accuracy.
  - Statistical significance badges (Wilcoxon Signed-Rank and McNemar's tests).
- **Team Profiles (`/teams/[team]`)**: Latent attack and defense strengths, current window Elo, rolling stats, and retraining staleness tracking badges.

---

## 📁 Repository Layout

```
MatchSense/
├── alembic/                          # PostgreSQL schema migration scripts
├── backend/
│   ├── api/
│   │   ├── dependencies.py           # Dependency injection & model accessors
│   │   ├── main.py                   # FastAPI app factory & CORS middleware
│   │   └── routes/
│   │       ├── health.py             # Health check endpoint (DB + Fixture Feed)
│   │       └── predictions.py        # H2H, Compare, Fixtures, Teams endpoints
│   ├── core/
│   │   ├── config.py                 # Pydantic Settings (.env configuration)
│   │   └── database.py               # SQLAlchemy engine & session factory
│   ├── models/
│   │   └── schemas.py                # ORM models (Match, Team, Fixture, ModelArtifact)
│   └── services/
│       ├── model_manager.py          # Zero-downtime hot-reloading manager
│       └── prediction.py             # Domain prediction service & feature extraction
├── frontend/
│   ├── src/
│   │   ├── app/                      # Next.js 15 App Router pages (/, /simulator, /models, /teams)
│   │   ├── components/               # UI components (Heatmap, ProbabilityBar, FeatureDiffTable)
│   │   └── lib/api.ts                # Typed client API client
│   └── tests/                        # Vitest component & resilience integration tests
├── ml/
│   ├── data/
│   │   ├── football_data_api.py      # Football-Data.org API client
│   │   ├── ingestion.py              # CSV ingestion & Pandera validation
│   │   ├── normalization.py          # Canonical 20-club team name normalization
│   │   └── season.py                 # Dynamic season detection & window derivation
│   ├── evaluation/
│   │   ├── metrics.py                # RPS, Brier Score, Log-Loss
│   │   └── significance.py           # Wilcoxon & McNemar tests
│   ├── features/
│   │   ├── elo.py                    # Window-anchored dynamic Elo engine
│   │   ├── form.py                   # Rolling form & temporal fatigue features
│   │   ├── match_stats.py            # Rolling shots, SOT, corners
│   │   └── pipeline.py               # ~70-feature matrix builder
│   └── models/
│       ├── base.py                   # Abstract predictor interface
│       ├── dixon_coles.py            # Bivariate Poisson MLE with 2-Pass Shrinkage
│       └── xgboost_model.py          # Gradient-boosted predictor with feature extraction
├── scripts/
│   ├── seed_data.py                  # Initial database seeding
│   └── sync_pipeline.py              # Automated weekly ingestion & retrain engine
├── tests/                            # Comprehensive backend test suite (142 tests)
├── docker-compose.yml                # PostgreSQL container definition
└── pyproject.toml                    # uv dependency specification
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.12+**
- **Node.js 18+** & **npm**
- **Docker** & **Docker Compose** (for PostgreSQL)
- **uv** (recommended: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/yashkokane/MatchSense.git
cd MatchSense

# Install Python backend dependencies
uv sync

# Install Frontend dependencies
cd frontend && npm install && cd ..
```

### 2. Environment Setup

Create `.env` in the project root:

```env
DATABASE_URL=postgresql://matchsense:matchsense@localhost:5432/matchsense
FOOTBALL_DATA_API_KEY=your_football_data_org_api_key_here
MODEL_PATH=data/models/dixon_coles_latest.pkl
XGB_MODEL_PATH=data/models/xgboost_latest.pkl
LOG_LEVEL=INFO
```

### 3. Start Database & Run Migrations

```bash
# Start PostgreSQL container
docker compose up -d db

# Run Alembic migrations
uv run alembic upgrade head
```

### 4. Run Data Ingestion & Model Fitting

```bash
# Ingest 4 seasons, fit Dixon-Coles & XGBoost, precompute predictions for all 342 fixtures
uv run python -m scripts.sync_pipeline
```

### 5. Launch Application Services

**Terminal 1: FastAPI Backend**
```bash
uv run uvicorn backend.api.main:app --reload --port 8000
```

**Terminal 2: Next.js Frontend**
```bash
cd frontend && npm run dev
```

Visit:
- **Web Dashboard**: [http://localhost:3000](http://localhost:3000)
- **H2H Simulator**: [http://localhost:3000/simulator](http://localhost:3000/simulator)
- **Model Benchmark**: [http://localhost:3000/models](http://localhost:3000/models)
- **Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Comprehensive Test Suite

The repository maintains strict test coverage across mathematical invariants, temporal boundaries, model optimization, API contracts, and frontend components.

```bash
# Run all 142 backend tests
uv run pytest

# Run with test coverage
uv run pytest --cov=ml --cov=backend

# Run frontend Vitest test suite
cd frontend && npm test
```

### Test Coverage Highlights
- **Mathematical Invariants**: $\sum P(H, D, A) = 1.0$, non-negativity of $\tau(x,y)$, parameter recovery under synthetic data.
- **Temporal Leakage Protection**: Ensures match features on date $T$ never utilize data from date $\ge T$.
- **Optimizer Regularization**: Verifies two-pass shrinkage handles single, simultaneous, and multi-team boundary collapses.
- **Resilience & Failover**: Tests API degradation, database reconnection, and honest UI fallbacks under offline scenarios.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
