# MatchSense — Evaluation Suite Design Spec (Phase 2A)

**Status**: Draft for User Review  
**Date**: 2026-09-13  
**Authors**: Antigravity & Yash Kokane  
**Target Module**: `ml/evaluation/`  

---

## 1. Executive Summary

Phase 2 of MatchSense introduces advanced modeling and machine learning rigor. Before training XGBoost, integrating Elo ratings, or computing rolling xG, we require an unimpeachable, quantitative evaluation harness.

This specification defines the architecture, mathematical contracts, and implementation plan for the **MatchSense Evaluation Suite** (`ml/evaluation/`). The suite provides:
1. **Probabilistic & Categorical Metrics**: Ranked Probability Score (RPS), multi-category Brier Score, Multi-class Log-Loss, and Expected Calibration Error (ECE).
2. **Hypothesis Testing**: Per-fold Wilcoxon signed-rank tests on paired $\Delta \text{RPS}_i$ and McNemar's tests on classification accuracy, with continuity corrections and exact binomial fallbacks.
3. **Walk-Forward Cross-Validation**: Fixed 4-season ($W = 1,520$ matches) rolling window evaluated gameweek-by-gameweek across 3 full Premier League seasons ($N = 1,140$ out-of-sample matches), strictly mirroring production training regime and eliminating temporal leakage.
4. **Financial Backtesting**: Expected-value edge detection ($\text{EV} = p \cdot o - 1 \ge \delta$), conflict-guarded single-bet selection, pre-gameweek bankroll sizing (zero intra-gameweek look-ahead), Flat Staking, and Quarter-Kelly staking across Market Average and Bet365 closing odds.
5. **Scorecard Reporting & CLI**: Tabular reliability diagrams, GitHub-flavored Markdown reports, programmatic dataclasses for future MLflow logging, and a unified execution CLI (`scripts/evaluate.py`).

---

## 2. Architecture & Module Structure

The evaluation suite is organized as a decoupled functional pipeline:

```
ml/evaluation/
├── __init__.py
├── metrics.py          # Vectorized RPS, Brier, LogLoss, Accuracy
├── significance.py     # Wilcoxon signed-rank & McNemar tests
├── calibration.py      # Reliability diagrams, ECE, MCE binning
├── backtest.py         # Financial simulation, EV edge, Flat & Quarter-Kelly
├── walk_forward.py     # Rolling fixed-window CV orchestrator & baseline runner
└── report.py           # EvaluationReport dataclass, Markdown & terminal formatters
scripts/
└── evaluate.py         # CLI entrypoint for running full evaluation
tests/
└── unit/
    ├── test_metrics.py
    ├── test_significance.py
    ├── test_calibration.py
    ├── test_backtest.py
    └── test_walk_forward.py
```

### Dependency Inversion & Model Protocol
All models evaluated by `walk_forward.py` conform to `BasePredictor` (`ml/models/base.py`). The evaluation harness is model-agnostic: it accepts any class providing:
```python
def fit(self, matches: pd.DataFrame) -> "BasePredictor": ...
def predict_proba(self, home_team: str, away_team: str) -> dict[str, float]: ...
```
This enables zero-friction benchmarking across Dixon-Coles (Phase 1), XGBoost (Phase 2B), Elo-enhanced predictors, and ensemble blends.

---

## 3. Mathematical Foundations & Metrics (`ml/evaluation/metrics.py`)

For each match $i$, let:
* $\mathbf{y}_i = [y_{i,H}, y_{i,D}, y_{i,A}] \in \{0, 1\}^3$ denote the true one-hot outcome vector.
* $\mathbf{p}_i = [p_{i,H}, p_{i,D}, p_{i,A}] \in [0, 1]^3$ denote the predicted probabilities, where $\sum_c p_{i,c} = 1$.

### 3.1 Ranked Probability Score (RPS)
Accounting for the natural ordinal structure of soccer match outcomes ($H < D < A$):
$$\text{RPS}_i = \frac{1}{K-1} \sum_{r=1}^{K-1} \left( \sum_{j=1}^r p_{i,j} - \sum_{j=1}^r y_{i,j} \right)^2$$
For $K = 3$ outcomes:
$$\text{RPS}_i = \frac{1}{2} \left[ (p_{i,H} - y_{i,H})^2 + ((p_{i,H} + p_{i,D}) - (y_{i,H} + y_{i,D}))^2 \right]$$
* **Range**: $[0, 1]$, where $0$ represents perfect certainty on the correct outcome.
* **Property**: Penalizes severe directional errors (e.g. predicting heavy Home win when Away wins) significantly more than adjacent errors (predicting Draw when Away wins).

