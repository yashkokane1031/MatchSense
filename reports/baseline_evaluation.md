# MatchSense — Model Evaluation Report: `dixon_coles`

## 1. Out-of-Sample Performance by Season (Rolling 4-Season Window)

| Season | Matches | RPS | Brier Score | Log-Loss | Accuracy | Convergence |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **2023-24** | 380 | 0.1905 | 0.5494 | 0.9339 | 57.6% | 38/38 GW |
| **2024-25** | 380 | 0.2000 | 0.5827 | 0.9749 | 52.9% | 38/38 GW |
| **2025-26** | 380 | 0.2116 | 0.6228 | 1.0528 | 46.3% | 38/38 GW |
| **Aggregate** | **1,140** | **0.2007** | **0.5850** | **0.9872** | **52.3%** | **114/114 GW** |

> [!NOTE]
> **Convergence & Numerical Stability Verification**:
> Across all 3 seasons (114 sequential gameweek refits), 100% of optimizations converged cleanly under L-BFGS-B with dynamic reference team constraints, parameter warm-starting, and relaxed evaluation limits (38/38 GW per fold, 114/114 GW total).
> Re-evaluating against earlier un-warm-started fits shows headline out-of-sample metrics rounding to identical values at 4 decimal places (RPS 0.2007, Accuracy 52.3%) with only microscopic shifts in Wilcoxon rank-sum statistics (e.g., vs Market Avg in 2023-24: $W=30,559.0 \to 30,556.0$; vs B365: $30,655.0 \to 30,653.0$). This confirms that pre-fix iterations terminating at maxfun limits were already exceptionally close to the true likelihood optimum (minor parameter perturbations affecting only borderline predictions), rather than divergent or degenerate.

## 2. Statistical Significance vs Baselines (Primary: Per-Fold Independent)

### Fold Season: `2023-24`

| Comparison | Metric | Test | Stat | p-value | Interpretation |
| :--- | :--- | :--- | :---: | :---: | :--- |
| vs Market Consensus (Avg) | RPS | Wilcoxon (Pratt) | W=30556.0, diff_RPS=+0.0067 | 0.0085 | Baseline better (p < 0.05 *) |
| vs Market Consensus (Avg) | Accuracy | McNemar (Chi2) | stat=0.5 | 0.4862 | not significant |
| vs Retail Bookmaker (B365) | RPS | Wilcoxon (Pratt) | W=30653.0, diff_RPS=+0.0067 | 0.0097 | Baseline better (p < 0.05 *) |
| vs Retail Bookmaker (B365) | Accuracy | McNemar (Chi2) | stat=1.5 | 0.2159 | not significant |
| vs Empirical Prior | RPS | Wilcoxon (Pratt) | W=22629.0, diff_RPS=-0.0436 | 0.0000 | Model better (p < 0.05 *) |
| vs Empirical Prior | Accuracy | McNemar (Chi2) | stat=16.2 | 0.0001 | Model better (p < 0.05 *) |
| vs Naive Uniform | RPS | Wilcoxon (Pratt) | W=22360.0, diff_RPS=-0.0513 | 0.0000 | Model better (p < 0.05 *) |
| vs Naive Uniform | Accuracy | McNemar (Chi2) | stat=16.2 | 0.0001 | Model better (p < 0.05 *) |

### Fold Season: `2024-25`

| Comparison | Metric | Test | Stat | p-value | Interpretation |
| :--- | :--- | :--- | :---: | :---: | :--- |
| vs Market Consensus (Avg) | RPS | Wilcoxon (Pratt) | W=34972.0, diff_RPS=+0.0026 | 0.5681 | not significant |
| vs Market Consensus (Avg) | Accuracy | McNemar (Chi2) | stat=0.5 | 0.4862 | not significant |
| vs Retail Bookmaker (B365) | RPS | Wilcoxon (Pratt) | W=35119.0, diff_RPS=+0.0027 | 0.6155 | not significant |
| vs Retail Bookmaker (B365) | Accuracy | McNemar (Chi2) | stat=0.3 | 0.6069 | not significant |
| vs Empirical Prior | RPS | Wilcoxon (Pratt) | W=24897.0, diff_RPS=-0.0351 | 0.0000 | Model better (p < 0.05 *) |
| vs Empirical Prior | Accuracy | McNemar (Chi2) | stat=16.9 | 0.0000 | Model better (p < 0.05 *) |
| vs Naive Uniform | RPS | Wilcoxon (Pratt) | W=25600.0, diff_RPS=-0.0370 | 0.0000 | Model better (p < 0.05 *) |
| vs Naive Uniform | Accuracy | McNemar (Chi2) | stat=16.9 | 0.0000 | Model better (p < 0.05 *) |

### Fold Season: `2025-26`

