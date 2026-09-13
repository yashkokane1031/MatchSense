# MatchSense — Phase 2B Implementation and Evaluation Walkthrough

Phase 2B (**Advanced Feature Engineering, Regularized XGBoost Classifier & Multi-Model Comparative Evaluation**) is complete, fully tested, and verified on real Premier League data across 7 seasons (2,660 matches) and 3 rolling out-of-sample test seasons (1,140 matches).

---

## 1. Architecture Overview & Components Delivered

Phase 2B expands MatchSense from a single generative model (Dixon-Coles) into a multi-model comparative prediction system:

```
ml/
├── features/
│   ├── elo.py          # Window-anchored Elo rating engine (MoV multiplier, summer reversion, Q0.25 entry)
│   ├── match_stats.py  # Rolling match stats (shots, SOT, SOT ratio, corners)
│   ├── xg.py           # Separated Understat xG schema (isolated columns, never conflated with shots)
│   └── pipeline.py     # Unified feature orchestrator with precomputed bounded feature caching
├── models/
│   ├── base.py         # Decoupled BasePredictor (predict_proba mandatory; scoreline/strengths optional)
│   ├── dixon_coles.py  # Poisson intensity model (predict_proba, scoreline, attack/defense parameters)
│   └── xgboost_model.py # Multi-class gradient boosted trees with native NaN routing & cold-start fallback
backend/
├── models/schemas.py   # Nullable predicted_score and score_distribution
├── services/prediction.py # Unified prediction service with window-anchored Elo startup cache
└── api/routes/         # 404 for team strengths on XGBoost, dynamic n_features in /health
reports/
└── model_comparison_evaluation.md # Full 3-season comparative scorecard
```

---

## 2. Key Architectural Decisions

1. **Universal Window-Anchoring Principle for Elo**:
   - Every 4-season training window (whether a cross-validation fold or a sliding live serving window) anchors all active teams to $R_0 = 1500$ at Season 1, Gameweek 1 of that window.
   - Summer reversion applies at each season transition: $R_{\text{new}} = 0.75 R_{\text{old}} + 0.25 \times 1500$.
   - Promoted clubs enter at the lower quartile of surviving clubs: $Q_{0.25}(\{R_{\text{surviving}}\})$.
   - This eliminates long-term cumulative drift, historical data leakage, and ensures 100% train/serve parity.
2. **Strict Schema Boundary for xG**:
   - In-repo match shot metrics and Understat xG metrics are strictly isolated. Columns like `rolling_shots_for` and `rolling_xg_for` never share names or fallback into each other. When xG is unavailable, XGBoost routes `np.nan` through learned missing-value branches.
3. **Decoupled Predictor Contract**:
   - `predict_proba()` is the sole mandatory method on `BasePredictor`.
   - `predict_score_distribution()` and `get_team_strengths()` return `None` by default.
   - The API cleanly handles this: `GET /api/v1/teams/{team}/strengths` returns HTTP 404 for XGBoost, and prediction responses return `null` for `predicted_score` and `score_distribution`.
4. **Cold-Start Fallback Safety**:
   - Known promoted clubs with zero prior matches in the window succeed via $Q_{0.25}$ Elo and `np.nan` rolling features (handled natively by tree splits). Fake club names return HTTP 404.
5. **Optimized "Compute Once, Slice by Index" CV Execution**:
   - Bounded lookback features (rolling form, H2H, rolling match stats) are computed once chronologically across the full dataset.
   - At each gameweek refit, only the window-anchored Elo ratings are recomputed and joined in $O(1)$ time, reducing weekly refit overhead from ~47s down to ~1.25s.

---

## 3. Out-of-Sample Benchmark Evaluation (1,140 Matches)

