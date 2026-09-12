# Graph Report - MatchSense  (2026-09-13)

## Corpus Check
- 80 files · ~46,071 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 860 nodes · 1176 edges · 69 communities (50 shown, 5 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 19 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `126aa7bf`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_features.py
- main.py
- PredictionService
- parse_season_csv
- TestPoissonProperties
- TestDixonColesModel
- Base
- BasePredictor
- .fit
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
- evaluate_significance_suite
- predictions.py
- Evaluation Core (`ml/evaluation/`)
- compute_calibration
- run_walk_forward_cv
- test_metrics.py
- MatchSense — Phase 1 Implementation & Training Walkthrough
- EloEngine
- Global Constraints
- 2. Statistical Significance vs Baselines (Primary: Per-Fold Independent)
- .predict_score_distribution
- XGBoostPredictor
- EvaluationReport
- build_match_features
- evaluate.py
- test_pipeline.py
- Proposed Changes
- wilcoxon_rps_test
- compute_form_features
- compute_temporal_features
- compute_match_stats_features
- Tasks
- 2. Statistical Significance vs Baselines (Primary: Per-Fold Independent)
- 2. Benchmark Evaluation Results (Dixon-Coles vs Baselines)
- form.py
- MatchSense — Multi-Model Comparative Evaluation: XGBoost vs. Dixon-Coles
- TestMediumScaleConvergence
- TestFeaturePipeline
- test_walk_forward.py
- TestPredictionEndpoints
- TestTeamEndpoints
- health_check
- .fit

## God Nodes (most connected - your core abstractions)
1. `DixonColesModel` - 47 edges
2. `BasePredictor` - 25 edges
3. `XGBoostPredictor` - 25 edges
4. `build_match_features()` - 20 edges
5. `TestDixonColesModel` - 18 edges
6. `run_walk_forward_cv()` - 16 edges
7. `parse_season_csv()` - 15 edges
8. `compute_form_features()` - 14 edges
9. `wilcoxon_rps_test()` - 13 edges
10. `_tau()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `set_model()` --uses--> `BasePredictor`  [INFERRED]
  backend/api/dependencies.py → ml/models/base.py
- `lifespan()` --uses--> `DixonColesModel`  [INFERRED]
  backend/api/main.py → ml/models/dixon_coles.py
- `PredictionService` --uses--> `BasePredictor`  [INFERRED]
  backend/services/prediction.py → ml/models/base.py
- `TestFullPipeline` --uses--> `PredictionService`  [INFERRED]
  tests/integration/test_pipeline.py → backend/services/prediction.py
- `test_xgboost_predictor_satisfies_base_interface()` --uses--> `BasePredictor`  [INFERRED]
  tests/unit/test_xgboost_model.py → ml/models/base.py

## Import Cycles
- None detected.

## Communities (69 total, 5 thin omitted)

### Community 0 - "test_features.py"
Cohesion: 0.16
Nodes (12): compute_h2h_features(), _empty_h2h_features(), DataFrame, Timestamp, Head-to-head feature engineering. Computes historical H2H statistics between…, Compute head-to-head features between two teams. Looks at the last…, Return H2H features with all null values (no historical meetings)., Tests for feature engineering. Covers: form features, H2H features, season-… (+4 more)

### Community 1 - "main.py"
Cohesion: 0.11
Nodes (17): Set the global model reference. Used by lifespan and tests., set_model(), create_app(), lifespan(), FastAPI application factory for MatchSense. Loads the fitted Dixon-Coles model…, Load the model at startup, clean up on shutdown., Create and configure the FastAPI application., Health check endpoint. Returns model metadata and system status. Useful for… (+9 more)

### Community 2 - "PredictionService"
Cohesion: 0.22
Nodes (6): PredictionService, Any, Service providing match prediction operations., Predict match outcome probabilities, most likely score, and distribution. Args:…, Return sorted list of known teams., Return attack and defense parameters for team. Raises: ValueError: If model…

### Community 3 - "parse_season_csv"
Cohesion: 0.10
Nodes (22): compute_implied_probabilities(), download_season_csv(), load_all_seasons(), normalize_team_name(), parse_season_csv(), DataFrame, Path, Data ingestion pipeline for football-data.co.uk CSVs. Downloads, parses,… (+14 more)

### Community 4 - "TestPoissonProperties"
Cohesion: 0.14
Nodes (10): given, settings, Property-based tests for Dixon-Coles model., τ must be positive for typical football scoring rates and empirical ρ., τ must be exactly 1.0 for all scores where both teams score 2+., Score distribution must sum to ~1.0 for any valid matchup., All probabilities must be >= 0., P(H) + P(D) + P(A) must sum to ~1.0 for any matchup. (+2 more)

### Community 5 - "TestDixonColesModel"
Cohesion: 0.06
Nodes (17): All score probabilities must be >= 0., Most likely score should be reasonable (not negative, not absurd)., Predicting with unknown team should raise ValueError when allow_unknown=False., Predicting with unknown team should succeed when allow_unknown=True., Predicting without fit() should raise RuntimeError., Save and load should produce identical predictions., get_team_strengths() should return dict for all teams., get_model_info() should return expected metadata. (+9 more)

### Community 6 - "Base"
Cohesion: 0.06
Nodes (36): Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online(), Pydantic settings for MatchSense configuration. Loads from environment…, Application configuration loaded from environment variables., Settings, Base (+28 more)

### Community 7 - "BasePredictor"
Cohesion: 0.13
Nodes (13): ABC, get_model(), Dependency injection for FastAPI routes. Holds the global model reference and…, Get the loaded model instance. Raises if model not loaded., Prediction service encapsulating prediction domain logic., Get the model instance, falling back to dependency injector., BasePredictor, Abstract base class for prediction models. All models (Dixon-Coles, XGBoost in… (+5 more)

### Community 8 - ".fit"
Cohesion: 0.17
Nodes (9): DataFrame, ndarray, Pack model parameters into a flat vector for the optimizer. Layout: [alpha_2,…, Unpack a flat parameter vector into named parameters. Returns: Tuple of…, Vectorized negative log-likelihood (to minimize). L = -Σ w(t) * [log(τ) +…, Fit the Dixon-Coles model on historical match data. Args: matches: DataFrame…, Compute exponential time-decay weights for each match. More recent matches…, _time_decay_weights() (+1 more)

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
Cohesion: 0.11
Nodes (14): DixonColesModel, Path, Predict outcome probabilities for a match., Predict the joint score probability distribution., Return attack/defense strengths for all teams., Return metadata about the fitted model., Serialize the fitted model to disk. Args: path: File path to save to (typically…, Deserialize a fitted model from disk. Args: path: File path to load from.… (+6 more)

### Community 35 - "MatchSense — Evaluation Suite Design Spec (Phase 2A)"
Cohesion: 0.07
Nodes (28): 1. Executive Summary, 2. Architecture & Module Structure, 3.1 Ranked Probability Score (RPS), 3.2 Multi-Category Brier Score, 3.3 Multi-Class Log-Loss (Cross-Entropy), 3.4 Categorical Accuracy, 3. Mathematical Foundations & Metrics (`ml/evaluation/metrics.py`), 4.1 Wilcoxon Signed-Rank Test on Paired $\Delta \text{RPS}$ (+20 more)

### Community 36 - "evaluate_significance_suite"
Cohesion: 0.15
Nodes (17): evaluate_significance_suite(), mcnemar_accuracy_test(), McNemarResult, Any, DataFrame, ndarray, Hypothesis testing for comparative model evaluation., McNemar's test for paired classification accuracy. Uses continuity correction… (+9 more)

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
Cohesion: 0.17
Nodes (16): compute_accuracy(), compute_brier_score(), compute_log_loss(), ndarray, Mathematical evaluation metrics for football match prediction., Compute multi-category Brier score. Args: probs: Array of shape (N, 3).…, Compute multi-class cross-entropy log-loss. Args: probs: Array of shape (N, 3).…, Compute binary classification correctness. Args: probs: Array of shape (N, 3).… (+8 more)

### Community 41 - "test_metrics.py"
Cohesion: 0.14
Nodes (17): compute_rps(), Compute Ranked Probability Score for 3-outcome ordered events (H < D < A). RPS…, Unit tests for probabilistic and categorical evaluation metrics., Certain home win prediction when home win occurs should give RPS = 0., Certain away win prediction when home win occurs should give maximum RPS = 1., Predicting Draw when Home wins should give lower RPS penalty than predicting…, RPS should handle 2D batch arrays correctly., Multi-category Brier score ranges from 0.0 to 2.0. (+9 more)

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

### Community 47 - "XGBoostPredictor"
Cohesion: 0.13
Nodes (14): Any, DataFrame, Discriminative match outcome predictor using regularized gradient-boosted trees., Index precomputed bounded features for fast lookup during CV., Return model metadata for health endpoint and status reporting., Fit XGBoost classifier on historical match window., XGBoostPredictor, mock_training_data() (+6 more)

### Community 48 - "EvaluationReport"
Cohesion: 0.12
Nodes (13): EvaluationReport, Any, Comprehensive evaluation scorecard generator., Generate full GitHub-flavored Markdown scorecard., Convert report metrics into a flattened dictionary., Print markdown report to stdout., Generate comprehensive GitHub-flavored Markdown comparative scorecard., Print comparative markdown report to stdout. (+5 more)

### Community 49 - "build_match_features"
Cohesion: 0.16
Nodes (14): build_feature_matrix(), build_match_features(), DataFrame, Timestamp, Feature pipeline orchestrator. Combines form, H2H, temporal, match statistics,…, Build feature vectors for ALL matches in the dataset. Processes matches in…, Build the complete feature vector for a single match. All features use ONLY…, compute_rolling_xg() (+6 more)

### Community 50 - "evaluate.py"
Cohesion: 0.20
Nodes (15): ComparisonReport, Multi-model comparative evaluation report for XGBoost vs Dixon-Coles., Namespace, _build_model_report(), _compute_head_to_head(), _compute_market_comparison(), main(), parse_args() (+7 more)

### Community 51 - "test_pipeline.py"
Cohesion: 0.14
Nodes (10): DataFrame, Pandera validation schemas for match data. Validates data integrity at…, Check that FTR is consistent with FTHG/FTAG., _result_matches_goals(), Dixon-Coles model for football match prediction. Implements the Dixon & Coles…, main(), Seed data script: download historical data, validate, fit model. Usage: uv run…, Download data, validate, fit model, and save. (+2 more)

### Community 52 - "Proposed Changes"
Cohesion: 0.17
Nodes (11): API & Serving, Automated Tests, Dependencies & Setup, Feature Engineering, Implementation Plan: Phase 2B — Advanced Features & XGBoost Classifier, Modeling & Interface Decoupling, Open Questions, Proposed Changes (+3 more)

### Community 53 - "wilcoxon_rps_test"
Cohesion: 0.18
Nodes (11): Paired Wilcoxon signed-rank test on match-by-match RPS differences. Uses Pratt…, wilcoxon_rps_test(), mini_league_dataset(), fixture, Integration test for multi-model walk-forward cross validation and comparison., Small realistic 6-team dataset across 2 seasons with match stats., test_multi_model_cv_execution_and_comparison(), Identical models should return p-value = 1.0 and zero difference. (+3 more)

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
Cohesion: 0.25
Nodes (7): 1. Executive Summary & Out-of-Sample Performance, 2. Direct Head-to-Head Comparison: XGBoost vs. Dixon-Coles, 3. Performance vs. Market Consensus Lines (1,140 Matches), 4. Probability Calibration & Reliability Summary, 5. Financial Simulation & ROI (Edge >= 5%), 6. Automated Sanity Verification Gates, MatchSense — Multi-Model Comparative Evaluation: XGBoost vs. Dixon-Coles

### Community 62 - "TestMediumScaleConvergence"
Cohesion: 0.25
Nodes (6): DataFrame, fixture, Test model convergence at realistic scale. This catches optimization bugs that…, Generate a synthetic 25-team, 500-match dataset., Model should converge on 25-team, 500-match dataset., TestMediumScaleConvergence

### Community 63 - "TestFeaturePipeline"
Cohesion: 0.25
Nodes (5): Test the full feature pipeline orchestrator., Pipeline should return features for both teams plus H2H., Pipeline should return rolling shot and corner statistics for both teams., xG metrics must be separate columns, never overwriting or mingling with shot…, TestFeaturePipeline

### Community 64 - "test_walk_forward.py"
Cohesion: 0.29
Nodes (6): fixture, Unit tests for rolling fixed-window walk-forward cross validation., Create 5 teams across 2 small test seasons (20 matches per season)., Walk forward CV runs on test season using rolling 1-season window., synthetic_seasons_data(), test_walk_forward_execution()

### Community 67 - "health_check"
Cohesion: 0.67
Nodes (3): health_check(), get, Return API health status and model metadata.

## Knowledge Gaps
- **177 isolated node(s):** `matchsense`, `[NEW] `matchsense/pyproject.toml``, `[NEW] `matchsense/docker-compose.yml``, `[NEW] `matchsense/.gitignore``, `[NEW] Directory skeleton` (+172 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 494 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DixonColesModel` connect `DixonColesModel` to `test_walk_forward.py`, `main.py`, `TestPoissonProperties`, `TestDixonColesModel`, `Base`, `BasePredictor`, `.fit`, `Database Schema & Migrations`, `evaluate.py`, `test_pipeline.py`, `wilcoxon_rps_test`, `TestMediumScaleConvergence`, `_tau`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Why does `BasePredictor` connect `BasePredictor` to `main.py`, `PredictionService`, `DixonColesModel`, `.fit`, `run_walk_forward_cv`, `.predict_score_distribution`, `XGBoostPredictor`, `build_match_features`, `test_pipeline.py`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `XGBoostPredictor` connect `XGBoostPredictor` to `test_walk_forward.py`, `main.py`, `PredictionService`, `BasePredictor`, `run_walk_forward_cv`, `build_match_features`, `evaluate.py`, `wilcoxon_rps_test`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `DixonColesModel` (e.g. with `lifespan()` and `main()`) actually correct?**
  _`DixonColesModel` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `BasePredictor` (e.g. with `get_model()` and `set_model()`) actually correct?**
  _`BasePredictor` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `matchsense`, `[NEW] `matchsense/pyproject.toml``, `[NEW] `matchsense/docker-compose.yml`` to the rest of the system?**
  _177 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10541310541310542 - nodes in this community are weakly interconnected._