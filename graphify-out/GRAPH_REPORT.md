# Graph Report - MatchSense  (2026-09-13)

## Corpus Check
- 48 files · ~16,840 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 481 nodes · 645 edges · 37 communities (21 shown, 1 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 14 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Feature Engineering & Temporal Form
- FastAPI Service & Endpoints
- PredictionService
- Feature Engineering & Temporal Form
- TestPoissonProperties
- TestDixonColesModel
- Base
- BasePredictor
- .fit
- Database Schema & Migrations
- DixonColesModel
- Database Schema & Migrations
- Database Schema & Migrations
- Proposed Changes
- Settled Decisions
- MatchSense ⚽
- TestTauCorrection
- What Was Completed
- test_pipeline.py
- .predict_score_distribution
- dixon_coles.py
- .medium_dataset

## God Nodes (most connected - your core abstractions)
1. `DixonColesModel` - 47 edges
2. `TestDixonColesModel` - 17 edges
3. `parse_season_csv()` - 15 edges
4. `compute_form_features()` - 14 edges
5. `build_match_features()` - 14 edges
6. `_tau()` - 13 edges
7. `PredictionService` - 12 edges
8. `Settled Decisions` - 12 edges
9. `BasePredictor` - 11 edges
10. `Base` - 10 edges

## Surprising Connections (you probably didn't know these)
- `get_model()` --uses--> `DixonColesModel`  [INFERRED]
  backend/api/dependencies.py → ml/models/dixon_coles.py
- `set_model()` --uses--> `DixonColesModel`  [INFERRED]
  backend/api/dependencies.py → ml/models/dixon_coles.py
- `lifespan()` --uses--> `DixonColesModel`  [INFERRED]
  backend/api/main.py → ml/models/dixon_coles.py
- `load_matches_from_db()` --uses--> `Match`  [INFERRED]
  ml/data/loader.py → backend/models/schemas.py
- `PredictionService` --uses--> `DixonColesModel`  [INFERRED]
  backend/services/prediction.py → ml/models/dixon_coles.py

## Import Cycles
- None detected.

## Communities (37 total, 1 thin omitted)

### Community 0 - "Feature Engineering & Temporal Form"
Cohesion: 0.05
Nodes (47): compute_form_features(), compute_home_away_splits(), compute_season_features(), compute_temporal_features(), _empty_form_features(), DataFrame, Timestamp, Recent form and temporal feature engineering. Computes per-team rolling… (+39 more)

### Community 1 - "FastAPI Service & Endpoints"
Cohesion: 0.05
Nodes (40): Dependency injection for FastAPI routes. Holds the global model reference and…, Set the global model reference. Used by lifespan and tests., set_model(), create_app(), lifespan(), FastAPI application factory for MatchSense. Loads the fitted Dixon-Coles model…, Load the model at startup, clean up on shutdown., Create and configure the FastAPI application. (+32 more)

### Community 2 - "PredictionService"
Cohesion: 0.14
Nodes (9): get_model(), Get the loaded model instance. Raises if model not loaded., PredictionService, Prediction service encapsulating prediction domain logic., Get the model instance, falling back to dependency injector., Predict match outcome probabilities, most likely score, and distribution. Args:…, Return sorted list of known teams., Return attack and defense parameters for team. Raises: ValueError: If team is… (+1 more)

### Community 3 - "Feature Engineering & Temporal Form"
Cohesion: 0.07
Nodes (29): compute_implied_probabilities(), download_season_csv(), load_all_seasons(), normalize_team_name(), parse_season_csv(), DataFrame, Path, Data ingestion pipeline for football-data.co.uk CSVs. Downloads, parses,… (+21 more)

### Community 4 - "TestPoissonProperties"
Cohesion: 0.14
Nodes (10): given, settings, Property-based tests for Dixon-Coles model., τ must be positive for typical football scoring rates and empirical ρ., τ must be exactly 1.0 for all scores where both teams score 2+., Score distribution must sum to ~1.0 for any valid matchup., All probabilities must be >= 0., P(H) + P(D) + P(A) must sum to ~1.0 for any matchup. (+2 more)

### Community 5 - "TestDixonColesModel"
Cohesion: 0.06
Nodes (19): Path, Serialize the fitted model to disk. Args: path: File path to save to (typically…, Deserialize a fitted model from disk. Args: path: File path to load from.…, All score probabilities must be >= 0., Most likely score should be reasonable (not negative, not absurd)., Predicting with unknown team should raise ValueError., Predicting without fit() should raise RuntimeError., Save and load should produce identical predictions. (+11 more)

### Community 6 - "Base"
Cohesion: 0.07
Nodes (27): Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online(), Pydantic settings for MatchSense configuration. Loads from environment…, Application configuration loaded from environment variables., Settings, Base (+19 more)

### Community 7 - "BasePredictor"
Cohesion: 0.12
Nodes (12): ABC, BasePredictor, DataFrame, ndarray, Abstract base class for prediction models. All models (Dixon-Coles, XGBoost in…, Interface that every prediction model must implement., Fit the model on historical match data. Args: matches: DataFrame with at…, Predict outcome probabilities for a match. Args: home_team: Canonical name of… (+4 more)

### Community 8 - ".fit"
Cohesion: 0.17
Nodes (9): DataFrame, ndarray, Pack model parameters into a flat vector for the optimizer. Layout: [alpha_2,…, Unpack a flat parameter vector into named parameters. Returns: Tuple of…, Vectorized negative log-likelihood (to minimize). L = -Σ w(t) * [log(τ) +…, Fit the Dixon-Coles model on historical match data. Args: matches: DataFrame…, Compute exponential time-decay weights for each match. More recent matches…, _time_decay_weights() (+1 more)

### Community 9 - "Database Schema & Migrations"
Cohesion: 0.29
Nodes (9): fitted_model(), multi_season_matches(), DataFrame, fixture, Shared test fixtures for MatchSense. Provides sample match data, a fitted…, Small realistic dataset for unit tests. 20 matches across 5 teams in 1 season,…, Two-season dataset for testing season-boundary behavior., A pre-fitted Dixon-Coles model on sample data. (+1 more)

### Community 10 - "DixonColesModel"
Cohesion: 0.16
Nodes (9): DixonColesModel, Return metadata about the fitted model., Dixon-Coles model with time-decay weighting. Parameters are estimated via…, Initialize the model. Args: xi: Time-decay rate per day. Higher = more…, main(), Inspect real model predictions on key fixtures., Test model convergence at realistic scale. This catches optimization bugs that…, Model should converge on 25-team, 500-match dataset. (+1 more)

### Community 11 - "Database Schema & Migrations"
Cohesion: 0.40
Nodes (4): downgrade(), Upgrade schema: create matches, teams, and predictions tables., Downgrade schema: drop predictions, matches, and teams tables., upgrade()

### Community 28 - "Proposed Changes"
Cohesion: 0.05
Nodes (42): 1. Project Scaffolding, 2. Data Ingestion Pipeline, 3. Feature Engineering, 4. Dixon-Coles Model, 5. FastAPI REST API, 6. Database Layer, 7. Testing, 8. Documentation (Basic) (+34 more)

### Community 29 - "Settled Decisions"
Cohesion: 0.09
Nodes (21): Architecture Overview, Core, Data Sources, Deployment, Documentation, Evaluation Strategy (Rigorous), Features, Frontend Dashboard (+13 more)

### Community 30 - "MatchSense ⚽"
Cohesion: 0.11
Nodes (18): 1. Installation, 2. Environment Configuration, 3. Seed Data & Fit Dixon-Coles Model, 4. Run the API Server, API Endpoints, Architecture, Head-to-Head Match Prediction, Health Check (+10 more)

### Community 31 - "TestTauCorrection"
Cohesion: 0.14
Nodes (8): Test the Dixon-Coles low-score correction function., 0-0: correction depends on lambda, mu, rho., 0-1: correction depends on lambda and rho., 1-0: correction depends on mu and rho., 1-1: correction is 1 - rho., All scores > 1-1 get no correction., Tau should be positive for typical rho values., TestTauCorrection

### Community 32 - "What Was Completed"
Cohesion: 0.15
Nodes (12): 1. Project Scaffolding & Configuration, 2. Data Ingestion & Validation, 3. Database & Migrations, 4. Feature Engineering Pipeline, 5. Dixon-Coles Model Implementation, 6. FastAPI Service Layer, 7. Documentation, Automated Test Suite: 57 / 57 Passed (+4 more)

### Community 33 - "test_pipeline.py"
Cohesion: 0.23
Nodes (10): load_matches_from_db(), DataFrame, Session, Database loader utilities for matches. Provides functions to save match…, Save match records from a DataFrame into the database. Skips matches that…, Load matches from database into a pandas DataFrame. Returns DataFrame…, save_matches_to_db(), End-to-end integration tests for the MatchSense pipeline. Tests the full… (+2 more)

### Community 34 - ".predict_score_distribution"
Cohesion: 0.24
Nodes (5): Predict outcome probabilities for a match., Predict the joint score probability distribution., Return attack/defense strengths for all teams., Raise if model has not been fitted., Raise if either team is unknown.

### Community 35 - "dixon_coles.py"
Cohesion: 0.32
Nodes (5): Dixon-Coles model for football match prediction. Implements the Dixon & Coles…, Dixon-Coles correction factor for low-scoring matches. Adjusts the joint…, _tau(), Property-based tests for Poisson model properties. Uses Hypothesis to verify…, Tests for the Dixon-Coles model. Covers: tau correction, parameter packing,…

### Community 36 - ".medium_dataset"
Cohesion: 0.50
Nodes (3): DataFrame, fixture, Generate a synthetic 25-team, 500-match dataset.

## Knowledge Gaps
- **72 isolated node(s):** `matchsense`, `[NEW] `matchsense/pyproject.toml``, `[NEW] `matchsense/docker-compose.yml``, `[NEW] `matchsense/.gitignore``, `[NEW] Directory skeleton` (+67 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 271 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DixonColesModel` connect `DixonColesModel` to `FastAPI Service & Endpoints`, `PredictionService`, `dixon_coles.py`, `.predict_score_distribution`, `TestDixonColesModel`, `Feature Engineering & Temporal Form`, `BasePredictor`, `.fit`, `Database Schema & Migrations`, `test_pipeline.py`, `TestPoissonProperties`?**
  _High betweenness centrality (0.304) - this node is a cross-community bridge._
- **Why does `build_match_features()` connect `Feature Engineering & Temporal Form` to `test_pipeline.py`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `TestDixonColesModel` connect `TestDixonColesModel` to `DixonColesModel`, `dixon_coles.py`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `DixonColesModel` (e.g. with `get_model()` and `set_model()`) actually correct?**
  _`DixonColesModel` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `matchsense`, `[NEW] `matchsense/pyproject.toml``, `[NEW] `matchsense/docker-compose.yml`` to the rest of the system?**
  _72 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Feature Engineering & Temporal Form` be split into smaller, more focused modules?**
  _Cohesion score 0.05182443151771549 - nodes in this community are weakly interconnected._
- **Should `FastAPI Service & Endpoints` be split into smaller, more focused modules?**
  _Cohesion score 0.05224963715529753 - nodes in this community are weakly interconnected._