Full markdown reports:
- Comparative Scorecard: [`reports/model_comparison_evaluation.md`](file:///d:/Yash%20Kokane/Projects/MatchSense/reports/model_comparison_evaluation.md)
- Dixon-Coles Baseline: [`reports/baseline_evaluation.md`](file:///d:/Yash%20Kokane/Projects/MatchSense/reports/baseline_evaluation.md)
- XGBoost Scorecard: [`reports/xgboost_evaluation.md`](file:///d:/Yash%20Kokane/Projects/MatchSense/reports/xgboost_evaluation.md)

### 3.1 Aggregate Performance Across 3 Test Seasons

| Architecture | Model Class | Matches | RPS | Brier Score | Log-Loss | Accuracy |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Dixon-Coles** | Generative Poisson (Bivariate) | 1,140 | 0.2007 | 0.5850 | 0.9872 | 52.3% |
| **XGBoost** | Discriminative Gradient Boosted Trees | 1,140 | 0.2036 | 0.5927 | 0.9962 | 53.2% |
| **Market Consensus (Avg)** | Closing Odds Implied Probabilities | 1,140 | 0.1955 | 0.5732 | 0.9634 | 54.2% |

### 3.2 Direct Head-to-Head Comparison (XGBoost vs. Dixon-Coles)

Direct paired statistical tests on matched out-of-sample fixture predictions:

| Season / Scope | Matches | RPS (DC) | RPS (XGB) | diff_RPS (XGB - DC) [negative = XGBoost better] | Wilcoxon p-value | Acc (DC) | Acc (XGB) | McNemar p-value | Better |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **2023-24** | 380 | 0.1905 | 0.1933 | +0.0027 | 0.3540 | 57.6% | 59.5% | 0.2812 | **Tied / Not Significant** |
| **2024-25** | 380 | 0.2000 | 0.2044 | +0.0045 | 0.0712 | 52.9% | 52.6% | 1.0000 | **Tied / Not Significant** |
| **2025-26** | 380 | 0.2116 | 0.2132 | +0.0016 | 0.3737 | 46.3% | 47.6% | 0.4576 | **Tied / Not Significant** |
| **Pooled (3 Seasons)** | **1,140** | **0.2007** | **0.2036** | **+0.0029** | **0.0329** | **52.3%** | **53.2%** | **0.3049** | **Dixon-Coles** |

> [!NOTE]
> **Interpretation of Head-to-Head Findings**:
> - **RPS Metric**: Across all 3 individual folds, the models are statistically indistinguishable ($p > 0.05$). On the pooled 1,140 matches, Dixon-Coles retains a slight, statistically significant advantage in probabilistic score quality ($\Delta\text{RPS} = +0.0029$, Wilcoxon $p = 0.0329$).
> - **Accuracy Metric**: While XGBoost shows a +0.9% higher nominal classification accuracy pooled (53.2% vs 52.3%), paired McNemar tests confirm this difference is **statistically indistinguishable from noise** ($p = 0.3049$ pooled; $p > 0.25$ across all individual folds). Neither model holds a statistically verifiable accuracy advantage (+0.9% pooled, not statistically significant, McNemar $p = 0.30$).
> - **Caveat on Pooled Testing**: The pooled 1,140-match significance test combines overlapping rolling training windows across adjacent seasons; per-fold test statistics provide the primary independent verification.

### 3.3 Probability Calibration & Reliability Summary

| Metric | Dixon-Coles | XGBoost | Better Calibration |
| :--- | :---: | :---: | :--- |
| **Overall ECE** | 0.0300 (3.0%) | 0.0289 (2.9%) | **XGBoost** |
| **Home ECE** | 0.0292 (2.9%) | 0.0279 (2.8%) | **XGBoost** |
| **Draw ECE** | 0.0259 (2.6%) | 0.0295 (2.9%) | **Dixon-Coles** |
| **Away ECE** | 0.0350 (3.5%) | 0.0292 (2.9%) | **XGBoost** |
| **Home MCE** | 0.1310 (13.1%) | 0.1092 (10.9%) | **XGBoost** |
| **Draw MCE** | 0.0865 (8.6%) | 0.4129 (41.3%) | **Dixon-Coles** |
| **Away MCE** | 0.4384 (43.8%) | 0.8009 (80.1%) | **Dixon-Coles** |

#### Away Outcome Reliability Bins Breakdown (1,140 Matches)

| Bin Range | Dixon-Coles Matches | DC Gap | XGBoost Matches | XGB Gap |
| :--- | :---: | :---: | :---: | :---: |
| [0.0, 0.1] | 87 | 0.0256 | 55 | 0.0051 |
| [0.1, 0.2] | 193 | 0.0264 | 292 | 0.0138 |
| [0.2, 0.3] | 249 | 0.0126 | 231 | 0.0119 |
| [0.3, 0.4] | 220 | 0.0258 | 163 | 0.0314 |
| [0.4, 0.5] | 169 | 0.0894 | 169 | 0.0469 |
| [0.5, 0.6] | 108 | 0.0267 | 114 | 0.0637 |
| [0.6, 0.7] | 74 | 0.0176 | 86 | 0.0278 |
| [0.7, 0.8] | 28 | 0.0792 | 29 | 0.0969 |
| [0.8, 0.9] | 10 | 0.1361 | 1 | 0.8009 |
| [0.9, 1.0] | 2 | 0.4384 | 0 | 0.0000 |

> **Context on Extreme Away MCE & Overall ECE**:
> - For Dixon-Coles, the worst-case bin `[0.9, 1.0]` contains only $|B_m| = 2$ matches (1 win, obs 0.5000 vs 0.9384 pred $\to$ gap 0.4384). Its weighted contribution to ECE is $2/1140 \times 0.4384 = 0.00077$.
> - For XGBoost, the worst-case bin `[0.8, 0.9]` contains **exactly 1 match** ($|B_m| = 1$, 0 wins, obs 0.0 vs 0.8009 pred $\to$ gap 0.8009), while bin `[0.9, 1.0]` has 0 matches. Its weighted contribution to ECE is $1/1140 \times 0.8009 = 0.00070$.
> - Both models exhibit the identical small-sample tail artifact in rare high-confidence away predictions. Across all well-populated bins ($|B_m| \ge 29$), both models calibrate smoothly within 0.5%–9.7%. Their overall ECE values (2.89% vs 3.00%) represent virtually identical calibration quality; describing XGBoost as having "superior calibration" is not justified once the tail bins are examined.

---

## 4. Automated Sanity Verification Gates

| Gate | Criterion | Threshold / Requirement | Measured Value | Status |
| :---: | :--- | :--- | :--- | :---: |
| **Gate 1** | Mathematical Invariants | $\sum P(c) = 1.0 \pm 10^{-5}, P(c) \ge 0$ | `max_dev = 1.11e-16, non-negative = True` | **[PASS]** |
| **Gate 2** | RPS Empirical Sanity Range | Pooled RPS $\in [0.180, 0.240]$ | `Pooled RPS = 0.2036` | **[PASS]** |
| **Gate 3** | Cold-Start Safety Fallback | Promoted succeeds via $Q_{0.25}$ Elo; fake 404s | `Luton prob_sum = 1.0000` | **[PASS]** |
| **Gate 4** | Execution Budget (Walk-Forward CV) | 3-Fold Walk-Forward CV $< 180.0$s per model | `XGBoost: 115.85s (1.02s/GW); Dixon-Coles: 125.02s (1.10s/GW)` | **[PASS]** |
| **Gate 5** | Regression Guard | All tests continue to pass | `99 passed, 0 failed across full suite` | **[PASS]** |

### Refit Complexity & Execution Budget Analysis (Gate 4)
- **Dixon-Coles Runtime (125.02s / 1.10s per refit)**: Dixon-Coles operates strictly on raw match fixtures (`HomeTeam`, `AwayTeam`, `Date`, `FTHG`, `FTAG`) and does NOT evaluate feature pipelines. Its runtime is driven entirely by numerical optimization of 51–55 parameters ($2N+1$ for $N \in [25, 27]$ clubs across the rolling 4-season window: $(N-1)$ free attack + $N$ defense + $\gamma$ + $\rho$, with $\alpha_{\text{ref}} = 1.0$ pinned). Enabling parameter warm-starting across consecutive gameweeks reduced average optimization iterations by ~38%, reducing total 3-season CV runtime from 181.88s pre-warm-start to 125.02s (1.10s per refit).
- **XGBoost Runtime (115.85s / 1.02s per refit)**: Includes dynamic window-anchored Elo recomputation (105ms) and 120 regularized gradient-boosted trees over 70 features on 1,520 rows (~950ms).
- **Takeaway**: With warm-starting enabled for Dixon-Coles and precomputed bounded features for XGBoost, both models complete 3 full seasons of walk-forward cross-validation (114 sequential refits) in approximately 1.9–2.0 minutes (~1.0–1.1s per gameweek refit), comfortably within the operational budget (< 180s total, < 1.5s per gameweek).

---

## 5. Verification & Code Quality

- **Pytest Suite**: 99 tests passed in 33.21s (`tests/unit/`, `tests/property/`, `tests/integration/`).
- **Ruff Linter**: 0 errors across entire workspace (`uv run ruff check .`).
- **Mypy Type Checking**: 0 errors across 37 source files in strict mode (`uv run mypy backend/ ml/`).
- **Knowledge Graph**: AST graph updated via `graphify update .` (860 nodes, 1176 edges, 69 communities).
