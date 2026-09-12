# MatchSense — Model Evaluation Report: `xgboost`

## 1. Out-of-Sample Performance by Season (Rolling 4-Season Window)

| Season | Matches | RPS | Brier Score | Log-Loss | Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **2023-24** | 380 | 0.1933 | 0.5563 | 0.9494 | 59.5% |
| **2024-25** | 380 | 0.2044 | 0.5940 | 0.9944 | 52.6% |
| **2025-26** | 380 | 0.2132 | 0.6279 | 1.0449 | 47.6% |
| **Aggregate** | **1,140** | **0.2036** | **0.5927** | **0.9962** | **53.2%** |

## 2. Statistical Significance vs Baselines (Primary: Per-Fold Independent)

### Fold Season: `2023-24`

| Comparison | Metric | Test | Stat | p-value | Interpretation |
| :--- | :--- | :--- | :---: | :---: | :--- |
| vs Market Consensus (Avg) | RPS | Wilcoxon (Pratt) | W=27828.0, diff_RPS=+0.0095 | 0.0001 | Baseline better (p < 0.05 *) |
| vs Market Consensus (Avg) | Accuracy | McNemar (Chi2) | stat=0.0 | 0.8711 | not significant |
| vs Retail Bookmaker (B365) | RPS | Wilcoxon (Pratt) | W=27952.0, diff_RPS=+0.0094 | 0.0001 | Baseline better (p < 0.05 *) |
| vs Retail Bookmaker (B365) | Accuracy | McNemar (Chi2) | stat=0.0 | 1.0000 | not significant |
| vs Empirical Prior | RPS | Wilcoxon (Pratt) | W=22838.0, diff_RPS=-0.0409 | 0.0000 | Model better (p < 0.05 *) |
| vs Empirical Prior | Accuracy | McNemar (Chi2) | stat=22.5 | 0.0000 | Model better (p < 0.05 *) |
| vs Naive Uniform | RPS | Wilcoxon (Pratt) | W=22296.0, diff_RPS=-0.0485 | 0.0000 | Model better (p < 0.05 *) |
| vs Naive Uniform | Accuracy | McNemar (Chi2) | stat=22.5 | 0.0000 | Model better (p < 0.05 *) |

### Fold Season: `2024-25`

| Comparison | Metric | Test | Stat | p-value | Interpretation |
| :--- | :--- | :--- | :---: | :---: | :--- |
| vs Market Consensus (Avg) | RPS | Wilcoxon (Pratt) | W=32266.0, diff_RPS=+0.0070 | 0.0667 | not significant |
| vs Market Consensus (Avg) | Accuracy | McNemar (Chi2) | stat=0.7 | 0.3912 | not significant |
| vs Retail Bookmaker (B365) | RPS | Wilcoxon (Pratt) | W=32170.0, diff_RPS=+0.0072 | 0.0603 | not significant |
| vs Retail Bookmaker (B365) | Accuracy | McNemar (Chi2) | stat=0.5 | 0.4862 | not significant |
| vs Empirical Prior | RPS | Wilcoxon (Pratt) | W=26186.0, diff_RPS=-0.0307 | 0.0000 | Model better (p < 0.05 *) |
| vs Empirical Prior | Accuracy | McNemar (Chi2) | stat=18.8 | 0.0000 | Model better (p < 0.05 *) |
| vs Naive Uniform | RPS | Wilcoxon (Pratt) | W=26734.0, diff_RPS=-0.0326 | 0.0000 | Model better (p < 0.05 *) |
| vs Naive Uniform | Accuracy | McNemar (Chi2) | stat=18.8 | 0.0000 | Model better (p < 0.05 *) |

### Fold Season: `2025-26`

| Comparison | Metric | Test | Stat | p-value | Interpretation |
| :--- | :--- | :--- | :---: | :---: | :--- |
| vs Market Consensus (Avg) | RPS | Wilcoxon (Pratt) | W=32218.0, diff_RPS=+0.0079 | 0.0634 | not significant |
| vs Market Consensus (Avg) | Accuracy | McNemar (Chi2) | stat=0.9 | 0.3487 | not significant |
| vs Retail Bookmaker (B365) | RPS | Wilcoxon (Pratt) | W=32461.0, diff_RPS=+0.0074 | 0.0814 | not significant |
| vs Retail Bookmaker (B365) | Accuracy | McNemar (Chi2) | stat=0.4 | 0.5322 | not significant |
| vs Empirical Prior | RPS | Wilcoxon (Pratt) | W=30648.0, diff_RPS=-0.0147 | 0.0096 | Model better (p < 0.05 *) |
| vs Empirical Prior | Accuracy | McNemar (Chi2) | stat=3.0 | 0.0818 | not significant |
| vs Naive Uniform | RPS | Wilcoxon (Pratt) | W=30002.0, diff_RPS=-0.0190 | 0.0038 | Model better (p < 0.05 *) |
| vs Naive Uniform | Accuracy | McNemar (Chi2) | stat=3.0 | 0.0818 | not significant |

