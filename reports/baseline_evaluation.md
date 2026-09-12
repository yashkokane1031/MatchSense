# MatchSense — Model Evaluation Report: `dixon_coles`

## 1. Out-of-Sample Performance by Season (Rolling 4-Season Window)

| Season | Matches | RPS | Brier Score | Log-Loss | Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **2023-24** | 380 | 0.1905 | 0.5494 | 0.9339 | 57.6% |
| **2024-25** | 380 | 0.2000 | 0.5827 | 0.9749 | 52.9% |
| **2025-26** | 380 | 0.2116 | 0.6228 | 1.0528 | 46.3% |
| **Aggregate** | **1,140** | **0.2007** | **0.5850** | **0.9872** | **52.3%** |

## 2. Statistical Significance vs Baselines (Primary: Per-Fold Independent)

### Fold Season: `2023-24`

| Comparison | Metric | Test | Stat | p-value | Interpretation |
| :--- | :--- | :--- | :---: | :---: | :--- |
| vs Market Consensus (Avg) | RPS | Wilcoxon (Pratt) | W=30559.0 | 0.0085 | p < 0.05 * |
| vs Market Consensus (Avg) | Accuracy | McNemar (Chi2) | stat=0.5 | 0.4862 | not significant |
| vs Retail Bookmaker (B365) | RPS | Wilcoxon (Pratt) | W=30655.0 | 0.0097 | p < 0.05 * |
| vs Retail Bookmaker (B365) | Accuracy | McNemar (Chi2) | stat=1.5 | 0.2159 | not significant |
| vs Empirical Prior | RPS | Wilcoxon (Pratt) | W=22628.0 | 0.0000 | p < 0.05 * |
| vs Empirical Prior | Accuracy | McNemar (Chi2) | stat=16.2 | 0.0001 | p < 0.05 * |
| vs Naive Uniform | RPS | Wilcoxon (Pratt) | W=22358.0 | 0.0000 | p < 0.05 * |
| vs Naive Uniform | Accuracy | McNemar (Chi2) | stat=16.2 | 0.0001 | p < 0.05 * |

### Fold Season: `2024-25`

| Comparison | Metric | Test | Stat | p-value | Interpretation |
| :--- | :--- | :--- | :---: | :---: | :--- |
| vs Market Consensus (Avg) | RPS | Wilcoxon (Pratt) | W=34973.0 | 0.5685 | not significant |
| vs Market Consensus (Avg) | Accuracy | McNemar (Chi2) | stat=0.5 | 0.4862 | not significant |
| vs Retail Bookmaker (B365) | RPS | Wilcoxon (Pratt) | W=35117.0 | 0.6149 | not significant |
| vs Retail Bookmaker (B365) | Accuracy | McNemar (Chi2) | stat=0.3 | 0.6069 | not significant |
| vs Empirical Prior | RPS | Wilcoxon (Pratt) | W=24899.0 | 0.0000 | p < 0.05 * |
| vs Empirical Prior | Accuracy | McNemar (Chi2) | stat=16.9 | 0.0000 | p < 0.05 * |
| vs Naive Uniform | RPS | Wilcoxon (Pratt) | W=25602.0 | 0.0000 | p < 0.05 * |
| vs Naive Uniform | Accuracy | McNemar (Chi2) | stat=16.9 | 0.0000 | p < 0.05 * |

### Fold Season: `2025-26`

| Comparison | Metric | Test | Stat | p-value | Interpretation |
| :--- | :--- | :--- | :---: | :---: | :--- |
| vs Market Consensus (Avg) | RPS | Wilcoxon (Pratt) | W=32903.0 | 0.1244 | not significant |
| vs Market Consensus (Avg) | Accuracy | McNemar (Chi2) | stat=3.8 | 0.0518 | not significant |
| vs Retail Bookmaker (B365) | RPS | Wilcoxon (Pratt) | W=33466.0 | 0.2028 | not significant |
| vs Retail Bookmaker (B365) | Accuracy | McNemar (Chi2) | stat=2.7 | 0.1003 | not significant |
| vs Empirical Prior | RPS | Wilcoxon (Pratt) | W=28322.0 | 0.0002 | p < 0.05 * |
| vs Empirical Prior | Accuracy | McNemar (Chi2) | stat=1.6 | 0.2067 | not significant |
| vs Naive Uniform | RPS | Wilcoxon (Pratt) | W=29584.0 | 0.0020 | p < 0.05 * |
| vs Naive Uniform | Accuracy | McNemar (Chi2) | stat=1.6 | 0.2067 | not significant |

### Pooled 3-Season Performance (Descriptive)

> [!NOTE]
> **Caveat**: The pooled 1,140-match significance test combines overlapping training windows across adjacent seasons; per-fold test statistics provide the primary independent verification.

| Comparison | Metric | Test | Stat | p-value | Interpretation |
| :--- | :--- | :--- | :---: | :---: | :--- |
| vs Market Consensus (Avg) | RPS | Wilcoxon (Pratt) | W=294692.0 | 0.0061 | p < 0.05 * |
| vs Market Consensus (Avg) | Accuracy | McNemar (Chi2) | stat=4.5 | 0.0339 | p < 0.05 * |
| vs Retail Bookmaker (B365) | RPS | Wilcoxon (Pratt) | W=297182.0 | 0.0118 | p < 0.05 * |
| vs Retail Bookmaker (B365) | Accuracy | McNemar (Chi2) | stat=4.6 | 0.0321 | p < 0.05 * |
| vs Empirical Prior | RPS | Wilcoxon (Pratt) | W=226793.0 | 0.0000 | p < 0.05 * |
| vs Empirical Prior | Accuracy | McNemar (Chi2) | stat=31.2 | 0.0000 | p < 0.05 * |
| vs Naive Uniform | RPS | Wilcoxon (Pratt) | W=230086.0 | 0.0000 | p < 0.05 * |
| vs Naive Uniform | Accuracy | McNemar (Chi2) | stat=31.2 | 0.0000 | p < 0.05 * |

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