### 3.2 Multi-Category Brier Score
$$\text{Brier}_i = \sum_{c \in \{H, D, A\}} (p_{i,c} - y_{i,c})^2$$
* **Range**: $[0, 2]$.

### 3.3 Multi-Class Log-Loss (Cross-Entropy)
$$\text{LogLoss}_i = -\sum_{c \in \{H, D, A\}} y_{i,c} \ln\left( \max(\epsilon, \min(1 - \epsilon, p_{i,c})) \right)$$
where clipping boundary $\epsilon = 10^{-15}$.

### 3.4 Categorical Accuracy
$$\text{Correct}_i = \mathbb{I}(\operatorname{argmax}(\mathbf{p}_i) = \operatorname{argmax}(\mathbf{y}_i))$$

---

## 4. Statistical Significance Testing (`ml/evaluation/significance.py`)

When comparing Model $A$ against Model/Baseline $B$ across $N$ matched out-of-sample predictions:

### 4.1 Wilcoxon Signed-Rank Test on Paired $\Delta \text{RPS}$
RPS differences between two competing models on the same match $d_i = \text{RPS}_{A, i} - \text{RPS}_{B, i}$ are continuous, bounded, and generally non-normally distributed, invalidating Student's paired t-test.
* **Method**: `scipy.stats.wilcoxon(d, zero_method='pratt', alternative='two-sided')`.
* **Pratt Zero-Handling**: Zero-differences are retained in the ranking pool so they contribute to sample size and rank positions; only their signed-rank contributions are excluded from the test statistic $W$.
* **Outputs**: Test statistic $W$, sample median difference, and two-sided $p$-value.

### 4.2 McNemar's Test on Binary Accuracy
Evaluates discordance in classification correctness via a $2 \times 2$ contingency table:
$$\begin{pmatrix} n_{11} & n_{10} \\ n_{01} & n_{00} \end{pmatrix}$$
* $n_{10}$: Model $A$ correct, Model $B$ incorrect.
* $n_{01}$: Model $B$ correct, Model $A$ incorrect.
* **Continuity-Corrected $\chi^2$** (for $n_{10} + n_{01} \ge 25$):
  $$\chi^2 = \frac{(|n_{10} - n_{01}| - 1)^2}{n_{10} + n_{01}}, \qquad p = 1 - F_{\chi^2_1}(\chi^2)$$
* **Exact Binomial Test Fallback** (for $n_{10} + n_{01} < 25$):
  $$p = 2 \times \sum_{k=0}^{\min(n_{10}, n_{01})} \binom{n_{10} + n_{01}}{k} 0.5^{n_{10} + n_{01}}$$

### 4.3 Reporting Strategy: Per-Fold Primary vs. Pooled Caveat (Option A)
* **Primary Evidence**: Statistical tests are evaluated independently **per fold** ($N = 380$ matches each), where matches within each single season satisfy the temporal independence requirement.
* **Supplementary Pooled View**: Pooled significance across all 1,140 matches is reported as a descriptive aggregate accompanied by an explicit caveat:
  > *Caveat: The pooled 1,140-match significance test combines overlapping training windows across adjacent seasons; per-fold test statistics provide the primary independent verification.*

---

## 5. Walk-Forward Cross-Validation Engine (`ml/evaluation/walk_forward.py`)

### 5.1 Dataset Expansion & Window Sizing
To mirror the production model configuration (`dixon_coles_latest.pkl`), the training window is strictly fixed at:
$$W = 4 \text{ seasons} = 1,520 \text{ matches}$$
To evaluate 3 out-of-sample seasons ($1,140$ matches), the dataset will be expanded to 7 seasons (`2019-20` through `2025-26`) via `CSVSeasonIngester`:
* **Fold 1**: Train on `19-20`, `20-21`, `21-22`, `22-23` $\longrightarrow$ Test out-of-sample on **`2023-24`** (380 matches)
* **Fold 2**: Train on `20-21`, `21-22`, `22-23`, `23-24` $\longrightarrow$ Test out-of-sample on **`2024-25`** (380 matches)
* **Fold 3**: Train on `21-22`, `22-23`, `23-24`, `24-25` $\longrightarrow$ Test out-of-sample on **`2025-26`** (380 matches)

