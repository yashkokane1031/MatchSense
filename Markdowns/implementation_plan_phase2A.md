# MatchSense — Phase 2A Evaluation Suite Implementation Plan

> **Scope**: Metrics → Significance Tests → Calibration → Financial Backtesting → Walk-Forward Cross Validation → Reporting & CLI  
> **Milestone**: Establish a quantitative, out-of-sample benchmark across 3 full Premier League seasons (1,140 matches) comparing Dixon-Coles against Bookmakers and Naive Baselines.  
> **Spec**: [`docs/superpowers/specs/2026-09-13-evaluation-suite-design.md`](file:///d:/Yash%20Kokane/Projects/MatchSense/docs/superpowers/specs/2026-09-13-evaluation-suite-design.md)  
> **Detailed Plan**: [`docs/superpowers/plans/2026-09-13-evaluation-suite.md`](file:///d:/Yash%20Kokane/Projects/MatchSense/docs/superpowers/plans/2026-09-13-evaluation-suite.md)

---

## User Review Required

> [!IMPORTANT]
> - **Rolling 4-Season Window ($W = 1,520$ matches)**: Matches production Dixon-Coles configuration across all 3 test folds (`2023-24`, `2024-25`, `2025-26`). Requires auto-downloading 3 earlier historical seasons (`1920`, `2021`, `2122`) via our existing cached `CSVSeasonIngester`.
> - **Significance Testing Strategy**: Per-fold independent tests (Folds 1, 2, 3) are reported as primary evidence; pooled 1,140-match statistics are descriptive and carry an explicit caveat regarding temporal cluster correlation across adjacent seasons.
> - **Staking Isolation**: The 25% gameweek total exposure cap applies strictly to Quarter-Kelly staking. Flat Staking remains strictly fixed at 1.0 unit per bet as an unconstrained control.

---

## Proposed Changes

### Evaluation Core (`ml/evaluation/`)

#### [NEW] [`ml/evaluation/metrics.py`](file:///d:/Yash%20Kokane/Projects/MatchSense/ml/evaluation/metrics.py)
* Vectorized implementation of **Ranked Probability Score (RPS)** for ordered 3-outcome events ($H < D < A$).
* Multi-category Brier Score ($[0, 2]$ range).
* Multi-class Log-Loss with $\epsilon$-boundary clipping ($10^{-15}$).
* Argmax classification accuracy.

#### [NEW] [`ml/evaluation/significance.py`](file:///d:/Yash%20Kokane/Projects/MatchSense/ml/evaluation/significance.py)
* Paired **Wilcoxon signed-rank test** on match-by-match $\Delta \text{RPS}_i$ using `zero_method='pratt'` (ties retained in ranking pool, zero rank sums excluded).
* **McNemar's test** on paired $2 \times 2$ accuracy contingency table with continuity correction, falling back to exact two-sided binomial test when discordant counts $n_{10} + n_{01} < 25$.

#### [NEW] [`ml/evaluation/calibration.py`](file:///d:/Yash%20Kokane/Projects/MatchSense/ml/evaluation/calibration.py)
* 10-bin reliability diagram calculator across $H$, $D$, and $A$.
* Expected Calibration Error (ECE) and Maximum Calibration Error (MCE).

#### [NEW] [`ml/evaluation/backtest.py`](file:///d:/Yash%20Kokane/Projects/MatchSense/ml/evaluation/backtest.py)
* Expected-Value edge calculation: $\text{EV} = (p_{\text{model}} \cdot o) - 1 \ge \delta$ (default $\delta = 0.05$).
* Single-outcome max-EV conflict guard per fixture.
* Pre-gameweek bankroll sizing preventing intra-gameweek look-ahead.
* Quarter-Kelly staking ($0.25 \times \frac{\text{EV}}{o - 1}$) with 5% bet cap and 25% gameweek portfolio exposure cap.
* Flat 1-unit staking (unconstrained baseline).
* Metrics: Turnover, Net PnL, ROI %, Win %, Max Drawdown, Annualized 38-Gameweek Sharpe ($R_f = 0$), and per-bet Sharpe.

#### [NEW] [`ml/evaluation/walk_forward.py`](file:///d:/Yash%20Kokane/Projects/MatchSense/ml/evaluation/walk_forward.py)
* Rolling 4-season ($1,520$-match) cross-validation orchestrator.
* Gameweek-by-gameweek intra-season walk-forward refit (zero future leakage).
* Dynamic reference team identifiability ($\alpha = 1.0$ for max match count team in window).
* Evaluates 4 parallel baselines: Naive Uniform, Empirical Prior, Market Average implied odds, and Bet365 implied odds.

#### [NEW] [`ml/evaluation/report.py`](file:///d:/Yash%20Kokane/Projects/MatchSense/ml/evaluation/report.py)
* `EvaluationReport` dataclass with `.to_markdown()`, `.to_dict()`, and `.print_summary()`.

---

### Scripts & Verification

#### [NEW] [`scripts/evaluate.py`](file:///d:/Yash%20Kokane/Projects/MatchSense/scripts/evaluate.py)
* CLI entrypoint for running the 3-fold evaluation, printing summary scorecards, and saving `reports/baseline_evaluation.md`.

#### [NEW] Unit Tests
* `tests/unit/test_metrics.py` (known values, edge cases)
* `tests/unit/test_significance.py` (Pratt zero handling, exact binomial cutoff)
* `tests/unit/test_calibration.py` (ECE & binning accuracy)
* `tests/unit/test_backtest.py` (Kelly math, gameweek batch sizing, drawdown)
* `tests/unit/test_walk_forward.py` (rolling window maintenance, zero leakage)
* `tests/unit/test_report.py` (markdown & dict serialization)

---

## Verification Plan

### Automated Tests
1. Run all unit tests:
   ```bash
   uv run pytest tests/unit/test_metrics.py tests/unit/test_significance.py tests/unit/test_calibration.py tests/unit/test_backtest.py tests/unit/test_walk_forward.py tests/unit/test_report.py -v
   ```
2. Run full project test suite:
   ```bash
   uv run pytest
   ```
3. Type check and lint:
   ```bash
   uv run ruff check .
   uv run mypy backend/ ml/
   ```

### Manual Verification & Benchmark Execution
1. Run the evaluation script on real Premier League data across 1,140 out-of-sample matches:
   ```bash
   uv run python scripts/evaluate.py --model dixon_coles --edge 0.05 --output reports/baseline_evaluation.md
   ```
2. Verify that `reports/baseline_evaluation.md` is populated with per-season scorecards, statistical significance tests vs bookmakers, and ROI backtests.
