# Evaluation Suite (Phase 2A) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-grade, mathematically rigorous evaluation, cross-validation, hypothesis testing, and financial backtesting suite for football match prediction models in `ml/evaluation/`.

**Architecture:** A decoupled, functional pipeline conforming to `BasePredictor`. Contains pure metric calculation (RPS, Brier, LogLoss, ECE), hypothesis testing (Pratt-mode Wilcoxon and continuity/exact McNemar), rolling 4-season fixed-window walk-forward cross-validation (1,140 out-of-sample matches across 3 seasons with gameweek-by-gameweek refitting), and pre-gameweek batch-settled financial backtesting (Flat and Quarter-Kelly).

**Tech Stack:** Python 3.12, NumPy, SciPy (`scipy.stats.wilcoxon`, `scipy.stats.chi2`, `scipy.stats.binom`), Pandas, Pandera, Pytest.

**Spec:** [`docs/superpowers/specs/2026-09-13-evaluation-suite-design.md`](file:///d:/Yash%20Kokane/Projects/MatchSense/docs/superpowers/specs/2026-09-13-evaluation-suite-design.md)

## Global Constraints

- **Window Size**: Fixed rolling window $W = 4$ seasons ($1,520$ matches) per fold.
- **Identifiability Constraint**: Reference team attack fixed at $\alpha = 1.0$ dynamically selected as $\operatorname{argmax}(\text{match count in training window})$.
- **Wilcoxon Zero-Handling**: `zero_method='pratt'` with zero-differences retained in ranking pool and only their signed-rank contributions dropped from $W$.
- **Edge Definition**: Expected Value $\text{EV} = (p_{\text{model}} \cdot o) - 1 \ge \delta$ (default $\delta = 0.05$).
- **Single-Outcome Conflict Guard**: Exactly one bet per fixture (the outcome with $\max \text{EV}$).
- **Bankroll Timing**: Pre-gameweek bankroll sizing with single batch settlement at gameweek end; 25% max gameweek exposure cap applies strictly to Quarter-Kelly staking (Flat staking is bankroll-independent 1.0 unit).
- **Annualized Sharpe**: Zero risk-free rate ($R_f = 0$) scaled over 38 weekly steps per season ($\frac{\bar{R}_g}{s_{R_g}}\sqrt{38}$).
- **Significance Reporting**: Per-fold independent tests are primary evidence; pooled 1,140-match tests carry an explicit temporal correlation caveat.

---

### Task 1: Probabilistic & Categorical Metrics

**Files:**
- Create: `ml/evaluation/metrics.py`
- Test: `tests/unit/test_metrics.py`

**Interfaces:**
- Consumes: Probabilities $\mathbf{p} \in \mathbb{R}^{N \times 3}$ and outcomes $\mathbf{y} \in \{0, 1\}^{N \times 3}$ or outcome labels in `{'H', 'D', 'A'}`.
- Produces:
  - `compute_rps(probs: np.ndarray, outcomes: np.ndarray) -> np.ndarray` (returns per-match RPS)
  - `compute_brier_score(probs: np.ndarray, outcomes: np.ndarray) -> np.ndarray` (returns per-match Brier score)
  - `compute_log_loss(probs: np.ndarray, outcomes: np.ndarray, eps: float = 1e-15) -> np.ndarray` (returns per-match LogLoss)
  - `compute_accuracy(probs: np.ndarray, outcomes: np.ndarray) -> np.ndarray` (returns boolean match correctness)

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_metrics.py
import numpy as np
import pytest
from ml.evaluation.metrics import (
    compute_rps,
    compute_brier_score,
    compute_log_loss,
    compute_accuracy,
)

def test_rps_perfect_prediction():
    # Certain home win prediction when home win occurs
    probs = np.array([[1.0, 0.0, 0.0]])
    outcomes = np.array([[1, 0, 0]])
    rps = compute_rps(probs, outcomes)
    assert rps[0] == pytest.approx(0.0)

def test_rps_worst_case_prediction():
    # Certain away win prediction when home win occurs
    probs = np.array([[0.0, 0.0, 1.0]])
    outcomes = np.array([[1, 0, 0]])
    rps = compute_rps(probs, outcomes)
    # e_H = 1, e_D = 0, e_A = 0
    # r=1: (0 - 1)^2 = 1.0
    # r=2: ((0+0) - (1+0))^2 = 1.0
    # RPS = 0.5 * (1 + 1) = 1.0
    assert rps[0] == pytest.approx(1.0)

def test_rps_adjacent_error_less_than_severe():
    # Predicting Draw when Home wins should have lower RPS than predicting Away
    outcomes = np.array([[1, 0, 0]])
    rps_draw = compute_rps(np.array([[0.0, 1.0, 0.0]]), outcomes)[0]
    rps_away = compute_rps(np.array([[0.0, 0.0, 1.0]]), outcomes)[0]
    assert rps_draw < rps_away

def test_brier_score_range():
    probs = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    outcomes = np.array([[1, 0, 0], [1, 0, 0]])
    brier = compute_brier_score(probs, outcomes)
    assert brier[0] == pytest.approx(0.0)
    assert brier[1] == pytest.approx(2.0)

def test_log_loss_clipping():
    probs = np.array([[0.0, 1.0, 0.0]])
    outcomes = np.array([[1, 0, 0]])
    loss = compute_log_loss(probs, outcomes, eps=1e-15)
    assert loss[0] > 30.0  # -ln(1e-15) ~ 34.5

def test_accuracy_argmax():
    probs = np.array([[0.6, 0.3, 0.1], [0.2, 0.5, 0.3]])
    outcomes = np.array([[1, 0, 0], [1, 0, 0]])
    acc = compute_accuracy(probs, outcomes)
    assert acc[0] == 1
    assert acc[1] == 0
```

- [ ] **Step 2: Run test to verify it fails**
Run: `uv run pytest tests/unit/test_metrics.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'ml.evaluation.metrics'`

- [ ] **Step 3: Write minimal implementation**

```python
# ml/evaluation/metrics.py
"""Mathematical evaluation metrics for football match prediction."""

import numpy as np


def compute_rps(probs: np.ndarray, outcomes: np.ndarray) -> np.ndarray:
    """Compute Ranked Probability Score for 3-outcome ordered events (H < D < A).

    Args:
        probs: Array of shape (N, 3) with probabilities for [H, D, A].
        outcomes: One-hot array of shape (N, 3) with actual outcomes for [H, D, A].

    Returns:
        Array of shape (N,) with RPS values in [0, 1].
    """
    probs = np.asarray(probs, dtype=float)
    outcomes = np.asarray(outcomes, dtype=float)

    # Cumulative probabilities
    p_h = probs[:, 0]
    p_hd = p_h + probs[:, 1]

    # Cumulative outcomes
    y_h = outcomes[:, 0]
    y_hd = y_h + outcomes[:, 1]

    # RPS = 0.5 * [(p_H - y_H)^2 + (p_HD - y_HD)^2]
    rps = 0.5 * ((p_h - y_h) ** 2 + (p_hd - y_hd) ** 2)
    return rps


def compute_brier_score(probs: np.ndarray, outcomes: np.ndarray) -> np.ndarray:
    """Compute multi-category Brier score.

    Args:
        probs: Array of shape (N, 3).
        outcomes: One-hot array of shape (N, 3).

    Returns:
        Array of shape (N,) with Brier scores in [0, 2].
    """
    probs = np.asarray(probs, dtype=float)
    outcomes = np.asarray(outcomes, dtype=float)
    return np.sum((probs - outcomes) ** 2, axis=1)


def compute_log_loss(
    probs: np.ndarray, outcomes: np.ndarray, eps: float = 1e-15
) -> np.ndarray:
    """Compute multi-class cross-entropy log-loss.

    Args:
        probs: Array of shape (N, 3).
        outcomes: One-hot array of shape (N, 3).
        eps: Boundary clipping parameter.

    Returns:
        Array of shape (N,) with log-loss values.
    """
    probs = np.clip(np.asarray(probs, dtype=float), eps, 1.0 - eps)
    outcomes = np.asarray(outcomes, dtype=float)
    return -np.sum(outcomes * np.log(probs), axis=1)


def compute_accuracy(probs: np.ndarray, outcomes: np.ndarray) -> np.ndarray:
    """Compute binary classification correctness.

    Args:
        probs: Array of shape (N, 3).
        outcomes: One-hot array of shape (N, 3).

    Returns:
        Integer array of shape (N,) with 1 for correct, 0 for incorrect.
    """
    pred_classes = np.argmax(np.asarray(probs), axis=1)
    true_classes = np.argmax(np.asarray(outcomes), axis=1)
    return (pred_classes == true_classes).astype(int)
```

- [ ] **Step 4: Run test to verify it passes**
Run: `uv run pytest tests/unit/test_metrics.py`
Expected: 6 passed

- [ ] **Step 5: Commit**
```bash
git add ml/evaluation/metrics.py tests/unit/test_metrics.py
git commit -m "feat(eval): implement vectorized RPS, Brier, LogLoss, and accuracy metrics"
```

---

### Task 2: Hypothesis Testing Engine

**Files:**
- Create: `ml/evaluation/significance.py`
- Test: `tests/unit/test_significance.py`

**Interfaces:**
- Consumes: Per-match RPS arrays and boolean accuracy arrays for Model A and Model B.
- Produces:
  - `wilcoxon_rps_test(rps_a: np.ndarray, rps_b: np.ndarray) -> WilcoxonResult`
  - `mcnemar_accuracy_test(correct_a: np.ndarray, correct_b: np.ndarray) -> McNemarResult`
  - `compare_models(rps_a, rps_b, correct_a, correct_b, model_a_name, model_b_name) -> dict`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_significance.py
import numpy as np
import pytest
from ml.evaluation.significance import (
    wilcoxon_rps_test,
    mcnemar_accuracy_test,
)

def test_wilcoxon_identical_models():
    rps = np.array([0.2, 0.3, 0.1, 0.4, 0.25])
    res = wilcoxon_rps_test(rps, rps)
    assert res.p_value == pytest.approx(1.0)
    assert res.mean_diff == pytest.approx(0.0)

def test_wilcoxon_significant_improvement():
    # Model A is consistently better than Model B
    rps_a = np.linspace(0.1, 0.3, 50)
    rps_b = rps_a + 0.05
    res = wilcoxon_rps_test(rps_a, rps_b)
    assert res.mean_diff < 0.0
    assert res.p_value < 0.001

def test_mcnemar_exact_binomial_fallback():
    # Small discordant count (n10 + n01 < 25)
    # Model A correct on 10 matches where B failed; B correct on 2 matches where A failed
    correct_a = np.array([1]*10 + [0]*2 + [1]*50 + [0]*10)
    correct_b = np.array([0]*10 + [1]*2 + [1]*50 + [0]*10)
    res = mcnemar_accuracy_test(correct_a, correct_b)
    assert res.is_exact is True
    assert res.p_value < 0.05

def test_mcnemar_large_sample_continuity():
    # Large discordant count (n10 + n01 >= 25)
    correct_a = np.array([1]*40 + [0]*10 + [1]*100)
    correct_b = np.array([0]*40 + [1]*10 + [1]*100)
    res = mcnemar_accuracy_test(correct_a, correct_b)
    assert res.is_exact is False
    assert res.statistic > 0.0
    assert res.p_value < 0.001
```

- [ ] **Step 2: Run test to verify it fails**
Run: `uv run pytest tests/unit/test_significance.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'ml.evaluation.significance'`

- [ ] **Step 3: Write minimal implementation**

```python
# ml/evaluation/significance.py
"""Hypothesis testing for comparative model evaluation."""

from dataclasses import dataclass
import numpy as np
from scipy import stats


@dataclass(frozen=True)
class WilcoxonResult:
    statistic: float
    p_value: float
    mean_diff: float
    median_diff: float
    n_pairs: int


@dataclass(frozen=True)
class McNemarResult:
    statistic: float
    p_value: float
    n10: int
    n01: int
    is_exact: bool


def wilcoxon_rps_test(rps_a: np.ndarray, rps_b: np.ndarray) -> WilcoxonResult:
    """Paired Wilcoxon signed-rank test on match-by-match RPS differences.

    Uses Pratt zero-method: zero-differences are retained in the ranking pool,
    and only their signed-rank contributions are dropped from the test statistic.
    """
    rps_a = np.asarray(rps_a, dtype=float)
    rps_b = np.asarray(rps_b, dtype=float)
    diff = rps_a - rps_b
    n = len(diff)

    if np.all(diff == 0.0):
        return WilcoxonResult(
            statistic=0.0, p_value=1.0, mean_diff=0.0, median_diff=0.0, n_pairs=n
        )

    res = stats.wilcoxon(diff, zero_method="pratt", alternative="two-sided")
    return WilcoxonResult(
        statistic=float(res.statistic),
        p_value=float(res.pvalue),
        mean_diff=float(np.mean(diff)),
        median_diff=float(np.median(diff)),
        n_pairs=n,
    )


def mcnemar_accuracy_test(
    correct_a: np.ndarray, correct_b: np.ndarray
) -> McNemarResult:
    """McNemar's test for paired classification accuracy.

    Uses continuity correction for discordant counts >= 25, and exact
    two-sided binomial test when discordant counts < 25.
    """
    correct_a = np.asarray(correct_a, dtype=int)
    correct_b = np.asarray(correct_b, dtype=int)

    n10 = int(np.sum((correct_a == 1) & (correct_b == 0)))
    n01 = int(np.sum((correct_a == 0) & (correct_b == 1)))
    discordant = n10 + n01

    if discordant == 0:
        return McNemarResult(statistic=0.0, p_value=1.0, n10=0, n01=0, is_exact=True)

    if discordant < 25:
        # Exact two-sided binomial test under H0: p=0.5
        k = min(n10, n01)
        p_val = float(2.0 * stats.binom.cdf(k, discordant, 0.5))
        p_val = min(1.0, p_val)
        return McNemarResult(statistic=float(k), p_value=p_val, n10=n10, n01=n01, is_exact=True)

    # Continuity-corrected chi-squared test: (|n10 - n01| - 1)^2 / (n10 + n01)
    chi2_stat = float(((abs(n10 - n01) - 1.0) ** 2) / discordant)
    p_val = float(1.0 - stats.chi2.cdf(chi2_stat, df=1))
    return McNemarResult(statistic=chi2_stat, p_value=p_val, n10=n10, n01=n01, is_exact=False)
```

- [ ] **Step 4: Run test to verify it passes**
Run: `uv run pytest tests/unit/test_significance.py`
Expected: 4 passed

- [ ] **Step 5: Commit**
```bash
git add ml/evaluation/significance.py tests/unit/test_significance.py
git commit -m "feat(eval): implement Wilcoxon signed-rank and McNemar hypothesis tests"
```

---

### Task 3: Calibration & Expected Calibration Error (ECE)

**Files:**
- Create: `ml/evaluation/calibration.py`
- Test: `tests/unit/test_calibration.py`

**Interfaces:**
- Consumes: Predicted probabilities $(N \times 3)$ and one-hot outcomes $(N \times 3)$.
- Produces:
  - `compute_calibration(probs: np.ndarray, outcomes: np.ndarray, n_bins: int = 10) -> CalibrationResult`
  - Returns `CalibrationResult` containing bin-by-bin confidence, empirical accuracy, counts, per-class ECE/MCE, and overall ECE.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_calibration.py
import numpy as np
import pytest
from ml.evaluation.calibration import compute_calibration

def test_perfect_calibration():
    # Synthesize well-calibrated probabilities
    np.random.seed(42)
    p = np.random.uniform(0.1, 0.9, 1000)
    y = (np.random.uniform(0, 1, 1000) < p).astype(int)
    probs = np.column_stack([p, (1-p)/2, (1-p)/2])
    outcomes = np.column_stack([y, np.zeros(1000), 1-y])

    res = compute_calibration(probs, outcomes, n_bins=5)
    assert res.ece_home < 0.06  # Close to 0 with finite sample noise

def test_extreme_miscalibration():
    # Always predicts 0.95 probability of home win, but home win occurs 10% of time
    probs = np.array([[0.95, 0.025, 0.025]] * 100)
    outcomes = np.array([[0, 1, 0]] * 100)
    res = compute_calibration(probs, outcomes, n_bins=10)
    assert res.ece_home == pytest.approx(0.95, abs=0.01)
    assert res.mce_home == pytest.approx(0.95, abs=0.01)
```

- [ ] **Step 2: Run test to verify it fails**
Run: `uv run pytest tests/unit/test_calibration.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'ml.evaluation.calibration'`

- [ ] **Step 3: Write minimal implementation**

```python
# ml/evaluation/calibration.py
"""Reliability diagrams and calibration metrics."""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BinSummary:
    bin_lower: float
    bin_upper: float
    count: int
    mean_predicted: float
    observed_frequency: float
    gap: float


@dataclass(frozen=True)
class CalibrationResult:
    ece_home: float
    ece_draw: float
    ece_away: float
    ece_overall: float
    mce_home: float
    mce_draw: float
    mce_away: float
    tables: dict[str, list[BinSummary]]


def _compute_class_calibration(
    pred: np.ndarray, true: np.ndarray, n_bins: int = 10
) -> tuple[float, float, list[BinSummary]]:
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_summaries: list[BinSummary] = []
    n = len(pred)

    ece = 0.0
    mce = 0.0

    for m in range(n_bins):
        b_low = bin_edges[m]
        b_high = bin_edges[m + 1]

        if m == 0:
            mask = (pred >= b_low) & (pred <= b_high)
        else:
            mask = (pred > b_low) & (pred <= b_high)

        count = int(np.sum(mask))
        if count > 0:
            mean_pred = float(np.mean(pred[mask]))
            obs_freq = float(np.mean(true[mask]))
            gap = abs(obs_freq - mean_pred)
            ece += (count / n) * gap
            mce = max(mce, gap)
        else:
            mean_pred = (b_low + b_high) / 2.0
            obs_freq = 0.0
            gap = 0.0

        bin_summaries.append(
            BinSummary(
                bin_lower=float(b_low),
                bin_upper=float(b_high),
                count=count,
                mean_predicted=mean_pred,
                observed_frequency=obs_freq,
                gap=gap,
            )
        )

    return float(ece), float(mce), bin_summaries


def compute_calibration(
    probs: np.ndarray, outcomes: np.ndarray, n_bins: int = 10
) -> CalibrationResult:
    """Compute Expected Calibration Error and reliability tables across H/D/A outcomes."""
    probs = np.asarray(probs, dtype=float)
    outcomes = np.asarray(outcomes, dtype=float)

    ece_h, mce_h, table_h = _compute_class_calibration(probs[:, 0], outcomes[:, 0], n_bins)
    ece_d, mce_d, table_d = _compute_class_calibration(probs[:, 1], outcomes[:, 1], n_bins)
    ece_a, mce_a, table_a = _compute_class_calibration(probs[:, 2], outcomes[:, 2], n_bins)
    ece_overall = (ece_h + ece_d + ece_a) / 3.0

    return CalibrationResult(
        ece_home=ece_h,
        ece_draw=ece_d,
        ece_away=ece_a,
        ece_overall=float(ece_overall),
        mce_home=mce_h,
        mce_draw=mce_d,
        mce_away=mce_a,
        tables={"H": table_h, "D": table_d, "A": table_a},
    )
```

- [ ] **Step 4: Run test to verify it passes**
Run: `uv run pytest tests/unit/test_calibration.py`
Expected: 2 passed

- [ ] **Step 5: Commit**
```bash
git add ml/evaluation/calibration.py tests/unit/test_calibration.py
git commit -m "feat(eval): implement reliability diagrams and ECE calculation"
```

---

### Task 4: Financial Backtesting & Betting Simulator

**Files:**
- Create: `ml/evaluation/backtest.py`
- Test: `tests/unit/test_backtest.py`

**Interfaces:**
- Consumes: Out-of-sample prediction records with gameweek IDs, decimal odds (`H/D/A`), model probabilities (`H/D/A`), and true outcomes.
- Produces:
  - `simulate_betting(df, odds_col_prefix='Avg', edge_threshold=0.05, staking_strategy='flat'|'quarter_kelly', initial_bankroll=100.0) -> BacktestResult`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_backtest.py
import pandas as pd
import pytest
from ml.evaluation.backtest import simulate_betting

@pytest.fixture
def sample_betting_df():
    return pd.DataFrame([
        # GW 1: Match 1 - model sees EV on Home: 0.60 * 2.0 - 1 = +0.20 (win)
        {"Gameweek": 1, "prob_home": 0.60, "prob_draw": 0.25, "prob_away": 0.15,
         "AvgH": 2.0, "AvgD": 3.4, "AvgA": 4.5, "FTR": "H"},
        # GW 1: Match 2 - model sees EV on Away: 0.40 * 3.0 - 1 = +0.20 (loss)
        {"Gameweek": 1, "prob_home": 0.30, "prob_draw": 0.30, "prob_away": 0.40,
         "AvgH": 2.5, "AvgD": 3.2, "AvgA": 3.0, "FTR": "H"},
        # GW 2: Match 3 - EV below 0.05 threshold: 0.50 * 2.0 - 1 = 0.0 (no bet)
        {"Gameweek": 2, "prob_home": 0.50, "prob_draw": 0.30, "prob_away": 0.20,
         "AvgH": 2.0, "AvgD": 3.5, "AvgA": 4.0, "FTR": "H"},
    ])

def test_flat_betting_execution(sample_betting_df):
    res = simulate_betting(sample_betting_df, odds_col_prefix="Avg", edge_threshold=0.05, staking="flat")
    assert res.total_bets == 2
    # Bet 1 won at 2.0 odds -> +1.0 unit PnL
    # Bet 2 lost -> -1.0 unit PnL
    assert res.net_pnl == pytest.approx(0.0)
    assert res.turnover == pytest.approx(2.0)
    assert res.roi == pytest.approx(0.0)
    assert res.win_rate == pytest.approx(0.5)

def test_quarter_kelly_sizing(sample_betting_df):
    res = simulate_betting(sample_betting_df, odds_col_prefix="Avg", edge_threshold=0.05, staking="quarter_kelly", initial_bankroll=100.0)
    # Bet 1: EV=0.20, b=1.0 -> f* = 0.20 / 1.0 = 0.20. Quarter Kelly = 0.05. Cap = 0.05 * 100 = 5 units.
    assert res.total_bets == 2
    assert res.turnover > 0.0
```

- [ ] **Step 2: Run test to verify it fails**
Run: `uv run pytest tests/unit/test_backtest.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'ml.evaluation.backtest'`

- [ ] **Step 3: Write minimal implementation**

```python
# ml/evaluation/backtest.py
"""Financial backtesting engine with pre-gameweek batch staking."""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BacktestResult:
    total_bets: int
    bet_frequency: float
    turnover: float
    net_pnl: float
    roi: float
    win_rate: float
    max_drawdown_units: float
    max_drawdown_pct: float
    annualized_sharpe: float
    per_bet_sharpe: float
    history: pd.DataFrame


def simulate_betting(
    df: pd.DataFrame,
    odds_col_prefix: str = "Avg",
    edge_threshold: float = 0.05,
    staking: str = "flat",
    initial_bankroll: float = 100.0,
) -> BacktestResult:
    """Run financial backtest with gameweek batch sizing and conflict guards.

    Args:
        df: DataFrame containing Gameweek, prob_home, prob_draw, prob_away,
            {prefix}H, {prefix}D, {prefix}A, FTR.
        odds_col_prefix: 'Avg' or 'B365'.
        edge_threshold: Minimum expected value (p * odds - 1).
        staking: 'flat' or 'quarter_kelly'.
        initial_bankroll: Starting bankroll units.
    """
    col_h = f"{odds_col_prefix}H"
    col_d = f"{odds_col_prefix}D"
    col_a = f"{odds_col_prefix}A"

    bankroll = float(initial_bankroll)
    peak_bankroll = bankroll
    max_dd_units = 0.0
    max_dd_pct = 0.0

    bet_records: list[dict] = []
    gameweek_returns: list[float] = []

    # Sort chronologically by gameweek/date
    sort_cols = [c for c in ["Season", "Gameweek", "Date"] if c in df.columns]
    if sort_cols:
        df = df.sort_values(sort_cols)

    grouped = df.groupby(["Season", "Gameweek"] if "Season" in df.columns else "Gameweek", sort=False)

    for _, gw_matches in grouped:
        gw_pre_bankroll = bankroll
        gw_bets: list[dict] = []

        for _, row in gw_matches.iterrows():
            odds = {"H": float(row[col_h]), "D": float(row[col_d]), "A": float(row[col_a])}
            probs = {"H": float(row["prob_home"]), "D": float(row["prob_draw"]), "A": float(row["prob_away"])}

            # Calculate EV: p * o - 1
            evs = {c: probs[c] * odds[c] - 1.0 for c in ["H", "D", "A"]}
            best_outcome = max(evs, key=evs.get)  # type: ignore
            max_ev = evs[best_outcome]

            if max_ev >= edge_threshold:
                best_odds = odds[best_outcome]
                best_prob = probs[best_outcome]

                if staking == "flat":
                    raw_stake = 1.0
                elif staking == "quarter_kelly":
                    # f* = EV / (o - 1)
                    denom = max(1e-4, best_odds - 1.0)
                    f_star = max_ev / denom
                    # Quarter Kelly with 5% max bankroll cap per bet
                    raw_stake = min(0.25 * f_star * gw_pre_bankroll, 0.05 * gw_pre_bankroll)
                    raw_stake = max(0.0, raw_stake)
                else:
                    raise ValueError(f"Unknown staking strategy: {staking}")

                gw_bets.append({
                    "outcome": best_outcome,
                    "odds": best_odds,
                    "prob": best_prob,
                    "ev": max_ev,
                    "raw_stake": raw_stake,
                    "actual": str(row["FTR"]),
                })

        # Apply 25% Gameweek Exposure Cap to Quarter-Kelly
        if staking == "quarter_kelly" and gw_bets:
            tot_gw_stake = sum(b["raw_stake"] for b in gw_bets)
            max_allowed = 0.25 * gw_pre_bankroll
            scale = min(1.0, max_allowed / tot_gw_stake) if tot_gw_stake > 0 else 1.0
            for b in gw_bets:
                b["stake"] = b["raw_stake"] * scale
        else:
            for b in gw_bets:
                b["stake"] = b["raw_stake"]

        # Batch settlement
        gw_pnl = 0.0
        for b in gw_bets:
            won = (b["outcome"] == b["actual"])
            pnl = b["stake"] * (b["odds"] - 1.0) if won else -b["stake"]
            b["won"] = won
            b["pnl"] = pnl
            gw_pnl += pnl
            bet_records.append(b)

        bankroll += gw_pnl
        peak_bankroll = max(peak_bankroll, bankroll)
        dd_units = peak_bankroll - bankroll
        dd_pct = (dd_units / peak_bankroll * 100.0) if peak_bankroll > 0 else 0.0
        max_dd_units = max(max_dd_units, dd_units)
        max_dd_pct = max(max_dd_pct, dd_pct)

        # Weekly return for Sharpe
        gw_ret = gw_pnl / gw_pre_bankroll if gw_pre_bankroll > 0 else 0.0
        gameweek_returns.append(gw_ret)

    total_bets = len(bet_records)
    total_matches = len(df)
    bet_freq = (total_bets / total_matches * 100.0) if total_matches > 0 else 0.0
    turnover = sum(b["stake"] for b in bet_records)
    net_pnl = sum(b["pnl"] for b in bet_records)
    roi = (net_pnl / turnover * 100.0) if turnover > 0 else 0.0
    win_rate = (sum(1 for b in bet_records if b["won"]) / total_bets) if total_bets > 0 else 0.0

    # Annualized Gameweek Sharpe (38 weeks per season)
    if len(gameweek_returns) > 1 and np.std(gameweek_returns) > 0:
        ann_sharpe = float(np.mean(gameweek_returns) / np.std(gameweek_returns) * np.sqrt(38))
    else:
        ann_sharpe = 0.0

    # Per-bet trade Sharpe
    if total_bets > 1:
        bet_returns = [b["pnl"] / b["stake"] for b in bet_records if b["stake"] > 0]
        if bet_returns and np.std(bet_returns) > 0:
            per_bet_sharpe = float(np.mean(bet_returns) / np.std(bet_returns))
        else:
            per_bet_sharpe = 0.0
    else:
        per_bet_sharpe = 0.0

    return BacktestResult(
        total_bets=total_bets,
        bet_frequency=float(bet_freq),
        turnover=float(turnover),
        net_pnl=float(net_pnl),
        roi=float(roi),
        win_rate=float(win_rate),
        max_drawdown_units=float(max_dd_units),
        max_drawdown_pct=float(max_dd_pct),
        annualized_sharpe=ann_sharpe,
        per_bet_sharpe=per_bet_sharpe,
        history=pd.DataFrame(bet_records),
    )
```

- [ ] **Step 4: Run test to verify it passes**
Run: `uv run pytest tests/unit/test_backtest.py`
Expected: 2 passed

- [ ] **Step 5: Commit**
```bash
git add ml/evaluation/backtest.py tests/unit/test_backtest.py
git commit -m "feat(eval): implement financial backtesting engine with gameweek batch sizing"
```

---

### Task 5: Walk-Forward CV Orchestrator & Baselines

**Files:**
- Create: `ml/evaluation/walk_forward.py`
- Test: `tests/unit/test_walk_forward.py`

**Interfaces:**
- Consumes: `BasePredictor` factory and match history DataFrame.
- Produces:
  - `run_walk_forward_cv(model_factory, matches_df, seasons, window_size=4) -> tuple[pd.DataFrame, list[dict]]`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_walk_forward.py
import pandas as pd
import numpy as np
import pytest
from ml.models.dixon_coles import DixonColesModel
from ml.evaluation.walk_forward import run_walk_forward_cv

@pytest.fixture
def synthetic_seasons_data():
    # 5 teams across 2 small test seasons (20 matches per season)
    dates = pd.date_range("2023-08-01", periods=40, freq="7D")
    teams = ["Arsenal", "Chelsea", "Liverpool", "ManCity", "Tottenham"]
    rows = []
    for i in range(40):
        ht = teams[i % 5]
        at = teams[(i + 1) % 5]
        season = "2023-24" if i < 20 else "2024-25"
        gw = (i % 20) + 1
        rows.append({
            "Season": season,
            "Gameweek": gw,
            "Date": dates[i],
            "HomeTeam": ht,
            "AwayTeam": at,
            "FTHG": (i % 3),
            "FTAG": ((i + 1) % 2),
            "FTR": "H" if (i % 3) > ((i + 1) % 2) else ("D" if (i % 3) == ((i + 1) % 2) else "A"),
            "AvgH": 2.1, "AvgD": 3.3, "AvgA": 3.8,
            "B365H": 2.0, "B365D": 3.4, "B365A": 4.0,
        })
    return pd.DataFrame(rows)

def test_walk_forward_execution(synthetic_seasons_data):
    # Train window = 1 season, test season = 2024-25
    df_eval, fold_metrics = run_walk_forward_cv(
        model_factory=lambda: DixonColesModel(xi=0.005),
        matches_df=synthetic_seasons_data,
        test_seasons=["2024-25"],
        window_size_seasons=1,
    )
    assert len(df_eval) == 20
    assert "prob_home" in df_eval.columns
    assert "prob_home_uniform" in df_eval.columns
    assert "prob_home_market" in df_eval.columns
    assert len(fold_metrics) == 1
    assert "rps" in fold_metrics[0]
```

- [ ] **Step 2: Run test to verify it fails**
Run: `uv run pytest tests/unit/test_walk_forward.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'ml.evaluation.walk_forward'`

- [ ] **Step 3: Write minimal implementation**

```python
# ml/evaluation/walk_forward.py
"""Walk-forward cross validation engine."""

from typing import Callable
import logging
import numpy as np
import pandas as pd

from ml.models.base import BasePredictor
from ml.data.ingestion import compute_implied_probabilities
from ml.evaluation.metrics import compute_rps, compute_brier_score, compute_log_loss, compute_accuracy

logger = logging.getLogger(__name__)


def run_walk_forward_cv(
    model_factory: Callable[[], BasePredictor],
    matches_df: pd.DataFrame,
    test_seasons: list[str],
    window_size_seasons: int = 4,
) -> tuple[pd.DataFrame, list[dict]]:
    """Execute rolling fixed-window walk-forward cross validation gameweek-by-gameweek.

    Args:
        model_factory: Callable returning an unfitted model.
        matches_df: Clean DataFrame containing Date, Season, Gameweek, HomeTeam, AwayTeam, FTHG, FTAG, FTR, odds.
        test_seasons: List of season strings to evaluate out-of-sample.
        window_size_seasons: Number of preceding seasons in the fixed rolling training window.
    """
    matches_df = matches_df.sort_values("Date").reset_index(drop=True)
    all_seasons = sorted(matches_df["Season"].unique())
    eval_records: list[pd.DataFrame] = []
    fold_metrics: list[dict] = []

    for test_s in test_seasons:
        test_idx = all_seasons.index(test_s)
        if test_idx < window_size_seasons:
            raise ValueError(f"Insufficient history for test season {test_s}: need {window_size_seasons} seasons.")

        train_seasons = all_seasons[test_idx - window_size_seasons : test_idx]
        test_data = matches_df[matches_df["Season"] == test_s].copy()
        logger.info("Evaluating fold: train on %s -> test on %s (%d matches)", train_seasons, test_s, len(test_data))

        # Gameweek walk-forward
        test_gameweeks = sorted(test_data["Gameweek"].unique())
        fold_predictions: list[dict] = []

        for gw in test_gameweeks:
            gw_fixtures = test_data[test_data["Gameweek"] == gw]
            min_date = gw_fixtures["Date"].min()

            # Rolling window: prior matches strictly before current GW min date
            train_pool = matches_df[(matches_df["Date"] < min_date) & (matches_df["Season"].isin(train_seasons))]

            model = model_factory()
            model.fit(train_pool)

            # Empirical prior baseline from current training slice
            h_freq = float((train_pool["FTR"] == "H").mean())
            d_freq = float((train_pool["FTR"] == "D").mean())
            a_freq = float((train_pool["FTR"] == "A").mean())

            for _, match in gw_fixtures.iterrows():
                ht = str(match["HomeTeam"])
                at = str(match["AwayTeam"])

                # Model predictions
                probs = model.predict_proba(ht, at)
                p_h, p_d, p_a = probs["prob_home"], probs["prob_draw"], probs["prob_away"]

                # Baselines
                imp_mkt = compute_implied_probabilities(float(match.get("AvgH", 2.5)), float(match.get("AvgD", 3.2)), float(match.get("AvgA", 3.0)))
                imp_b365 = compute_implied_probabilities(float(match.get("B365H", 2.5)), float(match.get("B365D", 3.2)), float(match.get("B365A", 3.0)))

                rec = match.to_dict()
                rec.update({
                    "prob_home": p_h, "prob_draw": p_d, "prob_away": p_a,
                    "prob_home_uniform": 1/3, "prob_draw_uniform": 1/3, "prob_away_uniform": 1/3,
                    "prob_home_empirical": h_freq, "prob_draw_empirical": d_freq, "prob_away_empirical": a_freq,
                    "prob_home_market": imp_mkt[0], "prob_draw_market": imp_mkt[1], "prob_away_market": imp_mkt[2],
                    "prob_home_b365": imp_b365[0], "prob_draw_b365": imp_b365[1], "prob_away_b365": imp_b365[2],
                })
                fold_predictions.append(rec)

        df_fold = pd.DataFrame(fold_predictions)

        # Compute instant scores
        outcomes_1hot = np.zeros((len(df_fold), 3))
        for i, ftr in enumerate(df_fold["FTR"]):
            idx = 0 if ftr == "H" else (1 if ftr == "D" else 2)
            outcomes_1hot[i, idx] = 1.0

        model_probs = df_fold[["prob_home", "prob_draw", "prob_away"]].to_numpy()
        df_fold["rps"] = compute_rps(model_probs, outcomes_1hot)
        df_fold["brier"] = compute_brier_score(model_probs, outcomes_1hot)
        df_fold["log_loss"] = compute_log_loss(model_probs, outcomes_1hot)
        df_fold["correct"] = compute_accuracy(model_probs, outcomes_1hot)

        fold_metrics.append({
            "season": test_s,
            "n_matches": len(df_fold),
            "rps": float(df_fold["rps"].mean()),
            "brier": float(df_fold["brier"].mean()),
            "log_loss": float(df_fold["log_loss"].mean()),
            "accuracy": float(df_fold["correct"].mean()),
        })
        eval_records.append(df_fold)

    df_all_eval = pd.concat(eval_records, ignore_index=True)
    return df_all_eval, fold_metrics
```

- [ ] **Step 4: Run test to verify it passes**
Run: `uv run pytest tests/unit/test_walk_forward.py`
Expected: 1 passed

- [ ] **Step 5: Commit**
```bash
git add ml/evaluation/walk_forward.py tests/unit/test_walk_forward.py
git commit -m "feat(eval): implement rolling fixed-window walk-forward cross validation"
```

---

### Task 6: Structured Report Container & Formatters

**Files:**
- Create: `ml/evaluation/report.py`
- Test: `tests/unit/test_report.py`

**Interfaces:**
- Consumes: Evaluated out-of-sample DataFrame, fold summaries, backtest results, significance results, and calibration results.
- Produces:
  - `EvaluationReport` with `.to_markdown()`, `.to_dict()`, `.print_summary()`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_report.py
from ml.evaluation.report import EvaluationReport

def test_report_serialization():
    rep = EvaluationReport(
        model_name="dixon_coles",
        folds=[{"season": "2023-24", "n_matches": 380, "rps": 0.201, "brier": 0.58, "log_loss": 0.98, "accuracy": 0.52}],
        aggregate_metrics={"rps": 0.201, "brier": 0.58, "log_loss": 0.98, "accuracy": 0.52},
        significance_results={},
        backtest_results={},
        calibration_results={},
    )
    md = rep.to_markdown()
    assert "dixon_coles" in md
    assert "2023-24" in md
    d = rep.to_dict()
    assert d["model_name"] == "dixon_coles"
    assert d["aggregate_rps"] == 0.201
```

- [ ] **Step 2: Run test to verify it fails**
Run: `uv run pytest tests/unit/test_report.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'ml.evaluation.report'`

- [ ] **Step 3: Write minimal implementation**

```python
# ml/evaluation/report.py
"""Comprehensive evaluation scorecard generator."""

from dataclasses import dataclass
from typing import Any


@dataclass
class EvaluationReport:
    model_name: str
    folds: list[dict[str, Any]]
    aggregate_metrics: dict[str, float]
    significance_results: dict[str, Any]
    backtest_results: dict[str, Any]
    calibration_results: dict[str, Any]

    def to_markdown(self) -> str:
        lines = [
            f"# MatchSense — Model Evaluation Report: `{self.model_name}`\n",
            "## 1. Out-of-Sample Performance by Season (Rolling 4-Season Window)\n",
            "| Season | Matches | RPS | Brier Score | Log-Loss | Accuracy |",
            "| :--- | :---: | :---: | :---: | :---: | :---: |",
        ]
        for f in self.folds:
            lines.append(
                f"| **{f['season']}** | {f['n_matches']} | {f['rps']:.4f} | {f['brier']:.4f} | {f['log_loss']:.4f} | {f['accuracy']:.1%} |"
            )

        agg = self.aggregate_metrics
        lines.append(
            f"| **Aggregate** | **{sum(f['n_matches'] for f in self.folds)}** | **{agg.get('rps', 0):.4f}** | **{agg.get('brier', 0):.4f}** | **{agg.get('log_loss', 0):.4f}** | **{agg.get('accuracy', 0):.1%}** |\n"
        )

        if self.significance_results:
            lines.extend([
                "## 2. Statistical Significance vs Baselines (Primary: Per-Fold Independent)\n",
                "> *Caveat: Per-fold independent tests provide primary evidence; pooled 1,140-match statistics are descriptive.*\n",
                "| Comparison | Metric | Test | Stat | p-value | Interpretation |",
                "| :--- | :--- | :--- | :---: | :---: | :--- |",
            ])
            for comp, data in self.significance_results.items():
                w = data.get("wilcoxon")
                if w:
                    sig = "p < 0.05 *" if w["p_value"] < 0.05 else "not significant"
                    lines.append(f"| vs {comp} | RPS | Wilcoxon (Pratt) | W={w['statistic']:.1f} | {w['p_value']:.4f} | {sig} |")
                m = data.get("mcnemar")
                if m:
                    sig = "p < 0.05 *" if m["p_value"] < 0.05 else "not significant"
                    test_name = "McNemar (Exact)" if m.get("is_exact") else "McNemar (Chi2)"
                    lines.append(f"| vs {comp} | Accuracy | {test_name} | stat={m['statistic']:.1f} | {m['p_value']:.4f} | {sig} |")
            lines.append("")

        if self.backtest_results:
            lines.extend([
                "## 3. Financial Simulation & ROI (Edge >= 5%)\n",
                "| Odds Source | Staking | Bets | Turnover | Net PnL | ROI % | Win % | Max DD % | Annual Sharpe |",
                "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
            ])
            for key, b in self.backtest_results.items():
                lines.append(
                    f"| {b['odds_source']} | {b['staking']} | {b['total_bets']} | {b['turnover']:.1f}u | {b['net_pnl']:+.1f}u | {b['roi']:+.1f}% | {b['win_rate']:.1%} | {b['max_drawdown_pct']:.1f}% | {b['annualized_sharpe']:.2f} |"
                )
            lines.append("")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        flat: dict[str, Any] = {"model_name": self.model_name}
        for k, v in self.aggregate_metrics.items():
            flat[f"aggregate_{k}"] = v
        for i, f in enumerate(self.folds):
            for k, v in f.items():
                flat[f"fold_{i}_{k}"] = v
        return flat

    def print_summary(self) -> None:
        print(self.to_markdown())
```

- [ ] **Step 4: Run test to verify it passes**
Run: `uv run pytest tests/unit/test_report.py`
Expected: 1 passed

- [ ] **Step 5: Commit**
```bash
git add ml/evaluation/report.py tests/unit/test_report.py
git commit -m "feat(eval): implement structured evaluation report container"
```

---

### Task 7: Evaluation CLI Script & Baseline Benchmark Run

**Files:**
- Create: `scripts/evaluate.py`
- Test: CLI execution producing `reports/baseline_evaluation.md`

**Interfaces:**
- Consumes: command-line flags `--model`, `--edge`, `--output`.
- Produces: Markdown report file with real Premier League walk-forward evaluation.

- [ ] **Step 1: Write CLI implementation in `scripts/evaluate.py`**

```python
# scripts/evaluate.py
"""CLI tool to execute full walk-forward CV and benchmark models."""

import argparse
import logging
from pathlib import Path
import numpy as np
import pandas as pd

from ml.data.ingestion import CSVSeasonIngester
from ml.models.dixon_coles import DixonColesModel
from ml.evaluation.walk_forward import run_walk_forward_cv
from ml.evaluation.significance import wilcoxon_rps_test, mcnemar_accuracy_test
from ml.evaluation.calibration import compute_calibration
from ml.evaluation.backtest import simulate_betting
from ml.evaluation.report import EvaluationReport
from ml.evaluation.metrics import compute_rps, compute_accuracy

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("evaluate")


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate MatchSense models")
    parser.add_argument("--model", type=str, default="dixon_coles", choices=["dixon_coles"])
    parser.add_argument("--edge", type=float, default=0.05, help="EV edge threshold for backtesting")
    parser.add_argument("--output", type=str, default="reports/baseline_evaluation.md")
    return parser.parse_args()


def main():
    args = parse_args()

    # 1. Ensure 7 historical seasons exist (1920 through 2526)
    seasons = ["1920", "2021", "2122", "2223", "2324", "2425", "2526"]
    ingester = CSVSeasonIngester()
    matches = ingester.load_seasons(seasons)
    logger.info("Loaded %d matches across %d seasons", len(matches), len(seasons))

    # 2. Run walk-forward CV on 3 test seasons
    test_seasons = ["2023-24", "2024-25", "2025-26"]
    df_eval, fold_metrics = run_walk_forward_cv(
        model_factory=lambda: DixonColesModel(xi=0.005),
        matches_df=matches,
        test_seasons=test_seasons,
        window_size_seasons=4,
    )

    # 3. Aggregate metrics
    agg_metrics = {
        "rps": float(df_eval["rps"].mean()),
        "brier": float(df_eval["brier"].mean()),
        "log_loss": float(df_eval["log_loss"].mean()),
        "accuracy": float(df_eval["correct"].mean()),
    }

    # 4. Significance vs Baselines
    outcomes_1hot = np.zeros((len(df_eval), 3))
    for i, ftr in enumerate(df_eval["FTR"]):
        outcomes_1hot[i, 0 if ftr == "H" else (1 if ftr == "D" else 2)] = 1.0

    significance: dict[str, dict] = {}
    for base, col_prefix in [("Market Consensus (Avg)", "market"), ("Retail (B365)", "b365"), ("Empirical Prior", "empirical"), ("Uniform", "uniform")]:
        b_probs = df_eval[[f"prob_home_{col_prefix}", f"prob_draw_{col_prefix}", f"prob_away_{col_prefix}"]].to_numpy()
        b_rps = compute_rps(b_probs, outcomes_1hot)
        b_corr = compute_accuracy(b_probs, outcomes_1hot)

        w_res = wilcoxon_rps_test(df_eval["rps"].to_numpy(), b_rps)
        m_res = mcnemar_accuracy_test(df_eval["correct"].to_numpy(), b_corr)

        significance[base] = {
            "wilcoxon": {"statistic": w_res.statistic, "p_value": w_res.p_value, "mean_diff": w_res.mean_diff},
            "mcnemar": {"statistic": m_res.statistic, "p_value": m_res.p_value, "is_exact": m_res.is_exact},
        }

    # 5. Financial Backtests
    backtests: dict[str, dict] = {}
    for odds_pfx in ["Avg", "B365"]:
        for stak in ["flat", "quarter_kelly"]:
            res = simulate_betting(df_eval, odds_col_prefix=odds_pfx, edge_threshold=args.edge, staking=stak)
            key = f"{odds_pfx}_{stak}"
            backtests[key] = {
                "odds_source": odds_pfx,
                "staking": stak,
                "total_bets": res.total_bets,
                "turnover": res.turnover,
                "net_pnl": res.net_pnl,
                "roi": res.roi,
                "win_rate": res.win_rate,
                "max_drawdown_pct": res.max_drawdown_pct,
                "annualized_sharpe": res.annualized_sharpe,
            }

    # 6. Build Report
    report = EvaluationReport(
        model_name=args.model,
        folds=fold_metrics,
        aggregate_metrics=agg_metrics,
        significance_results=significance,
        backtest_results=backtests,
        calibration_results={},
    )

    report.print_summary()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report.to_markdown())
    logger.info("Report saved to %s", out_path)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run CLI to produce baseline scorecard**
Run: `uv run python scripts/evaluate.py --output reports/baseline_evaluation.md`
Expected: Output report saved to `reports/baseline_evaluation.md` with 0 errors.

- [ ] **Step 3: Run full pytest suite & lint gates**
Run: `uv run pytest`
Run: `uv run ruff check .`
Run: `uv run mypy backend/ ml/`
Expected: All tests pass, 0 linter errors, 0 type errors.

- [ ] **Step 4: Commit**
```bash
git add scripts/evaluate.py reports/baseline_evaluation.md
git commit -m "feat(eval): add evaluation CLI and baseline benchmark report"
```