### 5.2 Dynamic Reference Team Rule
Per-fold training strictly follows the identifiability rule established in Phase 1:
$$\text{reference\_team} = \operatorname{argmax}_{t} \left( \text{match\_count}(t) \text{ in the training window} \right), \quad \alpha_{\text{ref}} = 1.0$$
Zero hardcoded team names are permitted, preserving full portability across leagues and temporal eras.

### 5.3 Intra-Season Gameweek Refitting
Within each test season:
1. For Gameweek $g \in \{1, \dots, 38\}$:
   * Training data is filtered to: $\text{Date} < \min(\text{fixture\_dates in GW } g)$.
   * The oldest matches are dropped to maintain the rolling $1,520$-match window.
   * Model fits in $\approx 700$ ms.
   * Predictions $\mathbf{p}_i$ are generated for all fixtures in GW $g$.
2. Strict chronological cutoffs prevent look-ahead bias and cross-gameweek leakage.

### 5.4 Benchmark Baselines
Predictions from the model under test are evaluated against 4 parallel baselines:
1. **Naive Uniform**: $\mathbf{p} = [0.3333, 0.3333, 0.3333]$.
2. **Empirical Historical Prior**: $\mathbf{p} = [\bar{y}_H, \bar{y}_D, \bar{y}_A]$ computed strictly from the active training slice.
3. **Market Consensus Implied Probabilities**: Overround-free probabilities from market average odds (`AvgH`, `AvgD`, `AvgA`).
4. **Retail Benchmark Implied Probabilities**: Overround-free probabilities from Bet365 closing odds (`B365H`, `B365D`, `B365A`).

---

## 6. Financial Backtesting & Betting Simulation (`ml/evaluation/backtest.py`)

### 6.1 Expected-Value Edge Formula
For match $i$ and outcome $c \in \{H, D, A\}$:
$$\text{EV}_{i, c} = (p_{i, c} \times o_{i, c}) - 1$$
where $o_{i, c}$ is the closing decimal odds.

* **Bet Selection Rule**:
  * A wager is triggered if and only if $\text{EV}_{i, c} \ge \delta$ (default $\delta = 0.05$).
  * **Single-Outcome Conflict Guard**: If multiple outcomes on the same fixture clear the threshold, only the single outcome with $\max(\text{EV}_{i, c})$ is selected.

### 6.2 Pre-Gameweek Bankroll Sizing (Zero Intra-Gameweek Look-Ahead)
To reflect real-world execution where gameweek fixtures kick off across staggered windows:
* All wagers in Gameweek $g$ are sized simultaneously based on the bankroll at the start of that gameweek ($B_g$).
* **Gameweek Exposure Cap**: Total capital committed across all bets in gameweek $g$ cannot exceed $0.25 \times B_g$. If $\sum \text{stake} > 0.25 B_g$, all stakes in GW $g$ are scaled down proportionally.
* Results settle as a batch at the conclusion of Gameweek $g$:
  $$B_{g+1} = B_g + \sum_{i \in g} \text{PnL}_i$$

### 6.3 Staking Models
1. **Flat Staking**:
   $$\text{stake}_{i, c} = 1.0 \text{ unit}$$
2. **Quarter-Kelly Staking**:
   Full Kelly fraction:
   $$f^*_{i, c} = \frac{\text{EV}_{i, c}}{o_{i, c} - 1}$$
   Quarter-Kelly stake with dynamic bankroll ($B_0 = 100$ units):
   $$\text{stake}_{i, c} = \min\left( 0.25 \times f^*_{i, c} \times B_g, \ 0.05 \times B_g \right)$$
   *(5% single-bet cap guards against tail risk).*