### Pooled 3-Season Performance (Descriptive)

> [!NOTE]
> **Caveat**: The pooled 1,140-match significance test combines overlapping training windows across adjacent seasons; per-fold test statistics provide the primary independent verification.

| Comparison | Metric | Test | Stat | p-value | Interpretation |
| :--- | :--- | :--- | :---: | :---: | :--- |
| vs Market Consensus (Avg) | RPS | Wilcoxon (Pratt) | W=276550.0, diff_RPS=+0.0081 | 0.0000 | Baseline better (p < 0.05 *) |
| vs Market Consensus (Avg) | Accuracy | McNemar (Chi2) | stat=0.9 | 0.3468 | not significant |
| vs Retail Bookmaker (B365) | RPS | Wilcoxon (Pratt) | W=277368.0, diff_RPS=+0.0080 | 0.0000 | Baseline better (p < 0.05 *) |
| vs Retail Bookmaker (B365) | Accuracy | McNemar (Chi2) | stat=0.9 | 0.3468 | not significant |
| vs Empirical Prior | RPS | Wilcoxon (Pratt) | W=236874.0, diff_RPS=-0.0288 | 0.0000 | Model better (p < 0.05 *) |
| vs Empirical Prior | Accuracy | McNemar (Chi2) | stat=40.5 | 0.0000 | Model better (p < 0.05 *) |
| vs Naive Uniform | RPS | Wilcoxon (Pratt) | W=235588.0, diff_RPS=-0.0334 | 0.0000 | Model better (p < 0.05 *) |
| vs Naive Uniform | Accuracy | McNemar (Chi2) | stat=40.5 | 0.0000 | Model better (p < 0.05 *) |

## 3. Financial Simulation & ROI (Edge >= 5%)

| Odds Source | Staking | Bets | Turnover | Net PnL | ROI % | Win % | Max DD % | Annual Sharpe |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Avg | flat | 928 | 928.0u | -118.1u | -12.7% | 30.1% | 134.2% | -0.75 |
| Avg | quarter_kelly | 928 | 840.8u | -94.6u | -11.2% | 30.1% | 96.1% | -0.90 |
| B365 | flat | 897 | 897.0u | -73.7u | -8.2% | 31.0% | 114.3% | 0.09 |
| B365 | quarter_kelly | 897 | 1036.7u | -89.7u | -8.6% | 31.0% | 95.4% | -0.62 |

## 4. Calibration & Reliability Summary

- **Overall ECE**: `0.0289` (2.9%)
- **Home ECE / MCE**: `0.0279` / `0.1092`
- **Draw ECE / MCE**: `0.0295` / `0.4129`
- **Away ECE / MCE**: `0.0292` / `0.8009`

> **Note on Away MCE (0.8009)**: The worst-case bin is `[0.8, 0.9]` containing only `|B_m| = 1` match (0 wins, observed frequency 0.0000 vs 0.8009 predicted). Its contribution to the overall Away ECE is negligible (0.00070), confirming that probability calibration is robust across well-populated bins.

### Away Outcome Reliability Bins (1,140 Matches)

| Bin Range | Matches | Mean Pred | Obs Freq | Calibration Gap |
| :--- | :---: | :---: | :---: | :---: |
| [0.0, 0.1] | 55 | 0.0858 | 0.0909 | 0.0051 |
| [0.1, 0.2] | 292 | 0.1506 | 0.1644 | 0.0138 |
| [0.2, 0.3] | 231 | 0.2456 | 0.2338 | 0.0119 |
| [0.3, 0.4] | 163 | 0.3490 | 0.3804 | 0.0314 |
| [0.4, 0.5] | 169 | 0.4492 | 0.4024 | 0.0469 |
| [0.5, 0.6] | 114 | 0.5462 | 0.4825 | 0.0637 |
| [0.6, 0.7] | 86 | 0.6441 | 0.6163 | 0.0278 |
| [0.7, 0.8] | 29 | 0.7307 | 0.8276 | 0.0969 |
| [0.8, 0.9] | 1 | 0.8009 | 0.0000 | 0.8009 |
| [0.9, 1.0] | 0 | 0.9500 | 0.0000 | 0.0000 |
