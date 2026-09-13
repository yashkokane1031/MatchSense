# Walkthrough: Two-Pass Joint Optimization & Pipeline Integration Verification

This document summarizes the resolution of the methodological small-sample shrinkage concern in Dixon-Coles, the end-to-end integration testing of `main()`, and the verification of XGBoost at $n=3$.

---

## 1. Dixon-Coles Two-Pass Joint Optimization (with Parameter Exclusion)

### Root Problem
When newly promoted clubs with small sample sizes ($< 5$ matches in the sliding window) scored or conceded 0 goals (e.g., Coventry scored 0 goals in 3 matches, Hull conceded 0 goals in 3 matches), standard Poisson MLE collapsed to the parameter boundary ($\alpha = 0.01$, $\beta = 0.01$). 
Previously, post-hoc substitution adjusted Coventry and Hull to empirical promoted priors ($P_{25}^{\text{att}} = 0.6097$, $P_{75}^{\text{def}} = 1.9590$) *after* convergence, leaving shared parameters ($\gamma = 1.2018$, $\rho = -0.1432$) fit around degenerate boundary values.

### Principled Architectural Solution
Rather than zero-width bounds `(prior, prior)`—which can trigger active-constraint warnings or solver-specific gradient noise in L-BFGS-B—we generalized the reference-team parameter exclusion mechanism:
1. **Pass 1 (Unconstrained Fit)**: Fits standard $2N + 1$ parameters with reference team $\alpha_{\text{ref}} = 1.0$ fixed.
2. **Boundary Collapse Detection**: Iterates over all teams with $< 5$ matches in the training window. Any teams with $\hat{\alpha} \le 0.15$ or $\hat{\beta} \le 0.15$ are pinned to empirical promoted priors ($P_{25}^{\text{att}}$, $P_{75}^{\text{def}}$ derived from established teams with $\ge 10$ matches).
3. **Pass 2 (Joint Re-Optimization via Parameter Exclusion)**:
   - The pinned parameters are completely excluded from the optimizer vector, reducing the parameter count from $55 \to 53$.
   - The remaining free parameters are warm-started from Pass 1 values with strictly open standard bounds `(0.01, 5.0)`, `(0.5, 3.0)`, `(-1.0, 1.0)`.
   - $\gamma$, $\rho$, and all free teams' attack and defense parameters optimize jointly conditional on the pinned priors.
4. **Finite Bound & Safeguard**: Capped at two passes. If any small-sample collapse persists after Pass 2, a warning is logged and `model._has_boundary_collapse = True` is recorded for Gate 2A auditing.

### Observed Parameter Shifts on Real 2026-27 League Data
- **Pass 1**: $\gamma = 1.2018$, $\rho = -0.1432$ (Coventry $\alpha = 0.0100$, Hull $\beta = 0.0100$)
- **Pass 2**: $\gamma = 1.1935$ ($\Delta\gamma = -0.0083$), $\rho = -0.1340$ ($\Delta\rho = +0.0092$)
- **Iterations & Runtime**: Converged in 85 iterations (0.47 seconds).

---

## 2. End-to-End Integration Test for `main()`

### Problem
Previously, unit tests exercised pipeline phase functions in isolation, masking "glue-code" failures such as silent `main()` skips, unpopulated database records, and missing class methods.

### Implementation: `test_main_end_to_end_pipeline_wiring`
Added in [`tests/integration/test_sync_pipeline.py`](file:///d:/Yash/Kokane/Projects/MatchSense/tests/integration/test_sync_pipeline.py):
- Mocks only the external HTTP boundary (`download_season_csv` and `FootballDataClient.get_scheduled_fixtures`).
- Injects a real test database session factory into `scripts.sync_pipeline.SessionLocal`.
- Invokes `sync_pipeline.main()` end-to-end through Phase A, Phase B1, and Phase B2.
- Verifies:
  1. `Match` records (2) and `Fixture` records (1) are committed to the DB.
  2. `ModelArtifact` for `dixon_coles` is active with valid metadata in the DB.
  3. `ModelArtifact` for `xgboost` is active with valid metadata in the DB (prompted adding `get_model_info()` and `@property model_name` to `XGBoostPredictor`).
  4. The scheduled fixture's `precomputed_predictions` contains both `"dixon_coles"` and `"xgboost"` entries without overwriting.

---

## 3. XGBoost Transitional Handling at $n=3$

Confirmed via code analysis and live booster inspection:
- **Elo Ratings**: Coventry and Hull entered at $Q_{0.25}$ (~1445) at the 2026-27 boundary, then dynamically updated through their 3 real matches (Coventry fell to **1409.16**, Hull rose to **1467.87**).
- **In-Window Routing**: In [`XGBoostPredictor.predict_proba()`](file:///d:/Yash/Kokane/Projects/MatchSense/ml/models/xgboost_model.py#L161-L204), `home_in_window` is `True`, so the cold-start NaN-masking branch is skipped.
- **Form Features**: [`compute_form_features()`](file:///d:/Yash/Kokane/Projects/MatchSense/ml/features/form.py#L50-L84) evaluates the 3 available matches (`matches_available=3`, real points, real goals), handling the transitional state gracefully.

---

## 4. Verification Summary

| Test Suite | Result | Details |
| :--- | :--- | :--- |
| **Backend Pytest** | **142 / 142 Passing** (100%) | Includes 3 new two-pass unit tests and `test_main_end_to_end_pipeline_wiring` |
| **Frontend Vitest** | **18 / 18 Passing** (100%) | Full client-side component and resilience suite |
| **Live Pipeline Execution** | **Successful** | Real DB updated with two-pass Dixon-Coles and XGBoost models; fallback pickles synced |
| **Knowledge Graph** | **Updated** | 1,453 nodes, 2,107 edges across 115 communities |
| **Git Commit** | `5311813` | Clean commit preserving complete historical audit trail |