### 6.4 Financial Metrics
* **Total Bets ($N$) & Bet Frequency (%)**: Volume of wagers placed.
* **Turnover**: $\sum \text{stake}$.
* **Net PnL**: Total profit/loss in units.
* **ROI (Yield %)**: $\frac{\text{Net PnL}}{\text{Turnover}} \times 100\%$.
* **Win Rate (%)**: Winning bets / Total bets.
* **Maximum Drawdown (MDD)**:
  $$\text{MDD} = \max_g \left( \max_{s \le g}(B_s) - B_g \right)$$
  *(reported in units and % of peak).*
* **Annualized Gameweek Sharpe Ratio** (zero risk-free rate $R_f = 0$):
  $$R_g = \frac{\sum_{i \in g} \text{PnL}_i}{B_g}, \qquad \text{Sharpe}_{\text{annual}} = \frac{\bar{R}_g}{s_{R_g}} \times \sqrt{38}$$
  *(Weeks with no bets have $R_g = 0$.)*
* **Per-Bet Trade Sharpe**: $\text{Sharpe}_{\text{bet}} = \frac{\bar{r}_{\text{bet}}}{s_{r_{\text{bet}}}}$ where $r_{\text{bet}} = \frac{\text{PnL}}{\text{stake}}$.

---

## 7. Calibration & Reporting (`ml/evaluation/calibration.py`, `ml/evaluation/report.py`)

### 7.1 Calibration Error & Reliability Tables
For each outcome $c \in \{H, D, A\}$, probabilities are partitioned into $M = 10$ uniform bins $B_m = (\frac{m-1}{10}, \frac{m}{10}]$:
$$\text{ECE}_c = \sum_{m=1}^{10} \frac{|B_m|}{N} |\text{acc}(B_m) - \text{conf}(B_m)|, \qquad \text{ECE}_{\text{overall}} = \frac{1}{3}(\text{ECE}_H + \text{ECE}_D + \text{ECE}_A)$$
$$\text{MCE}_c = \max_{m} |\text{acc}(B_m) - \text{conf}(B_m)|$$

### 7.2 Structured Report Container (`EvaluationReport`)
* Container holding `folds: list[FoldResult]`, `aggregate_metrics: dict`, `significance: dict`, `backtest: dict`, and `calibration: dict`.
* Export methods:
  * `.to_markdown() -> str`: Full GitHub-flavored markdown scorecard.
  * `.to_dict() -> dict`: Flat key-value dictionary ready for MLflow logging in Phase 2B.
  * `.print_summary()`: Rich terminal summary table.

---

## 8. CLI Interface (`scripts/evaluate.py`)

```bash
uv run python scripts/evaluate.py \
  --model dixon_coles \
  --edge 0.05 \
  --output reports/baseline_evaluation.md
```
* **Workflow**:
  1. Checks for raw seasons `1920` to `2526`. Auto-downloads `1920`, `2021`, `2122` if missing.
  2. Runs 3-fold rolling walk-forward CV ($W = 1,520$ matches, $N = 1,140$ evaluated matches).
  3. Computes RPS, Brier, LogLoss, Accuracy, and ECE for Dixon-Coles and all 4 baselines.
  4. Runs per-fold Wilcoxon and McNemar tests.
  5. Runs Flat and Quarter-Kelly backtests on Market Average and Bet365 odds.
  6. Emits console summary and writes markdown report to disk.

---

## 9. Verification & Testing Strategy

1. **Unit Tests**:
   * `test_metrics.py`: Known-value tests for RPS (including worst-case 1.0, perfect-case 0.0), Brier, Log-Loss, and Accuracy.
   * `test_significance.py`: Synthetic contingency tables validating continuity correction and exact binomial cutoff; synthetic paired series validating Pratt tie retention.
   * `test_calibration.py`: Known probability distributions verifying ECE and MCE computation.
   * `test_backtest.py`: Deterministic test matches verifying Kelly fraction math, single-outcome conflict guard, pre-gameweek batch sizing, and drawdown tracking.
2. **Integration Tests**:
   * `test_walk_forward.py`: Synthetic 4-season dataset validating rolling window maintenance, zero look-ahead leakage, and proper baseline execution.
3. **Pre-flight Quality Gates**:
   * `uv run ruff check .` $\longrightarrow$ 0 errors.
   * `uv run mypy backend/ ml/` $\longrightarrow$ 0 errors.
   * `uv run pytest` $\longrightarrow$ 100% pass on all new tests.
