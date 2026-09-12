# Graph Report - MatchSense  (2026-09-13)

## Corpus Check
- 66 files · ~31,690 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 682 nodes · 920 edges · 48 communities (32 shown, 2 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 15 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d12a8c78`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Feature Engineering & Temporal Form
- main.py
- test_pipeline.py
- Feature Engineering & Temporal Form
- DixonColesModel
- TestDixonColesModel
- Base
- dixon_coles.py
- .fit
- Database Schema & Migrations
- .load
- Database Schema & Migrations
- evaluation/__init__.py
- Database Schema & Migrations
- Proposed Changes
- Settled Decisions
- MatchSense ⚽
- _tau
- What Was Completed
- evaluate.py
- .predict_score_distribution
- MatchSense — Evaluation Suite Design Spec (Phase 2A)
- evaluate_significance_suite
- predictions.py
- Evaluation Core (`ml/evaluation/`)
- compute_calibration
- run_walk_forward_cv
- test_metrics.py
- MatchSense — Phase 1 Implementation & Training Walkthrough
- metrics.py
- Global Constraints
- 2. Statistical Significance vs Baselines (Primary: Per-Fold Independent)
- .predict_score_distribution
- compute_log_loss

## God Nodes (most connected - your core abstractions)
1. `DixonColesModel` - 52 edges
2. `TestDixonColesModel` - 18 edges
3. `parse_season_csv()` - 15 edges
4. `compute_form_features()` - 14 edges
5. `build_match_features()` - 14 edges
6. `run_walk_forward_cv()` - 13 edges
7. `BasePredictor` - 13 edges
8. `_tau()` - 13 edges
9. `PredictionService` - 12 edges
10. `Settled Decisions` - 12 edges

## Surprising Connections (you probably didn't know these)
- `get_model()` --uses--> `DixonColesModel`  [INFERRED]
  backend/api/dependencies.py → ml/models/dixon_coles.py
- `set_model()` --uses--> `DixonColesModel`  [INFERRED]
  backend/api/dependencies.py → ml/models/dixon_coles.py
- `lifespan()` --uses--> `DixonColesModel`  [INFERRED]
  backend/api/main.py → ml/models/dixon_coles.py
- `PredictionService` --uses--> `DixonColesModel`  [INFERRED]
  backend/services/prediction.py → ml/models/dixon_coles.py
- `main()` --uses--> `DixonColesModel`  [INFERRED]
  scripts/inspect_predictions.py → ml/models/dixon_coles.py

## Import Cycles
- None detected.

## Communities (48 total, 2 thin omitted)

### Community 0 - "Feature Engineering & Temporal Form"
Cohesion: 0.05
Nodes (47): compute_form_features(), compute_home_away_splits(), compute_season_features(), compute_temporal_features(), _empty_form_features(), DataFrame, Timestamp, Recent form and temporal feature engineering. Computes per-team rolling… (+39 more)

### Community 1 - "main.py"
Cohesion: 0.08
Nodes (24): get_model(), Dependency injection for FastAPI routes. Holds the global model reference and…, Get the loaded model instance. Raises if model not loaded., Set the global model reference. Used by lifespan and tests., set_model(), create_app(), lifespan(), FastAPI application factory for MatchSense. Loads the fitted Dixon-Coles model… (+16 more)

### Community 2 - "test_pipeline.py"
Cohesion: 0.14
Nodes (10): PredictionService, Prediction service encapsulating prediction domain logic., Get the model instance, falling back to dependency injector., Predict match outcome probabilities, most likely score, and distribution. Args:…, Return sorted list of known teams., Return attack and defense parameters for team. Raises: ValueError: If team is…, Service providing match prediction operations., End-to-end integration tests for the MatchSense pipeline. Tests the full… (+2 more)

### Community 3 - "Feature Engineering & Temporal Form"
Cohesion: 0.07
Nodes (29): compute_implied_probabilities(), download_season_csv(), load_all_seasons(), normalize_team_name(), parse_season_csv(), DataFrame, Path, Data ingestion pipeline for football-data.co.uk CSVs. Downloads, parses,… (+21 more)

### Community 4 - "DixonColesModel"
Cohesion: 0.13
Nodes (11): DixonColesModel, Return metadata about the fitted model., Dixon-Coles model with time-decay weighting. Parameters are estimated via…, Initialize the model. Args: xi: Time-decay rate per day. Higher = more…, Property-based tests for Poisson model properties. Uses Hypothesis to verify…, Property-based tests for Dixon-Coles model., Score distribution must sum to ~1.0 for any valid matchup., All probabilities must be >= 0. (+3 more)

### Community 5 - "TestDixonColesModel"
Cohesion: 0.07
Nodes (16): All score probabilities must be >= 0., Most likely score should be reasonable (not negative, not absurd)., Predicting with unknown team should raise ValueError when allow_unknown=False., Predicting with unknown team should succeed when allow_unknown=True., Predicting without fit() should raise RuntimeError., get_team_strengths() should return dict for all teams., get_model_info() should return expected metadata., Test model fitting and prediction on sample data. (+8 more)

### Community 6 - "Base"
Cohesion: 0.06
Nodes (34): Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online(), Pydantic settings for MatchSense configuration. Loads from environment…, Application configuration loaded from environment variables., Settings, Base (+26 more)

### Community 7 - "dixon_coles.py"
Cohesion: 0.14
Nodes (10): ABC, BasePredictor, DataFrame, Abstract base class for prediction models. All models (Dixon-Coles, XGBoost in…, Interface that every prediction model must implement., Fit the model on historical match data. Args: matches: DataFrame with at…, Predict outcome probabilities for a match. Args: home_team: Canonical name of…, Return estimated attack/defense strengths for all teams. Returns: Dict mapping… (+2 more)

### Community 8 - ".fit"
Cohesion: 0.17
Nodes (9): DataFrame, ndarray, Pack model parameters into a flat vector for the optimizer. Layout: [alpha_2,…, Unpack a flat parameter vector into named parameters. Returns: Tuple of…, Vectorized negative log-likelihood (to minimize). L = -Σ w(t) * [log(τ) +…, Fit the Dixon-Coles model on historical match data. Args: matches: DataFrame…, Compute exponential time-decay weights for each match. More recent matches…, _time_decay_weights() (+1 more)

### Community 9 - "Database Schema & Migrations"
Cohesion: 0.29
Nodes (9): fitted_model(), multi_season_matches(), DataFrame, fixture, Shared test fixtures for MatchSense. Provides sample match data, a fitted…, Small realistic dataset for unit tests. 20 matches across 5 teams in 1 season,…, Two-season dataset for testing season-boundary behavior., A pre-fitted Dixon-Coles model on sample data. (+1 more)

### Community 10 - ".load"
Cohesion: 0.20
Nodes (6): Path, Serialize the fitted model to disk. Args: path: File path to save to (typically…, Deserialize a fitted model from disk. Args: path: File path to load from.…, main(), Inspect real model predictions on key fixtures., Save and load should produce identical predictions.

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

### Community 31 - "_tau"
Cohesion: 0.08
Nodes (21): given, Dixon-Coles correction factor for low-scoring matches. Adjusts the joint…, _tau(), settings, τ must be positive for typical football scoring rates and empirical ρ., τ must be exactly 1.0 for all scores where both teams score 2+., DataFrame, fixture (+13 more)

### Community 32 - "What Was Completed"
Cohesion: 0.15
Nodes (12): 1. Project Scaffolding & Configuration, 2. Data Ingestion & Validation, 3. Database & Migrations, 4. Feature Engineering Pipeline, 5. Dixon-Coles Model Implementation, 6. FastAPI Service Layer, 7. Documentation, Automated Test Suite: 57 / 57 Passed (+4 more)

### Community 33 - "evaluate.py"
Cohesion: 0.07
Nodes (31): BacktestResult, DataFrame, Financial backtesting engine with pre-gameweek batch staking., Run financial backtest with gameweek batch sizing and conflict guards. Args:…, simulate_betting(), EvaluationReport, Any, Comprehensive evaluation scorecard generator. (+23 more)

### Community 34 - ".predict_score_distribution"
Cohesion: 0.24
Nodes (5): Predict outcome probabilities for a match., Predict the joint score probability distribution., Return attack/defense strengths for all teams., Raise if model has not been fitted., Raise if either team is unknown.

### Community 35 - "MatchSense — Evaluation Suite Design Spec (Phase 2A)"
Cohesion: 0.07
Nodes (28): 1. Executive Summary, 2. Architecture & Module Structure, 3.1 Ranked Probability Score (RPS), 3.2 Multi-Category Brier Score, 3.3 Multi-Class Log-Loss (Cross-Entropy), 3.4 Categorical Accuracy, 3. Mathematical Foundations & Metrics (`ml/evaluation/metrics.py`), 4.1 Wilcoxon Signed-Rank Test on Paired $\Delta \text{RPS}$ (+20 more)

### Community 36 - "evaluate_significance_suite"
Cohesion: 0.12
Nodes (23): evaluate_significance_suite(), mcnemar_accuracy_test(), McNemarResult, Any, DataFrame, ndarray, Hypothesis testing for comparative model evaluation., Paired Wilcoxon signed-rank test on match-by-match RPS differences. Uses Pratt… (+15 more)

### Community 37 - "predictions.py"
Cohesion: 0.15
Nodes (18): get_team_strength(), HeadToHeadRequest, list_teams(), MatchPrediction, predict_head_to_head(), get, Prediction endpoints for MatchSense API. Provides head-to-head match…, Request body for a head-to-head prediction. (+10 more)

### Community 38 - "Evaluation Core (`ml/evaluation/`)"
Cohesion: 0.12
Nodes (16): Automated Tests, Evaluation Core (`ml/evaluation/`), Manual Verification & Benchmark Execution, MatchSense — Phase 2A Evaluation Suite Implementation Plan, [NEW] [`ml/evaluation/backtest.py`](file:///d:/Yash%20Kokane/Projects/MatchSense/ml/evaluation/backtest.py), [NEW] [`ml/evaluation/calibration.py`](file:///d:/Yash%20Kokane/Projects/MatchSense/ml/evaluation/calibration.py), [NEW] [`ml/evaluation/metrics.py`](file:///d:/Yash%20Kokane/Projects/MatchSense/ml/evaluation/metrics.py), [NEW] [`ml/evaluation/report.py`](file:///d:/Yash%20Kokane/Projects/MatchSense/ml/evaluation/report.py) (+8 more)

### Community 39 - "compute_calibration"
Cohesion: 0.19
Nodes (14): BinSummary, CalibrationResult, compute_calibration(), _compute_class_calibration(), ndarray, Reliability diagrams and calibration metrics., Compute Expected Calibration Error and reliability tables across H/D/A outcomes., Unit tests for calibration and expected calibration error (ECE). (+6 more)

### Community 40 - "run_walk_forward_cv"
Cohesion: 0.18
Nodes (12): _odds_to_implied(), DataFrame, Walk-forward cross validation engine with parallel baseline evaluation., Convert decimal odds to overround-removed implied probabilities., Execute rolling fixed-window walk-forward cross validation gameweek-by-…, run_walk_forward_cv(), fixture, Unit tests for rolling fixed-window walk-forward cross validation. (+4 more)

### Community 41 - "test_metrics.py"
Cohesion: 0.23
Nodes (11): compute_rps(), Compute Ranked Probability Score for 3-outcome ordered events (H < D < A). RPS…, Unit tests for probabilistic and categorical evaluation metrics., Certain home win prediction when home win occurs should give RPS = 0., Certain away win prediction when home win occurs should give maximum RPS = 1., Predicting Draw when Home wins should give lower RPS penalty than predicting…, RPS should handle 2D batch arrays correctly., test_rps_adjacent_error_less_than_severe() (+3 more)

### Community 42 - "MatchSense — Phase 1 Implementation & Training Walkthrough"
Cohesion: 0.18
Nodes (10): 1. Resolution of Data Churn & Season Scope, 2. Model Training & Optimization Performance, 3. Team Strength Sanity Check, 4. Real Matchup Smoke Tests, 5. Verification & Code Quality Status, Bottom 5 Defenses (Highest Conceded Expected Goals $\beta$), Fitted Global Parameters, MatchSense — Phase 1 Implementation & Training Walkthrough (+2 more)

### Community 43 - "metrics.py"
Cohesion: 0.20
Nodes (10): compute_accuracy(), compute_brier_score(), ndarray, Mathematical evaluation metrics for football match prediction., Compute multi-category Brier score. Args: probs: Array of shape (N, 3).…, Compute binary classification correctness. Args: probs: Array of shape (N, 3).…, Multi-category Brier score ranges from 0.0 to 2.0., Accuracy evaluates whether argmax matches true class. (+2 more)

### Community 44 - "Global Constraints"
Cohesion: 0.20
Nodes (9): Evaluation Suite (Phase 2A) Implementation Plan, Global Constraints, Task 1: Probabilistic & Categorical Metrics, Task 2: Hypothesis Testing Engine, Task 3: Calibration & Expected Calibration Error (ECE), Task 4: Financial Backtesting & Betting Simulator, Task 5: Walk-Forward CV Orchestrator & Baselines, Task 6: Structured Report Container & Formatters (+1 more)

### Community 45 - "2. Statistical Significance vs Baselines (Primary: Per-Fold Independent)"
Cohesion: 0.20
Nodes (9): 1. Out-of-Sample Performance by Season (Rolling 4-Season Window), 2. Statistical Significance vs Baselines (Primary: Per-Fold Independent), 3. Financial Simulation & ROI (Edge >= 5%), 4. Calibration & Reliability Summary, Fold Season: `2023-24`, Fold Season: `2024-25`, Fold Season: `2025-26`, MatchSense — Model Evaluation Report: `dixon_coles` (+1 more)

### Community 46 - ".predict_score_distribution"
Cohesion: 0.40
Nodes (3): ndarray, Predict the joint score probability distribution. Args: home_team: Canonical…, Predict the single most likely scoreline. Args: home_team: Canonical name of…

### Community 47 - "compute_log_loss"
Cohesion: 0.50
Nodes (4): compute_log_loss(), Compute multi-class cross-entropy log-loss. Args: probs: Array of shape (N, 3).…, Log loss clips probabilities to prevent -inf log(0)., test_log_loss_clipping()

## Knowledge Gaps
- **125 isolated node(s):** `matchsense`, `[NEW] `matchsense/pyproject.toml``, `[NEW] `matchsense/docker-compose.yml``, `[NEW] `matchsense/.gitignore``, `[NEW] Directory skeleton` (+120 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 389 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DixonColesModel` connect `DixonColesModel` to `main.py`, `test_pipeline.py`, `.predict_score_distribution`, `evaluate.py`, `Feature Engineering & Temporal Form`, `TestDixonColesModel`, `dixon_coles.py`, `.fit`, `Database Schema & Migrations`, `.load`, `run_walk_forward_cv`, `_tau`?**
  _High betweenness centrality (0.271) - this node is a cross-community bridge._
- **Why does `build_match_features()` connect `Feature Engineering & Temporal Form` to `test_pipeline.py`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Why does `TestDixonColesModel` connect `TestDixonColesModel` to `.load`, `DixonColesModel`, `_tau`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `DixonColesModel` (e.g. with `get_model()` and `set_model()`) actually correct?**
  _`DixonColesModel` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `matchsense`, `[NEW] `matchsense/pyproject.toml``, `[NEW] `matchsense/docker-compose.yml`` to the rest of the system?**
  _125 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Feature Engineering & Temporal Form` be split into smaller, more focused modules?**
  _Cohesion score 0.05182443151771549 - nodes in this community are weakly interconnected._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07777777777777778 - nodes in this community are weakly interconnected._