# MatchSense ⚽

> **Premier League Match Predictor** powered by the Dixon-Coles model with time-decay weighting, robust feature engineering, and a production-grade FastAPI service.

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![uv](https://img.shields.io/badge/uv-fast%20packaging-purple.svg)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Overview

**MatchSense** predicts English Premier League match outcomes (probabilities for Home Win, Draw, Away Win) and full score distributions using the bivariate Poisson framework established by **Dixon & Coles (1997)**.

It improves upon naive independent Poisson models by:
1. **Accounting for correlation in low scorelines** ($0\text{--}0, 1\text{--}0, 0\text{--}1, 1\text{--}1$) via the $\tau(x, y)$ adjustment parameter $\rho$.
2. **Applying exponential time-decay weighting** ($\xi = 0.005$ per day) so recent matches carry more influence on team strength estimates than older matches.
3. **Imposing identifiability constraints** by anchoring a stable reference team's attack strength ($\alpha = 1.0$) rather than fighting optimizer gradients.
4. **Preventing data leakage** with strict chronological cutoffs and resetting rolling form windows at season boundaries (no cross-division carryover).

---

## Architecture

```mermaid
flowchart TD
    subgraph Data Layer
        FD[football-data.co.uk CSVs] --> ING[ml/data/ingestion.py]
        ING --> PAN[Pandera Schema Validation]
        PAN --> DB[(PostgreSQL Database)]
    end

    subgraph Modeling Layer
        DB --> FE[ml/features/pipeline.py]
        FE --> FORM[Form & Temporal Features]
        FE --> H2H[Head-to-Head Features]
        DB --> DC[ml/models/dixon_coles.py]
        DC --> MLE[Scipy L-BFGS-B Optimization]
        MLE --> MODEL[Serialized Model (.pkl)]
    end

    subgraph Service & API Layer
        MODEL --> SVC[backend/services/prediction.py]
        SVC --> API[FastAPI REST API]
        API --> H2H_EP["/api/v1/predictions/head-to-head"]
        API --> TEAMS_EP["/api/v1/teams"]
        API --> HEALTH_EP["/api/v1/health"]
    end
```

---

## Mathematical Formulation

The expected goals for home team $i$ facing away team $j$ are modeled as:
$$\lambda_{ij} = \alpha_i \beta_j \gamma$$
$$\mu_{ij} = \alpha_j \beta_i$$

where:
- $\alpha_i > 0$: Attack strength of team $i$
- $\beta_j > 0$: Defense vulnerability of team $j$
- $\gamma > 0$: Overall home ground advantage
- $\xi = 0.005$: Exponential time decay parameter, match weight $w(t) = e^{-\xi(t_{\max} - t)}$

Joint score probabilities $P(X=x, Y=y)$ are computed as:
$$P(X=x, Y=y) = \tau_{x,y}(\lambda, \mu, \rho) \cdot \frac{\lambda^x e^{-\lambda}}{x!} \cdot \frac{\mu^y e^{-\mu}}{y!}$$

The correction factor $\tau_{x,y}$ accounts for interdependence in low-scoring games:
$$\tau_{x,y}(\lambda, \mu, \rho) = \begin{cases}
1 - \lambda \mu \rho & x=0, y=0 \\
1 + \lambda \rho & x=0, y=1 \\
1 + \mu \rho & x=1, y=0 \\
1 - \rho & x=1, y=1 \\
1 & \text{otherwise}
\end{cases}$$

---

## Project Structure

```
MatchSense/
├── alembic/                      # Database migrations
│   └── versions/                 # Version scripts
├── backend/
│   ├── api/
│   │   ├── dependencies.py       # Dependency injection
│   │   ├── main.py               # FastAPI application factory
│   │   └── routes/
│   │       ├── health.py         # Health check endpoint
│   │       └── predictions.py    # Head-to-head and team routes
│   ├── core/
│   │   ├── config.py             # Pydantic Settings
│   │   └── database.py           # SQLAlchemy engine & session
│   ├── models/
│   │   └── schemas.py            # ORM models (Match, Team, Prediction)
│   └── services/
│       └── prediction.py         # Prediction domain service
├── ml/
│   ├── data/
│   │   ├── ingestion.py          # CSV downloader, parser, normalizer
│   │   ├── loader.py             # Database read/write helpers
│   │   └── schemas.py            # Pandera validation schemas
│   ├── features/
│   │   ├── form.py               # Rolling form & temporal features
│   │   ├── h2h.py                # Head-to-head features
│   │   └── pipeline.py           # Feature orchestrator
│   └── models/
│       ├── base.py               # Abstract predictor interface
│       └── dixon_coles.py        # Dixon-Coles implementation
├── scripts/
│   └── seed_data.py              # Download historical data & fit model
├── tests/
│   ├── conftest.py               # Test fixtures
│   ├── integration/
│   │   └── test_pipeline.py      # Full lifecycle integration tests
│   ├── property/
│   │   └── test_poisson_properties.py  # Hypothesis invariant tests
│   └── unit/
│       ├── test_api.py           # FastAPI endpoint tests
│       ├── test_dixon_coles.py   # Model math & convergence tests
│       ├── test_features.py      # Feature engineering tests
│       └── test_ingestion.py     # Data ingestion & schema tests
├── docker-compose.yml            # PostgreSQL + API containers
├── Dockerfile                    # API container image
└── pyproject.toml                # uv build configuration
```

---

## Quickstart

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or standard `pip`
- Docker Desktop (optional, for PostgreSQL)

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yashkokane/MatchSense.git
cd MatchSense

# Install dependencies using uv
uv sync
```

### 2. Environment Configuration

```bash
cp .env.example .env
```

### 3. Seed Data & Fit Dixon-Coles Model

Run the seed script to download the last 4 Premier League seasons, validate with Pandera schemas, fit the Dixon-Coles model, and persist it to disk:

```bash
uv run python scripts/seed_data.py
```

### 4. Run the API Server

```bash
uv run uvicorn backend.api.main:app --reload --port 8000
```

Access the interactive API documentation at:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## API Endpoints

### Health Check
`GET /api/v1/health`
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "dixon_coles",
  "n_teams": 28,
  "n_matches": 1280,
  "home_advantage": 1.284,
  "rho": -0.062,
  "reference_team": "Arsenal"
}
```

### Head-to-Head Match Prediction
`POST /api/v1/predictions/head-to-head`
```bash
curl -X POST http://localhost:8000/api/v1/predictions/head-to-head \
  -H "Content-Type: application/json" \
  -d '{"home_team": "Arsenal", "away_team": "Chelsea"}'
```

Response:
```json
{
  "home_team": "Arsenal",
  "away_team": "Chelsea",
  "prob_home": 0.5412,
  "prob_draw": 0.2315,
  "prob_away": 0.2273,
  "predicted_score": {
    "home": 2,
    "away": 1
  },
  "score_distribution": [
    [0.052, 0.068, 0.035, "..."],
    ["..."]
  ],
  "model": "dixon_coles"
}
```

### Team Strengths & Team List
- `GET /api/v1/teams`: List all known canonical teams
- `GET /api/v1/teams/{team_name}/strengths`: Retrieve estimated attack and defense parameters ($\alpha, \beta$)

---

## Testing

MatchSense maintains a comprehensive test suite across unit, property-based, and integration tests:

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=ml --cov=backend --cov-report=term-missing

# Run property-based tests only
uv run pytest tests/property/

# Run integration tests only
uv run pytest tests/integration/
```

### Invariants Tested:
- **Mathematical Invariants**: $\tau > 0$ for empirical ranges, $\sum_{i,j} P(i, j) \approx 1.0$, $P(H) + P(D) + P(A) = 1.0$.
- **Temporal Leakage**: Features computed for date $T$ strictly ignore matches on or after $T$.
- **Season Boundary**: Rolling forms reset at the start of every season; newly promoted teams receive null form flags.
- **Reference Constraint**: Chosen reference team has $\alpha \equiv 1.0$ post-convergence.
- **Scale Convergence**: Synthetic 25-team, 500-match convergence test ensures optimization stability at realistic league scale.

---

## Roadmap

- [x] **Phase 1: Dixon-Coles Foundation**
  - Historical data ingestion from football-data.co.uk (4 seasons)
  - Pandera schema validation
  - Full Dixon-Coles MLE with time-decay and reference constraint
  - Feature engineering (rolling form, H2H, home/away splits)
  - FastAPI endpoints and Docker configuration
  - 57 automated tests (unit, property, integration)
- [ ] **Phase 2: XGBoost Hybrid & Feature Store**
  - XGBoost residual predictor trained on Dixon-Coles expected goals
  - Elo ratings and rolling xG integration
  - Walk-forward temporal cross-validation
  - Comprehensive backtesting & Brier score evaluation
- [ ] **Phase 3: Live Ingestion & Interactive Dashboard**
  - Football-Data.org API weekly sync
  - Next.js dashboard with interactive match simulator and live tracking
