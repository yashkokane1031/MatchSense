# Graph Report - MatchSense  (2026-09-13)

## Corpus Check
- 150 files · ~96,685 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1440 nodes · 2084 edges · 110 communities (82 shown, 12 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 52 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1a4f6501`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_features.py
- test_api.py
- PredictionService
- sync_pipeline.py
- MatchSense — Modern Frontend Dashboard Design Specification
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
- MatchSense — Season Derivation Root-Cause Fix Walkthrough
- MatchSense — Phase 2B Implementation and Evaluation Walkthrough
- MatchSense — Phase 1 Implementation & Training Walkthrough
- EloEngine
- Global Constraints
- 2. Statistical Significance vs Baselines (Primary: Per-Fold Independent)
- .predict_score_distribution
- datetime
- run_walk_forward_cv
- compute_rolling_xg
- MatchSense — Phase 2B Implementation and Evaluation Walkthrough
- Dixon-Coles Convergence Audit: Walk-Forward CV (114 Gameweek Refits)
- Proposed Changes
- MatchSense — Phase 3: Live Serving & Automation Pipeline Specification
- compute_form_features
- TestSeasonBoundary
- compute_match_stats_features
- Tasks
- 2. Statistical Significance vs Baselines (Primary: Per-Fold Independent)
- 2. Benchmark Evaluation Results (Dixon-Coles vs Baselines)
- pipeline.py
- MatchSense — Multi-Model Comparative Evaluation: XGBoost vs. Dixon-Coles
- test_sync_pipeline.py
- build_match_features
- prediction.py
- package.json
- test_api_phase3.py
- EvaluationReport
- compilerOptions
- evaluate.py
- models/schemas.py
- simulator/page.tsx
- api.ts
- devDependencies
- Global Constraints
- ComparisonReport
- index.ts
- seed_data.py
- 2. Key Architectural Invariants & Verified Solutions
- TestMediumScaleConvergence
- constants.ts
- derive_current_season
- Global Constraints
- derive_season_from_date
- dependencies
- Proposed Changes
- api.generated.ts
- MatchSense — Phase 4 Modern Frontend Dashboard Walkthrough
- ingestion.py
- scripts
- teams/page.tsx
- parse_season_csv
- layout.tsx
- MockResizeObserver
- ModelProbabilityBar.tsx
- utils.ts
- MatchSense — Vercel v0 Prototype Brief
- next.config.mjs
- next-env.d.ts
- @vitejs/plugin-react
- main.py
- MockRecoveryModel
- MockXGBModel
- TestPredictionEndpoints
- config.py
- .is_healthy
- test_fixture_orm_default_jsonb
- test_walk_forward.py

## God Nodes (most connected - your core abstractions)
1. `DixonColesModel` - 53 edges
2. `BasePredictor` - 29 edges
3. `XGBoostPredictor` - 27 edges
4. `Fixture` - 22 edges
5. `build_match_features()` - 20 edges
6. `TestDixonColesModel` - 18 edges
7. `Base` - 17 edges
8. `parse_season_csv()` - 17 edges
9. `derive_current_season()` - 17 edges
10. `PredictionService` - 16 edges

## Surprising Connections (you probably didn't know these)
- `get_model()` --uses--> `BasePredictor`  [INFERRED]
  backend/api/dependencies.py → ml/models/base.py
- `set_model()` --uses--> `BasePredictor`  [INFERRED]
  backend/api/dependencies.py → ml/models/base.py
- `test_db()` --uses--> `Base`  [INFERRED]
  tests/integration/test_pipeline.py → backend/core/database.py
- `test_db()` --uses--> `Base`  [INFERRED]
  tests/integration/test_sync_pipeline.py → backend/core/database.py
- `load_matches_from_db()` --uses--> `Match`  [INFERRED]
  ml/data/loader.py → backend/models/schemas.py

## Import Cycles
- None detected.

## Communities (110 total, 12 thin omitted)

### Community 0 - "test_features.py"
Cohesion: 0.16
Nodes (12): compute_h2h_features(), _empty_h2h_features(), DataFrame, Timestamp, Head-to-head feature engineering. Computes historical H2H statistics between…, Compute head-to-head features between two teams. Looks at the last…, Return H2H features with all null values (no historical meetings)., Tests for feature engineering. Covers: form features, H2H features, season-… (+4 more)

### Community 1 - "test_api.py"
Cohesion: 0.10
Nodes (13): Set model reference in ModelManager. Used by tests and lifespan., set_model(), client(), client_no_model(), fixture, Tests for the FastAPI endpoints., Test client with a pre-loaded model., Verify health endpoint returns strictly typed HealthResponse model. (+5 more)

### Community 2 - "PredictionService"
Cohesion: 0.16
Nodes (11): PredictionService, Any, Resolve fixture prediction from cache if fresh, otherwise recompute dynamically., Return sorted list of known teams., Return attack and defense parameters for team., Service providing match prediction operations., Return combined profile with Poisson strengths and XGBoost/Elo stats., Get the model instance for a specific architecture. (+3 more)

### Community 3 - "sync_pipeline.py"
Cohesion: 0.14
Nodes (23): ModelArtifact, Serialized model binary and walk-forward verification manifest., download_season_csv(), load_all_seasons(), Path, Download, parse, and combine all configured seasons. Args: seasons: List of…, Download a season CSV from football-data.co.uk. Args: season_code: Two-digit…, check_gate_2a_dixon_coles() (+15 more)

### Community 4 - "MatchSense — Modern Frontend Dashboard Design Specification"
Cohesion: 0.07
Nodes (28): 1. Executive Summary & Design Principles, 2.1 Technology Stack, 2.2 Directory Structure, 2. Technology Stack & Repository Structure, 3.1 Backend Health Response Schema Hardening, 3.2 Offline Introspection Script (`scripts/export_openapi.py`), 3.3 Typegen Pipeline & CI Verification, 3. Backend Contract Synchronization & OpenAPI Typegen (+20 more)

### Community 5 - "TestDixonColesModel"
Cohesion: 0.06
Nodes (17): All score probabilities must be >= 0., Most likely score should be reasonable (not negative, not absurd)., Predicting with unknown team should raise ValueError when allow_unknown=False., Predicting with unknown team should succeed when allow_unknown=True., Predicting without fit() should raise RuntimeError., Save and load should produce identical predictions., get_team_strengths() should return dict for all teams., get_model_info() should return expected metadata. (+9 more)

### Community 6 - "test_pipeline.py"
Cohesion: 0.17
Nodes (13): load_matches_from_db(), DataFrame, Session, Database loader utilities for matches. Provides functions to save match…, Save match records from a DataFrame into the database. Skips matches that…, Load matches from database into a pandas DataFrame. Returns DataFrame…, save_matches_to_db(), fixture (+5 more)

### Community 7 - "BasePredictor"
Cohesion: 0.08
Nodes (26): ABC, BasePredictor, DataFrame, ndarray, Abstract base class for prediction models. All models (Dixon-Coles, XGBoost in…, Interface that every prediction model must implement., Fit the model on historical match data. Args: matches: DataFrame with at…, Predict outcome probabilities for a match. Args: home_team: Canonical name of… (+18 more)

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
Cohesion: 0.11
Nodes (15): given, Dixon-Coles correction factor for low-scoring matches. Adjusts the joint…, _tau(), settings, τ must be positive for typical football scoring rates and empirical ρ., τ must be exactly 1.0 for all scores where both teams score 2+., Tests for the Dixon-Coles model. Covers: tau correction, parameter packing,…, Test the Dixon-Coles low-score correction function. (+7 more)

### Community 32 - "What Was Completed"
Cohesion: 0.15
Nodes (12): 1. Project Scaffolding & Configuration, 2. Data Ingestion & Validation, 3. Database & Migrations, 4. Feature Engineering Pipeline, 5. Dixon-Coles Model Implementation, 6. FastAPI Service Layer, 7. Documentation, Automated Test Suite: 57 / 57 Passed (+4 more)

### Community 33 - "simulate_betting"
Cohesion: 0.15
Nodes (15): BacktestResult, DataFrame, Financial backtesting engine with pre-gameweek batch staking., Run financial backtest with gameweek batch sizing and conflict guards. Args:…, simulate_betting(), fixture, Unit tests for financial backtesting and staking simulator., Create deterministic fixture dataset across 2 gameweeks. (+7 more)

### Community 34 - "DixonColesModel"
Cohesion: 0.09
Nodes (17): DixonColesModel, Path, Dixon-Coles model for football match prediction. Implements the Dixon & Coles…, Return metadata about the fitted model., Serialize the fitted model to disk. Args: path: File path to save to (typically…, Deserialize a fitted model from disk. Args: path: File path to load from.…, Dixon-Coles model with time-decay weighting. Parameters are estimated via…, Initialize the model. Args: xi: Time-decay rate per day. Higher = more… (+9 more)

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

### Community 40 - "MatchSense — Season Derivation Root-Cause Fix Walkthrough"
Cohesion: 0.12
Nodes (15): Architecture, Commit History, Dry-Run Verification, Fix: API-First Dynamic Season Derivation, Frontend (18/18), Full Backend (130/130), Key Files, MatchSense — Season Derivation Root-Cause Fix Walkthrough (+7 more)

### Community 41 - "MatchSense — Phase 2B Implementation and Evaluation Walkthrough"
Cohesion: 0.17
Nodes (11): 1. Architecture Overview & Components Delivered, 2. Key Architectural Decisions, 3.1 Aggregate Performance Across 3 Test Seasons, 3.2 Direct Head-to-Head Comparison (XGBoost vs. Dixon-Coles), 3.3 Probability Calibration & Reliability Summary, 3. Out-of-Sample Benchmark Evaluation (1,140 Matches), 4. Automated Sanity Verification Gates, 5. Verification & Code Quality (+3 more)

### Community 42 - "MatchSense — Phase 1 Implementation & Training Walkthrough"
Cohesion: 0.18
Nodes (10): 1. Resolution of Data Churn & Season Scope, 2. Model Training & Optimization Performance, 3. Team Strength Sanity Check, 4. Real Matchup Smoke Tests, 5. Verification & Code Quality Status, Bottom 5 Defenses (Highest Conceded Expected Goals $\beta$), Fitted Global Parameters, MatchSense — Phase 1 Implementation & Training Walkthrough (+2 more)

### Community 43 - "EloEngine"
Cohesion: 0.09
Nodes (20): compute_window_elo(), EloEngine, DataFrame, Timestamp, Window-anchored Elo rating engine with dynamic margin-of-victory and empirical…, Compute expected outcome score probabilities for home and away teams. Args:…, Dynamic multiplier based on margin of victory following World Football Elo…, Apply inter-season mean-reversion and empirical Q0.25 promoted entry. Surviving… (+12 more)

### Community 44 - "Global Constraints"
Cohesion: 0.20
Nodes (9): Evaluation Suite (Phase 2A) Implementation Plan, Global Constraints, Task 1: Probabilistic & Categorical Metrics, Task 2: Hypothesis Testing Engine, Task 3: Calibration & Expected Calibration Error (ECE), Task 4: Financial Backtesting & Betting Simulator, Task 5: Walk-Forward CV Orchestrator & Baselines, Task 6: Structured Report Container & Formatters (+1 more)

### Community 45 - "2. Statistical Significance vs Baselines (Primary: Per-Fold Independent)"
Cohesion: 0.18
Nodes (10): 1. Out-of-Sample Performance by Season (Rolling 4-Season Window), 2. Statistical Significance vs Baselines (Primary: Per-Fold Independent), 3. Financial Simulation & ROI (Edge >= 5%), 4. Calibration & Reliability Summary, Away Outcome Reliability Bins (1,140 Matches), Fold Season: `2023-24`, Fold Season: `2024-25`, Fold Season: `2025-26` (+2 more)

### Community 46 - ".predict_score_distribution"
Cohesion: 0.24
Nodes (5): Predict outcome probabilities for a match., Predict the joint score probability distribution., Return attack/defense strengths for all teams., Raise if model has not been fitted., Raise if either team is unknown.

### Community 47 - "datetime"
Cohesion: 0.13
Nodes (16): ModelManager, ModelMetadata, ModelManager for zero-downtime hot-reloading of ML models from PostgreSQL., Startup hook: attempt DB reload, falling back to local files., Metadata tracking loaded model version, active timestamps, and manifests., Manages hot-reloading in-memory models backed by PostgreSQL artifacts., Register or atomically swap an in-memory model reference., Retrieve active in-memory model, checking polling TTL first. (+8 more)

### Community 48 - "run_walk_forward_cv"
Cohesion: 0.10
Nodes (31): compute_accuracy(), compute_brier_score(), compute_log_loss(), compute_rps(), ndarray, Mathematical evaluation metrics for football match prediction., Compute multi-category Brier score. Args: probs: Array of shape (N, 3).…, Compute multi-class cross-entropy log-loss. Args: probs: Array of shape (N, 3).… (+23 more)

### Community 49 - "compute_rolling_xg"
Cohesion: 0.33
Nodes (5): compute_rolling_xg(), DataFrame, Timestamp, Understat xG feature extractor with strict schema separation., Compute rolling xG metrics strictly prior to match_date. Produces separate,…

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
Cohesion: 0.18
Nodes (10): compute_form_features(), _empty_form_features(), Compute recent form features for a team. Uses ONLY matches from the same…, Return form features with all null values (no data available)., Test recent form feature computation., Form features should be computed correctly after 5+ matches., First match of season should return null/empty form., Early in season, form uses however many matches are available. (+2 more)

### Community 55 - "TestSeasonBoundary"
Cohesion: 0.20
Nodes (6): Test that form features reset at season boundaries., Form features should NOT carry over from previous season., Newly promoted team should have null form features., is_newly_promoted should be True for teams not in previous season., Teams present in previous season should NOT be flagged as promoted., TestSeasonBoundary

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

### Community 60 - "pipeline.py"
Cohesion: 0.27
Nodes (10): compute_home_away_splits(), compute_season_features(), compute_temporal_features(), DataFrame, Timestamp, Recent form and temporal feature engineering. Computes per-team rolling…, Compute home vs away performance splits. Args: matches: Full matches DataFrame.…, Compute temporal features: fatigue, league position, promotion status. Args:… (+2 more)

### Community 61 - "MatchSense — Multi-Model Comparative Evaluation: XGBoost vs. Dixon-Coles"
Cohesion: 0.20
Nodes (9): 1. Executive Summary & Out-of-Sample Performance, 2. Direct Head-to-Head Comparison: XGBoost vs. Dixon-Coles, 3. Performance vs. Market Consensus Lines (1,140 Matches), 4. Probability Calibration & Reliability Summary, 5. Financial Simulation & ROI (Edge >= 5%), 6. Automated Sanity Verification Gates, Away Outcome Reliability Bins Breakdown (1,140 Matches), MatchSense — Multi-Model Comparative Evaluation: XGBoost vs. Dixon-Coles (+1 more)

### Community 62 - "test_sync_pipeline.py"
Cohesion: 0.14
Nodes (18): Fixture, Match, Upcoming scheduled Premier League fixture with cached predictions., A single Premier League match with result, stats, and bookmaker odds., Score completed matches against pre-match fixture predictions grouped by GW., Ingest latest completed matches and upcoming fixtures into DB. Returns new…, run_phase_a_ingestion(), score_gate_2b_audit() (+10 more)

### Community 63 - "build_match_features"
Cohesion: 0.16
Nodes (12): build_feature_matrix(), build_match_features(), DataFrame, Timestamp, Build feature vectors for ALL matches in the dataset. Processes matches in…, Build the complete feature vector for a single match. All features use ONLY…, Predict outcome probabilities for a match., Test the full feature pipeline orchestrator. (+4 more)

### Community 64 - "prediction.py"
Cohesion: 0.21
Nodes (11): get_model(), Dependency injection for FastAPI routes. Provides model references and access…, Get the loaded model instance from ModelManager., health_check(), HealthResponse, ModelStatus, BaseModel, get (+3 more)

### Community 65 - "package.json"
Cohesion: 0.11
Nodes (18): name, private, version, class-variance-authority, cmdk, jsdom, lucide-react, openapi-typescript (+10 more)

### Community 66 - "test_api_phase3.py"
Cohesion: 0.13
Nodes (4): get_db(), Session, Yield a database session, ensuring it's closed after use., MockDCModel

### Community 67 - "EvaluationReport"
Cohesion: 0.19
Nodes (10): EvaluationReport, Any, Comprehensive evaluation scorecard generator., Generate full GitHub-flavored Markdown scorecard., Convert report metrics into a flattened dictionary., Container for model evaluation results, cross-validation, significance, and…, Unit tests for EvaluationReport serialization and markdown rendering., test_report_hierarchical_significance() (+2 more)

### Community 68 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 69 - "evaluate.py"
Cohesion: 0.23
Nodes (13): Namespace, _build_model_report(), _compute_head_to_head(), _compute_market_comparison(), main(), parse_args(), Any, DataFrame (+5 more)

### Community 70 - "models/schemas.py"
Cohesion: 0.12
Nodes (17): Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online(), Base, create_tables(), SQLAlchemy database engine and session management. Uses synchronous SQLAlchemy…, Base class for all SQLAlchemy ORM models. (+9 more)

### Community 71 - "simulator/page.tsx"
Cohesion: 0.17
Nodes (12): SimulatorPage(), FeatureDiffTable(), ModelComparisonBlock(), ModelComparisonBlockProps, computeCellAlpha(), ScoreHeatmap(), ScoreHeatmapProps, TeamSelector() (+4 more)

### Community 72 - "api.ts"
Cohesion: 0.22
Nodes (11): HealthBadge(), useHealthStatus(), api, ApiError, ClientHealthStatus, HealthResponse, HealthStatusType, server (+3 more)

### Community 73 - "devDependencies"
Cohesion: 0.14
Nodes (14): devDependencies, jsdom, msw, openapi-typescript, postcss, tailwindcss, @tailwindcss/postcss, @testing-library/react (+6 more)

### Community 74 - "Global Constraints"
Cohesion: 0.22
Nodes (8): Global Constraints, Phase 3: Live Serving & Automation Pipeline Implementation Plan, Task 1: Database Schema & Migration Layer (`models` and `fixtures`), Task 2: External API Client & Canonical Team Name Ingestion, Task 3: In-Memory Model Manager with Polling & Hot-Reloading, Task 4: Phase 3 API Layer & Backward Compatibility, Task 5: Weekly Synchronization Pipeline Engine (`scripts/sync_pipeline.py`), Task 6: GitHub Actions Cron Workflow & Full Regression Run

### Community 75 - "ComparisonReport"
Cohesion: 0.29
Nodes (5): ComparisonReport, Print markdown report to stdout., Multi-model comparative evaluation report for XGBoost vs Dixon-Coles., Generate comprehensive GitHub-flavored Markdown comparative scorecard., Print comparative markdown report to stdout.

### Community 76 - "index.ts"
Cohesion: 0.19
Nodes (12): dynamic, FixtureCard(), FixtureGrid(), FixtureGridProps, GameweekHero(), GameweekHeroProps, MOCK_FIXTURES_GW28, FixtureCard (+4 more)

### Community 77 - "seed_data.py"
Cohesion: 0.22
Nodes (7): DataFrame, Pandera validation schemas for match data. Validates data integrity at…, Check that FTR is consistent with FTHG/FTAG., _result_matches_goals(), main(), Seed data script: download historical data, validate, fit model. Usage: uv run…, Download data, validate, fit model, and save.

### Community 79 - "2. Key Architectural Invariants & Verified Solutions"
Cohesion: 0.17
Nodes (11): 1. System Architecture & Components Delivered, 2.1 Decoupled 3-Phase Execution Boundaries, 2.2 Atomic JSONB Partial Merging, 2.3 Per-Model Freshness & Dynamic Dynamic Recomputation, 2.4 In-Memory Zero-Downtime Hot-Reloading (`ModelManager`), 2.5 Strict Refusal of Unvalidated Consensus Blending, 2. Key Architectural Invariants & Verified Solutions, 3.1 Test Suite Breakdown (114 Passed) (+3 more)

### Community 80 - "TestMediumScaleConvergence"
Cohesion: 0.25
Nodes (6): DataFrame, fixture, Test model convergence at realistic scale. This catches optimization bugs that…, Generate a synthetic 25-team, 500-match dataset., Model should converge on 25-team, 500-match dataset., TestMediumScaleConvergence

### Community 81 - "constants.ts"
Cohesion: 0.16
Nodes (10): dynamic, TeamProfilePage(), FixtureFilter(), FixtureFilterProps, ALIAS_LOOKUP, BASE_PREMIER_LEAGUE_TEAMS, HISTORICAL_TEAMS, PREMIER_LEAGUE_TEAMS (+2 more)

### Community 82 - "derive_current_season"
Cohesion: 0.13
Nodes (13): default_training_seasons(), Compute the 4-season training window ending at the current season. Derives the…, derive_current_season(), Return (season_code, season_label) for the active PL season. Uses the API-…, When API reports a season, it wins over date-math., When API season is None, date-math fallback activates., Empty API strings are treated as absent., Early Aug: date fallback says 2526, but API reports 2627 → API wins. (+5 more)

### Community 83 - "Global Constraints"
Cohesion: 0.15
Nodes (12): Global Constraints, MatchSense Modern Frontend Dashboard Implementation Plan, Plan Self-Review Checklist, Task 1: Backend HealthResponse Hardening & Offline OpenAPI Exporter, Task 2: Frontend Scaffolding, Tailwind v4 Design Tokens & OpenAPI Typegen, Task 3: Typed API Client, Resilience Handling & Health Status Hook, Task 4: Mathematical Visualizations — Dual-Model Probability Bar & 5x5 Poisson Heatmap, Task 5: Route 1 — Upcoming Gameweek Fixtures Dashboard (`/`) (+4 more)

### Community 84 - "derive_season_from_date"
Cohesion: 0.08
Nodes (23): derive_season_from_date(), derive_training_window(), Dynamic Premier League season identification. Single source of truth for…, Return the N-season sliding window ending at current_code. Args: current_code:…, Convert a season start year to the 4-digit code used by football-data.co.uk.…, Convert a season start year to a human-readable label. Example: 2026 → "2026-27", Convert a 4-digit season code back to a full start year. Example: "2627" → 2026…, Derive the active PL season from the system date. This is the **fallback** path… (+15 more)

### Community 85 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, class-variance-authority, clsx, cmdk, lucide-react, next, @radix-ui/react-popover, @radix-ui/react-tabs (+5 more)

### Community 86 - "Proposed Changes"
Cohesion: 0.11
Nodes (17): Automated Tests, Fix sync_pipeline.py Season Derivation — Root Cause Fix, Git Commit Strategy, Ingestion Module Update, [MODIFY] [`ml/data/ingestion.py`](file:///d:/Yash Kokane/Projects/MatchSense/ml/data/ingestion.py), [MODIFY] [`scripts/sync_pipeline.py`](file:///d:/Yash Kokane/Projects/MatchSense/scripts/sync_pipeline.py), [MODIFY] `tests/integration/test_sync_pipeline.py`, [NEW] [`ml/data/season.py`](file:///d:/Yash Kokane/Projects/MatchSense/ml/data/season.py) (+9 more)

### Community 87 - "api.generated.ts"
Cohesion: 0.33
Nodes (5): components, $defs, operations, paths, webhooks

### Community 88 - "MatchSense — Phase 4 Modern Frontend Dashboard Walkthrough"
Cohesion: 0.12
Nodes (16): 1. System Architecture & Components Delivered, 2.1 Issue Diagnosis, 2.2 Fixes Applied, 2.3 Result, 2.4 Comprehensive Premier League Team Alias Normalization, 2. Live Runtime Integration & Offline Snapshot Resolution, 3.1 Zero-Cost Offline OpenAPI Type Generation, 3.2 Strictly Bounded Mathematical Visualizations (+8 more)

### Community 89 - "ingestion.py"
Cohesion: 0.17
Nodes (12): FootballDataClient, Football-Data.org API client for upcoming Premier League fixtures., Client for querying Football-Data.org Premier League endpoints., Fetch scheduled fixtures and return normalized fixture dictionaries., normalize_football_data_org_name(), Data ingestion pipeline for football-data.co.uk CSVs. Downloads, parses,…, Map Football-Data.org official club names to MatchSense canonical names., normalize_team() (+4 more)

### Community 90 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, start, test, typecheck, typegen, typegen:check

### Community 91 - "teams/page.tsx"
Cohesion: 0.18
Nodes (8): dynamic, ModelsPage(), dynamic, CalibrationBin, CalibrationChart(), LeagueStrengthScatter(), TeamScatterPoint, recharts

### Community 92 - "parse_season_csv"
Cohesion: 0.11
Nodes (16): compute_implied_probabilities(), normalize_team_name(), parse_season_csv(), DataFrame, Parse a football-data.co.uk CSV into a cleaned DataFrame. Handles both dd/mm/yy…, Compute bookmaker implied probabilities from decimal odds. Removes the…, Normalize a team name to its canonical form., Unit tests for data ingestion, normalization, and validation. (+8 more)

### Community 93 - "layout.tsx"
Cohesion: 0.40
Nodes (3): metadata, Navbar(), next

### Community 102 - "main.py"
Cohesion: 0.27
Nodes (9): create_app(), lifespan(), FastAPI application factory for MatchSense. Loads the fitted Dixon-Coles model…, Initialize model manager at startup and log status., Create and configure the FastAPI application., FastAPI, export_openapi(), Export FastAPI OpenAPI schema to frontend/openapi.json offline. (+1 more)

### Community 106 - "config.py"
Cohesion: 0.40
Nodes (4): Pydantic settings for MatchSense configuration. Loads from environment…, Application configuration loaded from environment variables., Settings, BaseSettings

### Community 107 - ".is_healthy"
Cohesion: 0.40
Nodes (3): Any, Return loaded status and versions for health checks., Return human-readable metadata about the model instance. Optional. Subclasses…

### Community 108 - "test_fixture_orm_default_jsonb"
Cohesion: 0.67
Nodes (3): Session, test_fixture_orm_default_jsonb(), test_model_artifact_orm()

### Community 109 - "test_walk_forward.py"
Cohesion: 0.22
Nodes (8): fixture, Unit tests for rolling fixed-window walk-forward cross validation., Create 5 teams across 2 small test seasons (20 matches per season)., Walk forward CV runs on test season using rolling 1-season window., Walk forward CV runs identically with XGBoostPredictor without leakage., synthetic_seasons_data(), test_walk_forward_execution(), test_walk_forward_execution_with_xgboost()

## Knowledge Gaps
- **385 isolated node(s):** `nextConfig`, `name`, `version`, `private`, `dev` (+380 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 828 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DixonColesModel` connect `DixonColesModel` to `sync_pipeline.py`, `evaluate.py`, `main.py`, `BasePredictor`, `ndarray`, `Database Schema & Migrations`, `test_pipeline.py`, `TestDixonColesModel`, `seed_data.py`, `.predict_score_distribution`, `datetime`, `TestMediumScaleConvergence`, `test_walk_forward.py`, `_tau`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Why does `XGBoostPredictor` connect `BasePredictor` to `test_api.py`, `PredictionService`, `sync_pipeline.py`, `evaluate.py`, `EloEngine`, `test_walk_forward.py`, `build_match_features`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `BasePredictor` connect `BasePredictor` to `prediction.py`, `test_api.py`, `PredictionService`, `DixonColesModel`, `.is_healthy`, `datetime`, `run_walk_forward_cv`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `DixonColesModel` (e.g. with `ModelManager` and `main()`) actually correct?**
  _`DixonColesModel` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `datetime` (e.g. with `setup_models()` and `test_model_manager_poll_database_trigger_reload()`) actually correct?**
  _`datetime` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `BasePredictor` (e.g. with `get_model()` and `set_model()`) actually correct?**
  _`BasePredictor` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `Fixture` (e.g. with `list_upcoming_fixtures()` and `PredictionService`) actually correct?**
  _`Fixture` has 7 INFERRED edges - model-reasoned connections that need verification._