| Comparison | Metric | Test | Stat | p-value | Interpretation |
| :--- | :--- | :--- | :---: | :---: | :--- |
| vs Market Consensus (Avg) | RPS | Wilcoxon (Pratt) | W=32903.0, diff_RPS=+0.0063 | 0.1244 | not significant |
| vs Market Consensus (Avg) | Accuracy | McNemar (Chi2) | stat=3.8 | 0.0518 | not significant |
| vs Retail Bookmaker (B365) | RPS | Wilcoxon (Pratt) | W=33468.0, diff_RPS=+0.0058 | 0.2031 | not significant |
| vs Retail Bookmaker (B365) | Accuracy | McNemar (Chi2) | stat=2.7 | 0.1003 | not significant |
| vs Empirical Prior | RPS | Wilcoxon (Pratt) | W=28323.0, diff_RPS=-0.0163 | 0.0002 | Model better (p < 0.05 *) |
| vs Empirical Prior | Accuracy | McNemar (Chi2) | stat=1.6 | 0.2067 | not significant |
| vs Naive Uniform | RPS | Wilcoxon (Pratt) | W=29583.0, diff_RPS=-0.0206 | 0.0020 | Model better (p < 0.05 *) |
| vs Naive Uniform | Accuracy | McNemar (Chi2) | stat=1.6 | 0.2067 | not significant |

### Pooled 3-Season Performance (Descriptive)

> [!NOTE]
> **Caveat**: The pooled 1,140-match significance test combines overlapping training windows across adjacent seasons; per-fold test statistics provide the primary independent verification.

| Comparison | Metric | Test | Stat | p-value | Interpretation |
| :--- | :--- | :--- | :---: | :---: | :--- |
| vs Market Consensus (Avg) | RPS | Wilcoxon (Pratt) | W=294681.0, diff_RPS=+0.0052 | 0.0061 | Baseline better (p < 0.05 *) |
| vs Market Consensus (Avg) | Accuracy | McNemar (Chi2) | stat=4.5 | 0.0339 | Baseline better (p < 0.05 *) |
| vs Retail Bookmaker (B365) | RPS | Wilcoxon (Pratt) | W=297191.0, diff_RPS=+0.0051 | 0.0118 | Baseline better (p < 0.05 *) |
| vs Retail Bookmaker (B365) | Accuracy | McNemar (Chi2) | stat=4.6 | 0.0321 | Baseline better (p < 0.05 *) |
| vs Empirical Prior | RPS | Wilcoxon (Pratt) | W=226799.0, diff_RPS=-0.0317 | 0.0000 | Model better (p < 0.05 *) |
| vs Empirical Prior | Accuracy | McNemar (Chi2) | stat=31.2 | 0.0000 | Model better (p < 0.05 *) |
| vs Naive Uniform | RPS | Wilcoxon (Pratt) | W=230083.0, diff_RPS=-0.0363 | 0.0000 | Model better (p < 0.05 *) |
| vs Naive Uniform | Accuracy | McNemar (Chi2) | stat=31.2 | 0.0000 | Model better (p < 0.05 *) |

## 3. Financial Simulation & ROI (Edge >= 5%)

| Odds Source | Staking | Bets | Turnover | Net PnL | ROI % | Win % | Max DD % | Annual Sharpe |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Avg | flat | 796 | 796.0u | -56.3u | -7.1% | 30.5% | 78.3% | -0.10 |
| Avg | quarter_kelly | 796 | 1333.4u | -68.5u | -5.1% | 30.5% | 83.1% | -0.26 |
| B365 | flat | 766 | 766.0u | -19.1u | -2.5% | 30.9% | 71.2% | 0.06 |
| B365 | quarter_kelly | 766 | 1332.5u | -52.8u | -4.0% | 30.9% | 80.1% | -0.05 |

## 4. Calibration & Reliability Summary

- **Overall ECE**: `0.0300` (3.0%)
- **Home ECE / MCE**: `0.0292` / `0.1310`
- **Draw ECE / MCE**: `0.0259` / `0.0865`
- **Away ECE / MCE**: `0.0350` / `0.4384`

> **Note on Away MCE (0.4384)**: The worst-case bin is `[0.9, 1.0]` containing only `|B_m| = 2` match(es) (observed frequency 0.5000 vs 0.9384 predicted). Its contribution to the overall Away ECE is negligible (0.00077), confirming that probability calibration is robust across well-populated bins.

### Away Outcome Reliability Bins (1,140 Matches)

| Bin Range | Matches | Mean Pred | Obs Freq | Calibration Gap |
| :--- | :---: | :---: | :---: | :---: |
| [0.0, 0.1] | 87 | 0.0663 | 0.0920 | 0.0256 |
| [0.1, 0.2] | 193 | 0.1507 | 0.1244 | 0.0264 |
| [0.2, 0.3] | 249 | 0.2496 | 0.2369 | 0.0126 |
| [0.3, 0.4] | 220 | 0.3469 | 0.3727 | 0.0258 |
| [0.4, 0.5] | 169 | 0.4444 | 0.3550 | 0.0894 |
| [0.5, 0.6] | 108 | 0.5452 | 0.5185 | 0.0267 |
| [0.6, 0.7] | 74 | 0.6446 | 0.6622 | 0.0176 |
| [0.7, 0.8] | 28 | 0.7423 | 0.8214 | 0.0792 |
| [0.8, 0.9] | 10 | 0.8361 | 0.7000 | 0.1361 |
| [0.9, 1.0] | 2 | 0.9384 | 0.5000 | 0.4384 |
