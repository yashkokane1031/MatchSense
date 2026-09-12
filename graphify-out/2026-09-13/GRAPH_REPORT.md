# Graph Report - MatchSense  (2026-09-12)

## Corpus Check
- Corpus is ~15,938 words - fits in a single context window. You may not need a graph.

## Summary
- 381 nodes · 548 edges · 28 communities (12 shown, 1 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Feature Engineering & Temporal Form
- FastAPI Service & Endpoints
- Dixon-Coles Bivariate Poisson Model
- Feature Engineering & Temporal Form
- Dixon-Coles Bivariate Poisson Model
- Dixon-Coles Bivariate Poisson Model
- Data Ingestion & Schemas
- Dixon-Coles Bivariate Poisson Model
- Dixon-Coles Bivariate Poisson Model
- Database Schema & Migrations
- Dixon-Coles Bivariate Poisson Model
- Database Schema & Migrations
- Database Schema & Migrations

## God Nodes (most connected - your core abstractions)
1. `DixonColesModel` - 45 edges
2. `TestDixonColesModel` - 17 edges
3. `parse_season_csv()` - 15 edges
4. `compute_form_features()` - 14 edges
5. `build_match_features()` - 14 edges
6. `_tau()` - 14 edges
7. `PredictionService` - 12 edges
8. `BasePredictor` - 11 edges
9. `Base` - 10 edges
10. `compute_h2h_features()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `TestMediumScaleConvergence` --uses--> `DixonColesModel`  [INFERRED]
  tests/unit/test_dixon_coles.py → ml/models/dixon_coles.py
- `set_model()` --uses--> `DixonColesModel`  [INFERRED]
  backend/api/dependencies.py → ml/models/dixon_coles.py
- `lifespan()` --uses--> `DixonColesModel`  [INFERRED]
  backend/api/main.py → ml/models/dixon_coles.py
- `TestPoissonProperties` --uses--> `DixonColesModel`  [INFERRED]
  tests/property/test_poisson_properties.py → ml/models/dixon_coles.py
- `TestDixonColesModel` --uses--> `DixonColesModel`  [INFERRED]
  tests/unit/test_dixon_coles.py → ml/models/dixon_coles.py

## Import Cycles
- None detected.

## Communities (28 total, 1 thin omitted)

### Community 0 - "Feature Engineering & Temporal Form"
Cohesion: 0.05
Nodes (47): compute_form_features(), compute_home_away_splits(), compute_season_features(), compute_temporal_features(), _empty_form_features(), DataFrame, Timestamp, Recent form and temporal feature engineering. Computes per-team rolling… (+39 more)

### Community 1 - "FastAPI Service & Endpoints"
Cohesion: 0.05
Nodes (40): Dependency injection for FastAPI routes. Holds the global model reference and…, Set the global model reference. Used by lifespan and tests., set_model(), create_app(), lifespan(), FastAPI application factory for MatchSense. Loads the fitted Dixon-Coles model…, Load the model at startup, clean up on shutdown., Create and configure the FastAPI application. (+32 more)

### Community 2 - "Dixon-Coles Bivariate Poisson Model"
Cohesion: 0.06
Nodes (30): get_model(), Get the loaded model instance. Raises if model not loaded., Match, A single Premier League match with result, stats, and bookmaker odds., PredictionService, Prediction service encapsulating prediction domain logic., Get the model instance, falling back to dependency injector., Predict match outcome probabilities, most likely score, and distribution. Args:… (+22 more)

### Community 3 - "Feature Engineering & Temporal Form"
Cohesion: 0.07
Nodes (29): compute_implied_probabilities(), download_season_csv(), load_all_seasons(), normalize_team_name(), parse_season_csv(), DataFrame, Path, Data ingestion pipeline for football-data.co.uk CSVs. Downloads, parses,… (+21 more)

### Community 4 - "Dixon-Coles Bivariate Poisson Model"
Cohesion: 0.07
Nodes (22): given, Dixon-Coles correction factor for low-scoring matches. Adjusts the joint…, _tau(), settings, Property-based tests for Poisson model properties. Uses Hypothesis to verify…, Property-based tests for Dixon-Coles model., τ must be positive for typical football scoring rates and empirical ρ., τ must be exactly 1.0 for all scores where both teams score 2+. (+14 more)

### Community 5 - "Dixon-Coles Bivariate Poisson Model"
Cohesion: 0.06
Nodes (19): Path, Serialize the fitted model to disk. Args: path: File path to save to (typically…, Deserialize a fitted model from disk. Args: path: File path to load from.…, All score probabilities must be >= 0., Most likely score should be reasonable (not negative, not absurd)., Predicting with unknown team should raise ValueError., Predicting without fit() should raise RuntimeError., Save and load should produce identical predictions. (+11 more)

### Community 6 - "Data Ingestion & Schemas"
Cohesion: 0.08
Nodes (25): Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online(), Pydantic settings for MatchSense configuration. Loads from environment…, Application configuration loaded from environment variables., Settings, Base (+17 more)

### Community 7 - "Dixon-Coles Bivariate Poisson Model"
Cohesion: 0.11
Nodes (13): ABC, BasePredictor, DataFrame, ndarray, Abstract base class for prediction models. All models (Dixon-Coles, XGBoost in…, Interface that every prediction model must implement., Fit the model on historical match data. Args: matches: DataFrame with at…, Predict outcome probabilities for a match. Args: home_team: Canonical name of… (+5 more)

### Community 8 - "Dixon-Coles Bivariate Poisson Model"
Cohesion: 0.18
Nodes (9): DataFrame, ndarray, Pack model parameters into a flat vector for the optimizer. Layout: [alpha_2,…, Unpack a flat parameter vector into named parameters. Returns: Tuple of…, Negative log-likelihood (to minimize). L = -Σ w(t) * [log(τ) +…, Fit the Dixon-Coles model on historical match data. Args: matches: DataFrame…, Compute exponential time-decay weights for each match. More recent matches…, _time_decay_weights() (+1 more)

### Community 9 - "Database Schema & Migrations"
Cohesion: 0.29
Nodes (9): fitted_model(), multi_season_matches(), DataFrame, fixture, Shared test fixtures for MatchSense. Provides sample match data, a fitted…, Small realistic dataset for unit tests. 20 matches across 5 teams in 1 season,…, Two-season dataset for testing season-boundary behavior., A pre-fitted Dixon-Coles model on sample data. (+1 more)

### Community 10 - "Dixon-Coles Bivariate Poisson Model"
Cohesion: 0.25
Nodes (6): DataFrame, fixture, Test model convergence at realistic scale. This catches optimization bugs that…, Generate a synthetic 25-team, 500-match dataset., Model should converge on 25-team, 500-match dataset., TestMediumScaleConvergence

### Community 11 - "Database Schema & Migrations"
Cohesion: 0.40
Nodes (4): downgrade(), Upgrade schema: create matches, teams, and predictions tables., Downgrade schema: drop predictions, matches, and teams tables., upgrade()

## Knowledge Gaps
- **1 isolated node(s):** `matchsense`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 195 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DixonColesModel` connect `Dixon-Coles Bivariate Poisson Model` to `FastAPI Service & Endpoints`, `Feature Engineering & Temporal Form`, `Dixon-Coles Bivariate Poisson Model`, `Dixon-Coles Bivariate Poisson Model`, `Dixon-Coles Bivariate Poisson Model`, `Dixon-Coles Bivariate Poisson Model`, `Database Schema & Migrations`, `Dixon-Coles Bivariate Poisson Model`?**
  _High betweenness centrality (0.473) - this node is a cross-community bridge._
- **Why does `build_match_features()` connect `Feature Engineering & Temporal Form` to `Dixon-Coles Bivariate Poisson Model`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Why does `TestDixonColesModel` connect `Dixon-Coles Bivariate Poisson Model` to `Dixon-Coles Bivariate Poisson Model`, `Dixon-Coles Bivariate Poisson Model`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `DixonColesModel` (e.g. with `get_model()` and `set_model()`) actually correct?**
  _`DixonColesModel` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `matchsense` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Feature Engineering & Temporal Form` be split into smaller, more focused modules?**
  _Cohesion score 0.05182443151771549 - nodes in this community are weakly interconnected._
- **Should `FastAPI Service & Endpoints` be split into smaller, more focused modules?**
  _Cohesion score 0.05224963715529753 - nodes in this community are weakly interconnected._