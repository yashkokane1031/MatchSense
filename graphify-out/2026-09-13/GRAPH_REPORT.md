# Graph Report - MatchSense  (2026-09-13)

## Corpus Check
- 97 files · ~71,389 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1075 nodes · 1536 edges · 85 communities (63 shown, 7 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 34 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5a14114d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_features.py
- test_api.py
- PredictionService
- parse_season_csv
- TestPoissonProperties
- TestDixonColesModel
- test_pipeline.py
- BasePredictor
- ndarray
- Database Schema & Migrations
- Phase 2B Design Specification: Advanced Features & XGBoost Classifier
- Database Schema & Migrations
- evaluation/__init__.py
- Database Schema & Migrations
- Proposed Changes
- Settled Decisions
- MatchSense ⚽
- _tau
- What Was Completed
- simulate_betting
- DixonColesModel
- MatchSense — Evaluation Suite Design Spec (Phase 2A)
- wilcoxon_rps_test
- predictions.py
- Evaluation Core (`ml/evaluation/`)
- compute_calibration
- mini_league_dataset
- MatchSense — Phase 2B Implementation and Evaluation Walkthrough
- MatchSense — Phase 1 Implementation & Training Walkthrough
- EloEngine
- Global Constraints
- 2. Statistical Significance vs Baselines (Primary: Per-Fold Independent)
- .predict_score_distribution
- ModelManager
- run_walk_forward_cv
- pipeline.py
- MatchSense — Phase 2B Implementation and Evaluation Walkthrough
- Dixon-Coles Convergence Audit: Walk-Forward CV (114 Gameweek Refits)
- Proposed Changes
- MatchSense — Phase 3: Live Serving & Automation Pipeline Specification
- compute_form_features
- compute_temporal_features
- compute_match_stats_features
- Tasks
- 2. Statistical Significance vs Baselines (Primary: Per-Fold Independent)
- 2. Benchmark Evaluation Results (Dixon-Coles vs Baselines)
- form.py
- MatchSense — Multi-Model Comparative Evaluation: XGBoost vs. Dixon-Coles
- sync_pipeline.py
- build_match_features
- XGBoostPredictor
- MockXGBModel
- test_api_phase3.py
- EvaluationReport
- .fit
- evaluate.py
- Base
- config.py
- ModelArtifact
- main.py
- Global Constraints
- ComparisonReport
- test_sync_pipeline.py
- MockRecoveryModel
- 2. Key Architectural Invariants & Verified Solutions
- TestMediumScaleConvergence
- TestPredictionEndpoints
- TestTeamEndpoints
- TestHealthEndpoint
- synthetic_seasons_data

## God Nodes (most connected - your core abstractions)
1. `DixonColesModel` - 50 edges
2. `BasePredictor` - 29 edges
3. `XGBoostPredictor` - 27 edges
4. `Fixture` - 21 edges
5. `build_match_features()` - 20 edges
6. `TestDixonColesModel` - 18 edges
7. `Base` - 17 edges
8. `parse_season_csv()` - 17 edges
9. `PredictionService` - 16 edges
10. `run_walk_forward_cv()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `set_model()` --uses--> `BasePredictor`  [INFERRED]
  backend/api/dependencies.py → ml/models/base.py
- `test_db()` --uses--> `Base`  [INFERRED]
  tests/integration/test_pipeline.py → backend/core/database.py
- `test_db()` --uses--> `Base`  [INFERRED]
  tests/integration/test_sync_pipeline.py → backend/core/database.py
- `db_session()` --uses--> `Base`  [INFERRED]
  tests/unit/test_schemas_phase3.py → backend/core/database.py
- `load_matches_from_db()` --uses--> `Match`  [INFERRED]
  ml/data/loader.py → backend/models/schemas.py

## Import Cycles
- None detected.

## Communities (85 total, 7 thin omitted)

### Community 0 - "test_features.py"
Cohesion: 0.16
Nodes (12): compute_h2h_features(), _empty_h2h_features(), DataFrame, Timestamp, Head-to-head feature engineering. Computes historical H2H statistics between…, Compute head-to-head features between two teams. Looks at the last…, Return H2H features with all null values (no historical meetings)., Tests for feature engineering. Covers: form features, H2H features, season-… (+4 more)

### Community 1 - "test_api.py"
Cohesion: 0.18
Nodes (9): Set model reference in ModelManager. Used by tests and lifespan., set_model(), client(), client_no_model(), fixture, Tests for the FastAPI endpoints., Test client with a pre-loaded model., Test client with no model loaded. (+1 more)

### Community 2 - "PredictionService"
Cohesion: 0.16
Nodes (11): PredictionService, Any, Resolve fixture prediction from cache if fresh, otherwise recompute dynamically., Service providing match prediction operations., Return sorted list of known teams., Return attack and defense parameters for team., Return combined profile with Poisson strengths and XGBoost/Elo stats., Get the model instance for a specific architecture. (+3 more)

### Community 3 - "parse_season_csv"
Cohesion: 0.06
Nodes (34): FootballDataClient, Football-Data.org API client for upcoming Premier League fixtures., Client for querying Football-Data.org Premier League endpoints., Fetch scheduled fixtures and return normalized fixture dictionaries., compute_implied_probabilities(), download_season_csv(), load_all_seasons(), normalize_football_data_org_name() (+26 more)

### Community 4 - "TestPoissonProperties"
Cohesion: 0.14
Nodes (10): given, settings, Property-based tests for Dixon-Coles model., τ must be positive for typical football scoring rates and empirical ρ., τ must be exactly 1.0 for all scores where both teams score 2+., Score distribution must sum to ~1.0 for any valid matchup., All probabilities must be >= 0., P(H) + P(D) + P(A) must sum to ~1.0 for any matchup. (+2 more)

### Community 5 - "TestDixonColesModel"
Cohesion: 0.05
Nodes (20): Path, Serialize the fitted model to disk. Args: path: File path to save to (typically…, Deserialize a fitted model from disk. Args: path: File path to load from.…, All score probabilities must be >= 0., Most likely score should be reasonable (not negative, not absurd)., Predicting with unknown team should raise ValueError when allow_unknown=False., Predicting with unknown team should succeed when allow_unknown=True., Predicting without fit() should raise RuntimeError. (+12 more)

### Community 6 - "test_pipeline.py"
Cohesion: 0.19
Nodes (12): load_matches_from_db(), DataFrame, Session, Save match records from a DataFrame into the database. Skips matches that…, Load matches from database into a pandas DataFrame. Returns DataFrame…, save_matches_to_db(), fixture, End-to-end integration tests for the MatchSense pipeline. Tests the full… (+4 more)

### Community 7 - "BasePredictor"
Cohesion: 0.17
Nodes (11): ABC, get_model(), Dependency injection for FastAPI routes. Provides model references and access…, Get the loaded model instance from ModelManager., Prediction service encapsulating prediction domain logic., BasePredictor, Abstract base class for prediction models. All models (Dixon-Coles, XGBoost in…, Interface that every prediction model must implement. (+3 more)

### Community 8 - "ndarray"
Cohesion: 0.16
Nodes (10): DataFrame, ndarray, Pack model parameters into a flat vector for the optimizer. Layout: [alpha_2,…, Unpack a flat parameter vector into named parameters. Returns: Tuple of…, Vectorized negative log-likelihood (to minimize). L = -Σ w(t) * [log(τ) +…, Return the current parameter vector for warm-starting a subsequent fit.…, Fit the Dixon-Coles model on historical match data. Args: matches: DataFrame…, Compute exponential time-decay weights for each match. More recent matches… (+2 more)

### Community 9 - "Database Schema & Migrations"
Cohesion: 0.29
Nodes (9): fitted_model(), multi_season_matches(), DataFrame, fixture, Shared test fixtures for MatchSense. Provides sample match data, a fitted…, Small realistic dataset for unit tests. 20 matches across 5 teams in 1 season,…, Two-season dataset for testing season-boundary behavior., A pre-fitted Dixon-Coles model on sample data. (+1 more)

### Community 10 - "Phase 2B Design Specification: Advanced Features & XGBoost Classifier"
Cohesion: 0.09
Nodes (22): 1. Executive Summary & Architecture, 2.1 Universal Window-Anchored Elo Rating System (`ml/features/elo.py`), 2.2 Rolling Match Activity & Shot Quality (`ml/features/match_stats.py`), 2.3 Understat xG Schema & Separation (`ml/features/xg.py`), 2.4 Feature Pipeline Orchestration (`ml/features/pipeline.py`), 2. Feature Engineering & Data Architecture, 3.1 XGBoost Classifier (`ml/models/xgboost_model.py`), 3.2 Cold-Start & Zero-Window History Handling (+14 more)

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
Cohesion: 0.15
Nodes (11): Dixon-Coles correction factor for low-scoring matches. Adjusts the joint…, _tau(), Tests for the Dixon-Coles model. Covers: tau correction, parameter packing,…, Test the Dixon-Coles low-score correction function., 0-0: correction depends on lambda, mu, rho., 0-1: correction depends on lambda and rho., 1-0: correction depends on mu and rho., 1-1: correction is 1 - rho. (+3 more)

### Community 32 - "What Was Completed"
Cohesion: 0.15
Nodes (12): 1. Project Scaffolding & Configuration, 2. Data Ingestion & Validation, 3. Database & Migrations, 4. Feature Engineering Pipeline, 5. Dixon-Coles Model Implementation, 6. FastAPI Service Layer, 7. Documentation, Automated Test Suite: 57 / 57 Passed (+4 more)

### Community 33 - "simulate_betting"
Cohesion: 0.15
Nodes (15): BacktestResult, DataFrame, Financial backtesting engine with pre-gameweek batch staking., Run financial backtest with gameweek batch sizing and conflict guards. Args:…, simulate_betting(), fixture, Unit tests for financial backtesting and staking simulator., Create deterministic fixture dataset across 2 gameweeks. (+7 more)

### Community 34 - "DixonColesModel"
Cohesion: 0.10
Nodes (16): DixonColesModel, Dixon-Coles model for football match prediction. Implements the Dixon & Coles…, Predict outcome probabilities for a match., Predict the joint score probability distribution., Return attack/defense strengths for all teams., Return metadata about the fitted model., Raise if model has not been fitted., Raise if either team is unknown. (+8 more)

### Community 35 - "MatchSense — Evaluation Suite Design Spec (Phase 2A)"
Cohesion: 0.07
Nodes (28): 1. Executive Summary, 2. Architecture & Module Structure, 3.1 Ranked Probability Score (RPS), 3.2 Multi-Category Brier Score, 3.3 Multi-Class Log-Loss (Cross-Entropy), 3.4 Categorical Accuracy, 3. Mathematical Foundations & Metrics (`ml/evaluation/metrics.py`), 4.1 Wilcoxon Signed-Rank Test on Paired $\Delta \text{RPS}$ (+20 more)

### Community 36 - "wilcoxon_rps_test"
Cohesion: 0.12
Nodes (23): evaluate_significance_suite(), mcnemar_accuracy_test(), McNemarResult, Any, DataFrame, ndarray, Hypothesis testing for comparative model evaluation., Paired Wilcoxon signed-rank test on match-by-match RPS differences. Uses Pratt… (+15 more)

### Community 37 - "predictions.py"
Cohesion: 0.11
Nodes (29): compare_predictions(), ComparePredictionResponse, FixtureCard, get_team_profile(), get_team_strength(), HeadToHeadRequest, list_teams(), list_upcoming_fixtures() (+21 more)

### Community 38 - "Evaluation Core (`ml/evaluation/`)"
Cohesion: 0.12
Nodes (16): Automated Tests, Evaluation Core (`ml/evaluation/`), Manual Verification & Benchmark Execution, MatchSense — Phase 2A Evaluation Suite Implementation Plan, [NEW] [`ml/evaluation/backtest.py`](file:///d:/Yash%20Kokane/Projects/MatchSense/ml/evaluation/backtest.py), [NEW] [`ml/evaluation/calibration.py`](file:///d:/Yash%20Kokane/Projects/MatchSense/ml/evaluation/calibration.py), [NEW] [`ml/evaluation/metrics.py`](file:///d:/Yash%20Kokane/Projects/MatchSense/ml/evaluation/metrics.py), [NEW] [`ml/evaluation/report.py`](file:///d:/Yash%20Kokane/Projects/MatchSense/ml/evaluation/report.py) (+8 more)

### Community 39 - "compute_calibration"
Cohesion: 0.19
Nodes (14): BinSummary, CalibrationResult, compute_calibration(), _compute_class_calibration(), ndarray, Reliability diagrams and calibration metrics., Compute Expected Calibration Error and reliability tables across H/D/A outcomes., Unit tests for calibration and expected calibration error (ECE). (+6 more)

### Community 40 - "mini_league_dataset"
Cohesion: 0.67
Nodes (3): mini_league_dataset(), fixture, Small realistic 6-team dataset across 2 seasons with match stats.

### Community 41 - "MatchSense — Phase 2B Implementation and Evaluation Walkthrough"
Cohesion: 0.17
Nodes (11): 1. Architecture Overview & Components Delivered, 2. Key Architectural Decisions, 3.1 Aggregate Performance Across 3 Test Seasons, 3.2 Direct Head-to-Head Comparison (XGBoost vs. Dixon-Coles), 3.3 Probability Calibration & Reliability Summary, 3. Out-of-Sample Benchmark Evaluation (1,140 Matches), 4. Automated Sanity Verification Gates, 5. Verification & Code Quality (+3 more)

### Community 42 - "MatchSense — Phase 1 Implementation & Training Walkthrough"
Cohesion: 0.18
Nodes (10): 1. Resolution of Data Churn & Season Scope, 2. Model Training & Optimization Performance, 3. Team Strength Sanity Check, 4. Real Matchup Smoke Tests, 5. Verification & Code Quality Status, Bottom 5 Defenses (Highest Conceded Expected Goals $\beta$), Fitted Global Parameters, MatchSense — Phase 1 Implementation & Training Walkthrough (+2 more)

### Community 43 - "EloEngine"
Cohesion: 0.13
Nodes (15): compute_window_elo(), EloEngine, DataFrame, Timestamp, Window-anchored Elo rating engine with dynamic margin-of-victory and empirical…, Compute expected outcome score probabilities for home and away teams. Args:…, Dynamic multiplier based on margin of victory following World Football Elo…, Apply inter-season mean-reversion and empirical Q0.25 promoted entry. Surviving… (+7 more)

### Community 44 - "Global Constraints"
Cohesion: 0.20
Nodes (9): Evaluation Suite (Phase 2A) Implementation Plan, Global Constraints, Task 1: Probabilistic & Categorical Metrics, Task 2: Hypothesis Testing Engine, Task 3: Calibration & Expected Calibration Error (ECE), Task 4: Financial Backtesting & Betting Simulator, Task 5: Walk-Forward CV Orchestrator & Baselines, Task 6: Structured Report Container & Formatters (+1 more)

### Community 45 - "2. Statistical Significance vs Baselines (Primary: Per-Fold Independent)"
Cohesion: 0.18
Nodes (10): 1. Out-of-Sample Performance by Season (Rolling 4-Season Window), 2. Statistical Significance vs Baselines (Primary: Per-Fold Independent), 3. Financial Simulation & ROI (Edge >= 5%), 4. Calibration & Reliability Summary, Away Outcome Reliability Bins (1,140 Matches), Fold Season: `2023-24`, Fold Season: `2024-25`, Fold Season: `2025-26` (+2 more)

### Community 46 - ".predict_score_distribution"
Cohesion: 0.40
Nodes (3): ndarray, Predict the joint score probability distribution. Optional. Returns None for…, Predict the single most likely scoreline. Optional. Returns None if score…

### Community 47 - "ModelManager"
Cohesion: 0.11
Nodes (16): ModelManager, ModelMetadata, Any, ModelManager for zero-downtime hot-reloading of ML models from PostgreSQL., Startup hook: attempt DB reload, falling back to local files., Metadata tracking loaded model version, active timestamps, and manifests., Manages hot-reloading in-memory models backed by PostgreSQL artifacts., Register or atomically swap an in-memory model reference. (+8 more)

### Community 48 - "run_walk_forward_cv"
Cohesion: 0.08
Nodes (38): compute_accuracy(), compute_brier_score(), compute_log_loss(), compute_rps(), ndarray, Mathematical evaluation metrics for football match prediction., Compute multi-category Brier score. Args: probs: Array of shape (N, 3).…, Compute multi-class cross-entropy log-loss. Args: probs: Array of shape (N, 3).… (+30 more)

### Community 49 - "pipeline.py"
Cohesion: 0.29
Nodes (6): Feature pipeline orchestrator. Combines form, H2H, temporal, match statistics,…, compute_rolling_xg(), DataFrame, Timestamp, Understat xG feature extractor with strict schema separation., Compute rolling xG metrics strictly prior to match_date. Produces separate,…

### Community 50 - "MatchSense — Phase 2B Implementation and Evaluation Walkthrough"
Cohesion: 0.17
Nodes (11): 1. Architecture Overview & Components Delivered, 2. Key Architectural Decisions, 3.1 Aggregate Performance Across 3 Test Seasons, 3.2 Direct Head-to-Head Comparison (XGBoost vs. Dixon-Coles), 3.3 Probability Calibration & Reliability Summary, 3. Out-of-Sample Benchmark Evaluation (1,140 Matches), 4. Automated Sanity Verification Gates, 5. Verification & Code Quality (+3 more)

### Community 51 - "Dixon-Coles Convergence Audit: Walk-Forward CV (114 Gameweek Refits)"
Cohesion: 0.20
Nodes (9): Audit Summary, Code Bug, Correlation with Fold-Level Performance Degradation, Detailed Failure Map, Dixon-Coles Convergence Audit: Walk-Forward CV (114 Gameweek Refits), Fold 2 (2024-25): 9 failures, Fold 3 (2025-26): 13 failures, Per-Fold Breakdown (+1 more)

### Community 52 - "Proposed Changes"
Cohesion: 0.17
Nodes (11): API & Serving, Automated Tests, Dependencies & Setup, Feature Engineering, Implementation Plan: Phase 2B — Advanced Features & XGBoost Classifier, Modeling & Interface Decoupling, Open Questions, Proposed Changes (+3 more)

### Community 53 - "MatchSense — Phase 3: Live Serving & Automation Pipeline Specification"
Cohesion: 0.07
Nodes (28): 1. Executive Summary & Goals, 1. Single-Model Head-to-Head (Backward-Compatible), 2.1 Model Artifact Store (`models` Table), 2.2 Upcoming Fixtures Store (`fixtures` Table), 2. Database Architecture & Schema Layer, 2. Multi-Model Comparison, 3.1 Ingestion-Time Canonical Name Resolution, 3. Ingestion & Team Name Normalization (+20 more)

### Community 54 - "compute_form_features"
Cohesion: 0.21
Nodes (8): compute_form_features(), Compute recent form features for a team. Uses ONLY matches from the same…, Test recent form feature computation., Form features should be computed correctly after 5+ matches., First match of season should return null/empty form., Early in season, form uses however many matches are available., Features must NOT use data from after the match date., TestFormFeatures

### Community 55 - "compute_temporal_features"
Cohesion: 0.18
Nodes (8): compute_temporal_features(), Compute temporal features: fatigue, league position, promotion status. Args:…, Test that form features reset at season boundaries., Form features should NOT carry over from previous season., Newly promoted team should have null form features., is_newly_promoted should be True for teams not in previous season., Teams present in previous season should NOT be flagged as promoted., TestSeasonBoundary

### Community 56 - "compute_match_stats_features"
Cohesion: 0.21
Nodes (10): compute_match_stats_features(), DataFrame, Timestamp, Rolling match statistics and shot quality feature extractor., Compute rolling shot and corner metrics strictly prior to match_date. Resets at…, fixture, Unit tests for rolling match statistics and shot quality feature extractor., sample_match_data() (+2 more)

### Community 57 - "Tasks"
Cohesion: 0.18
Nodes (10): Global Constraints, Phase 2B Implementation Plan: Advanced Features & XGBoost Classifier, Task 1: Environment & Dependency Setup, Task 2: Window-Anchored Elo Rating System (`ml/features/elo.py`), Task 3: Rolling Match Activity & Shot Quality (`ml/features/match_stats.py`), Task 4: Separated Understat xG Schema & Feature Pipeline Integration (`ml/features/xg.py`, `ml/features/pipeline.py`), Task 5: `BasePredictor` Decoupling & XGBoost Classifier (`ml/models/base.py`, `ml/models/xgboost_model.py`), Task 6: API Layer & Route Updates (`backend/models/schemas.py`, `backend/services/prediction.py`, `tests/unit/test_api.py`) (+2 more)

### Community 58 - "2. Statistical Significance vs Baselines (Primary: Per-Fold Independent)"
Cohesion: 0.18
Nodes (10): 1. Out-of-Sample Performance by Season (Rolling 4-Season Window), 2. Statistical Significance vs Baselines (Primary: Per-Fold Independent), 3. Financial Simulation & ROI (Edge >= 5%), 4. Calibration & Reliability Summary, Away Outcome Reliability Bins (1,140 Matches), Fold Season: `2023-24`, Fold Season: `2024-25`, Fold Season: `2025-26` (+2 more)

### Community 59 - "2. Benchmark Evaluation Results (Dixon-Coles vs Baselines)"
Cohesion: 0.20
Nodes (9): 1. Phase 2A Architecture Overview, 2. Benchmark Evaluation Results (Dixon-Coles vs Baselines), 3. Go / No-Go Sanity Gates Verification, 4. Code Quality & Test Suite Status, Calibration, Financial Backtest & Betting Simulation ($\text{EV} \ge 0.05$), MatchSense — Phase 1 & Phase 2A Implementation and Evaluation Walkthrough, Out-of-Sample Performance by Season (Rolling 4-Season Window) (+1 more)

### Community 60 - "form.py"
Cohesion: 0.24
Nodes (9): compute_home_away_splits(), compute_season_features(), _empty_form_features(), DataFrame, Timestamp, Recent form and temporal feature engineering. Computes per-team rolling…, Compute home vs away performance splits. Args: matches: Full matches DataFrame.…, Return form features with all null values (no data available). (+1 more)

### Community 61 - "MatchSense — Multi-Model Comparative Evaluation: XGBoost vs. Dixon-Coles"
Cohesion: 0.20
Nodes (9): 1. Executive Summary & Out-of-Sample Performance, 2. Direct Head-to-Head Comparison: XGBoost vs. Dixon-Coles, 3. Performance vs. Market Consensus Lines (1,140 Matches), 4. Probability Calibration & Reliability Summary, 5. Financial Simulation & ROI (Edge >= 5%), 6. Automated Sanity Verification Gates, Away Outcome Reliability Bins Breakdown (1,140 Matches), MatchSense — Multi-Model Comparative Evaluation: XGBoost vs. Dixon-Coles (+1 more)

### Community 62 - "sync_pipeline.py"
Cohesion: 0.18
Nodes (19): Fixture, Upcoming scheduled Premier League fixture with cached predictions., check_gate_2a_dixon_coles(), check_gate_2a_xgboost(), main(), DataFrame, Session, Weekly synchronization pipeline engine for MatchSense. Orchestrates decoupled… (+11 more)

### Community 63 - "build_match_features"
Cohesion: 0.16
Nodes (12): build_feature_matrix(), build_match_features(), DataFrame, Timestamp, Build feature vectors for ALL matches in the dataset. Processes matches in…, Build the complete feature vector for a single match. All features use ONLY…, Predict outcome probabilities for a match., Test the full feature pipeline orchestrator. (+4 more)

### Community 64 - "XGBoostPredictor"
Cohesion: 0.13
Nodes (14): Any, DataFrame, Discriminative match outcome predictor using regularized gradient-boosted trees., Index precomputed bounded features for fast lookup during CV., Return model metadata for health endpoint and status reporting., Fit XGBoost classifier on historical match window., XGBoostPredictor, mock_training_data() (+6 more)

### Community 65 - "MockXGBModel"
Cohesion: 0.13
Nodes (4): MockDCModel, MockXGBModel, fixture, setup_models()

### Community 66 - "test_api_phase3.py"
Cohesion: 0.15
Nodes (7): create_tables(), get_db(), Session, SQLAlchemy database engine and session management. Uses synchronous SQLAlchemy…, Yield a database session, ensuring it's closed after use., Create all tables defined by ORM models. Used for dev/testing., test_fixtures_upcoming_with_per_model_freshness()

### Community 67 - "EvaluationReport"
Cohesion: 0.19
Nodes (10): EvaluationReport, Any, Comprehensive evaluation scorecard generator., Generate full GitHub-flavored Markdown scorecard., Convert report metrics into a flattened dictionary., Container for model evaluation results, cross-validation, significance, and…, Unit tests for EvaluationReport serialization and markdown rendering., test_report_hierarchical_significance() (+2 more)

### Community 69 - "evaluate.py"
Cohesion: 0.23
Nodes (13): Namespace, _build_model_report(), _compute_head_to_head(), _compute_market_comparison(), main(), parse_args(), Any, DataFrame (+5 more)

### Community 70 - "Base"
Cohesion: 0.22
Nodes (8): Base, Base class for all SQLAlchemy ORM models., Prediction, SQLAlchemy ORM models for MatchSense. Three core tables: - Match: Historical…, A Premier League team with canonical name for normalization., A model prediction for a match, storing full probability distributions., Team, DeclarativeBase

### Community 71 - "config.py"
Cohesion: 0.20
Nodes (8): Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online(), Pydantic settings for MatchSense configuration. Loads from environment…, Application configuration loaded from environment variables., Settings, BaseSettings

### Community 72 - "ModelArtifact"
Cohesion: 0.24
Nodes (8): ModelArtifact, Serialized model binary and walk-forward verification manifest., test_phase_b1_two_tier_recovery(), db_session(), fixture, Session, test_fixture_orm_default_jsonb(), test_model_artifact_orm()

### Community 73 - "main.py"
Cohesion: 0.23
Nodes (10): create_app(), lifespan(), FastAPI application factory for MatchSense. Loads the fitted Dixon-Coles model…, Initialize model manager at startup and log status., Create and configure the FastAPI application., health_check(), get, Health check endpoint. Returns model metadata, database connectivity, and… (+2 more)

### Community 74 - "Global Constraints"
Cohesion: 0.22
Nodes (8): Global Constraints, Phase 3: Live Serving & Automation Pipeline Implementation Plan, Task 1: Database Schema & Migration Layer (`models` and `fixtures`), Task 2: External API Client & Canonical Team Name Ingestion, Task 3: In-Memory Model Manager with Polling & Hot-Reloading, Task 4: Phase 3 API Layer & Backward Compatibility, Task 5: Weekly Synchronization Pipeline Engine (`scripts/sync_pipeline.py`), Task 6: GitHub Actions Cron Workflow & Full Regression Run

### Community 75 - "ComparisonReport"
Cohesion: 0.29
Nodes (5): ComparisonReport, Print markdown report to stdout., Multi-model comparative evaluation report for XGBoost vs Dixon-Coles., Generate comprehensive GitHub-flavored Markdown comparative scorecard., Print comparative markdown report to stdout.

### Community 76 - "test_sync_pipeline.py"
Cohesion: 0.18
Nodes (10): Match, A single Premier League match with result, stats, and bookmaker odds., Database loader utilities for matches. Provides functions to save match…, Score completed matches against pre-match fixture predictions grouped by GW., score_gate_2b_audit(), fixture, Integration tests for the weekly synchronization pipeline engine., test_db() (+2 more)

### Community 79 - "2. Key Architectural Invariants & Verified Solutions"
Cohesion: 0.17
Nodes (11): 1. System Architecture & Components Delivered, 2.1 Decoupled 3-Phase Execution Boundaries, 2.2 Atomic JSONB Partial Merging, 2.3 Per-Model Freshness & Dynamic Dynamic Recomputation, 2.4 In-Memory Zero-Downtime Hot-Reloading (`ModelManager`), 2.5 Strict Refusal of Unvalidated Consensus Blending, 2. Key Architectural Invariants & Verified Solutions, 3.1 Test Suite Breakdown (114 Passed) (+3 more)

### Community 80 - "TestMediumScaleConvergence"
Cohesion: 0.25
Nodes (6): DataFrame, fixture, Test model convergence at realistic scale. This catches optimization bugs that…, Generate a synthetic 25-team, 500-match dataset., Model should converge on 25-team, 500-match dataset., TestMediumScaleConvergence

### Community 84 - "synthetic_seasons_data"
Cohesion: 0.67
Nodes (3): fixture, Create 5 teams across 2 small test seasons (20 matches per season)., synthetic_seasons_data()

## Knowledge Gaps
- **229 isolated node(s):** `matchsense`, `Per-Fold Breakdown`, `Fold 2 (2024-25): 9 failures`, `Fold 3 (2025-26): 13 failures`, `Root Cause Analysis` (+224 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 618 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DixonColesModel` connect `DixonColesModel` to `TestPoissonProperties`, `evaluate.py`, `TestDixonColesModel`, `BasePredictor`, `ndarray`, `main.py`, `Database Schema & Migrations`, `test_pipeline.py`, `run_walk_forward_cv`, `TestMediumScaleConvergence`, `sync_pipeline.py`, `_tau`?**
  _High betweenness centrality (0.152) - this node is a cross-community bridge._
- **Why does `BasePredictor` connect `BasePredictor` to `XGBoostPredictor`, `test_api.py`, `PredictionService`, `DixonColesModel`, `.fit`, `.predict_score_distribution`, `ModelManager`, `run_walk_forward_cv`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `XGBoostPredictor` connect `XGBoostPredictor` to `test_api.py`, `PredictionService`, `evaluate.py`, `BasePredictor`, `run_walk_forward_cv`, `sync_pipeline.py`, `build_match_features`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `DixonColesModel` (e.g. with `main()` and `check_gate_2a_dixon_coles()`) actually correct?**
  _`DixonColesModel` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `BasePredictor` (e.g. with `get_model()` and `set_model()`) actually correct?**
  _`BasePredictor` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `Fixture` (e.g. with `list_upcoming_fixtures()` and `PredictionService`) actually correct?**
  _`Fixture` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `matchsense`, `Per-Fold Breakdown`, `Fold 2 (2024-25): 9 failures` to the rest of the system?**
  _229 weakly-connected nodes found - possible documentation gaps or missing edges._