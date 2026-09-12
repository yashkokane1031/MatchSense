# Implementation Plan: Phase 2B — Advanced Features & XGBoost Classifier

Implement the Phase 2B advanced feature pipeline (window-anchored Elo, rolling match stats, separated xG schema), decouple `BasePredictor`, build the regularized multi-class `XGBoostPredictor` with zero-window cold-start fallback, update API endpoints, and expand the walk-forward evaluation harness to benchmark XGBoost vs Dixon-Coles vs market closing lines.

## User Review Required

> [!IMPORTANT]
> - **Universal Window-Anchored Elo**: Every 4-season training window anchors Elo to $R_0 = 1500$ at Season 1, GW1. Summer mean-reversion ($0.75 R_{\text{old}} + 0.25 \times 1500$) and empirical $Q_{0.25}$ entry are applied dynamically.
> - **Cold-Start Safety Guard**: Known promoted clubs with zero prior matches in the window succeed via $Q_{0.25}$ Elo and `np.nan` rolling stats (native XGBoost split-routing). Unrecognized / fake clubs return HTTP 404.
> - **Direct Model Comparison**: $\Delta\text{RPS} = \text{XGBoost} - \text{DixonColes}$, with mandated column header `diff_RPS (XGB - DC) [negative = XGBoost better]` and an explicit `Better` column.
> - **Sanity Gate 2 Range**: Pooled XGBoost RPS $\in [0.180, 0.240]$.

## Open Questions

None. All modeling, architecture, and boundary decisions were resolved and approved in the design specification.

## Proposed Changes

Grouped across 7 sequential tasks:

### Dependencies & Setup
- **`pyproject.toml`**: Add `xgboost>=2.0` dependency.

### Feature Engineering
- **[NEW] `ml/features/elo.py`**: Window-anchored soccer Elo engine ($H_{\text{elo}}=65$, dynamic margin-of-victory $K_{\text{base}}=24$, summer reversion, $Q_{0.25}$ promoted entry).
- **[NEW] `ml/features/match_stats.py`**: Rolling 5-match shot, SOT, SOT ratio, and corner metrics from `football-data.co.uk`.
- **[NEW] `ml/features/xg.py`**: Separated Understat xG metrics (`home_rolling_xg_for/against/diff`, `away_rolling_xg_for/against/diff`), passing `np.nan` when absent.
- **[MODIFY] `ml/features/pipeline.py`**: Integrate match stats, xG, and window-anchored Elo joining.

### Modeling & Interface Decoupling
- **[MODIFY] `ml/models/base.py`**: Decouple `predict_score_distribution` and `get_team_strengths` into optional methods returning `None` by default.
- **[NEW] `ml/models/xgboost_model.py`**: Regularized multi-class gradient boosted classifier with native NaN routing and zero-window cold-start fallback.

### API & Serving
- **[MODIFY] `backend/models/schemas.py`**: Make `predicted_score` and `score_distribution` nullable.
- **[MODIFY] `backend/services/prediction.py`**: Support XGBoost prediction, cache window-anchored Elo at startup.
- **[MODIFY] `backend/api/routes/predictions.py`**: Return 404 for strengths if unsupported by model.
- **[MODIFY] `backend/api/routes/health.py`**: Dynamically report `n_features`.

### Walk-Forward CV & Multi-Model Reporting
- **[MODIFY] `ml/evaluation/walk_forward.py`**: Evaluate XGBoost alongside Dixon-Coles and baselines.
- **[MODIFY] `ml/evaluation/report.py`**: Direct model-vs-model comparative report with explicit header and `Better` column.
- **[MODIFY] `scripts/evaluate.py`**: Add `--model {dixon_coles,xgboost,all}` CLI option and automated Sanity Gates 1–5.

## Verification Plan

### Automated Tests
- Unit tests:
  - `tests/unit/test_elo.py`
  - `tests/unit/test_match_stats.py`
  - `tests/unit/test_xgboost_model.py`
  - `tests/unit/test_api.py`
  - `tests/unit/test_features.py`
- Integration tests:
  - `tests/integration/test_multi_model_cv.py`
- Sanity Gates:
  - `uv run python scripts/evaluate.py --model all`
  - Gate 1: Probability sums to $1.0 \pm 10^{-5}$
  - Gate 2: RPS $\in [0.180, 0.240]$
  - Gate 3: Cold-start safety test (promoted succeeds, fake 404s)
  - Gate 4: Runtime $< 30$ seconds
  - Gate 5: All 81 existing tests pass
