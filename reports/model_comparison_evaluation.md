# MatchSense — Multi-Model Comparative Evaluation: XGBoost vs. Dixon-Coles

## 1. Executive Summary & Out-of-Sample Performance

Comparative benchmark of `XGBoostPredictor` (advanced feature pipeline: window-anchored Elo, rolling shots/corners, separated xG) against `DixonColesModel` (Poisson intensity model with time decay) across 1,140 Premier League matches (3 out-of-sample seasons: 2023-24, 2024-25, 2025-26) under identical rolling 4-season walk-forward cross-validation.

| Architecture | Model Class | Matches | RPS | Brier Score | Log-Loss | Accuracy | Convergence |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dixon-Coles** | Generative Poisson (Bivariate) | 1,140 | 0.2007 | 0.5850 | 0.9872 | 52.3% | 114/114 GW |
| **XGBoost** | Discriminative Gradient Boosted Trees | 1,140 | 0.2036 | 0.5927 | 0.9962 | 53.2% | 114/114 GW |

## 2. Direct Head-to-Head Comparison: XGBoost vs. Dixon-Coles

Direct paired statistical tests on matched out-of-sample fixture predictions. Negative diff_RPS indicates XGBoost superior accuracy; positive indicates Dixon-Coles superior accuracy.

| Season / Scope | Matches | RPS (DC) | RPS (XGB) | diff_RPS (XGB - DC) [negative = XGBoost better] | Wilcoxon p-value | Acc (DC) | Acc (XGB) | McNemar p-value | Better |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **2023-24** | 380 | 0.1905 | 0.1933 | +0.0027 | 0.3542 | 57.6% | 59.5% | 0.2812 | **Tied / Not Significant** |
| **2024-25** | 380 | 0.2000 | 0.2044 | +0.0045 | 0.0712 | 52.9% | 52.6% | 1.0000 | **Tied / Not Significant** |
| **2025-26** | 380 | 0.2116 | 0.2132 | +0.0016 | 0.3734 | 46.3% | 47.6% | 0.4576 | **Tied / Not Significant** |
| **Pooled (3 Seasons)** | **1,140** | **0.2007** | **0.2036** | **+0.0029** | **0.0329** | **52.3%** | **53.2%** | **0.3049** | **Dixon-Coles** |

> [!NOTE]
> **Interpretation of Comparative Findings**:
> - **RPS Metric**: Across all 3 individual folds, the models are statistically indistinguishable ($p > 0.05$). On the pooled 1,140 matches, Dixon-Coles retains a slight, statistically significant advantage in probabilistic score quality ($\Delta\text{RPS} = +0.0029$, Wilcoxon $p = 0.0329$).
> - **Accuracy Metric**: While XGBoost shows a +1.0% difference in nominal classification accuracy pooled (53.2% vs 52.3%), paired McNemar tests confirm this difference is **statistically indistinguishable from noise** ($p = 0.3049$ pooled; $p > 0.25$ across all individual folds). Neither model holds a statistically verifiable accuracy advantage.
> - **Optimizer Stability**: 100% of weekly refits converged cleanly across both models (114/114 GW). Headline RPS and accuracy remain identical to 4 decimal places with microscopic Wilcoxon shifts ($W=30,559.0 \to 30,556.0$), verifying that previous iterations near maxfun limits were already within the near-optimum neighborhood.
> - **Caveat on Pooled Testing**: The pooled 1,140-match significance test combines overlapping rolling training windows across adjacent seasons; per-fold test statistics provide the primary independent verification.

## 3. Performance vs. Market Consensus Lines (1,140 Matches)

Comparison against closing market consensus odds (AvgH, AvgD, AvgA). Negative diff indicates model outperforming the market.

| Architecture | Model RPS | Market RPS | diff_RPS (Model - Market) | Model Acc | Market Acc | Wilcoxon p-val | Market Outperformed? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Dixon-Coles** | 0.2007 | 0.1955 | +0.0052 | 52.3% | 54.2% | 0.0061 | NO (Market Superior) |
| **XGBoost** | 0.2036 | 0.1955 | +0.0081 | 53.2% | 54.2% | 0.0000 | NO (Market Superior) |

## 4. Probability Calibration & Reliability Summary

| Metric | Dixon-Coles | XGBoost | Better Calibration |
| :--- | :---: | :---: | :--- |
| **Overall ECE** | 0.0300 (3.0%) | 0.0289 (2.9%) | **XGBoost** |
| **Home ECE** | 0.0292 (2.9%) | 0.0279 (2.8%) | **XGBoost** |
| **Draw ECE** | 0.0259 (2.6%) | 0.0295 (2.9%) | **Dixon-Coles** |
| **Away ECE** | 0.0350 (3.5%) | 0.0292 (2.9%) | **XGBoost** |
| **Home MCE** | 0.1310 (13.1%) | 0.1092 (10.9%) | **XGBoost** |
| **Draw MCE** | 0.0865 (8.6%) | 0.4129 (41.3%) | **Dixon-Coles** |
| **Away MCE** | 0.4384 (43.8%) | 0.8009 (80.1%) | **Dixon-Coles** |

### Away Outcome Reliability Bins Breakdown (1,140 Matches)

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

> **Context on Extreme Away MCE**:
> - For Dixon-Coles, the worst-case bin `[0.9, 1.0]` contains only $|B_m| = 2$ matches (1 win, obs 0.5000 vs 0.9384 pred $\to$ gap 0.4384). Its weighted contribution to ECE is $2/1140 \times 0.4384 = 0.00077$.
> - For XGBoost, the worst-case bin `[0.8, 0.9]` contains **exactly 1 match** ($|B_m| = 1$, 0 wins, obs 0.0 vs 0.8009 pred $\to$ gap 0.8009), while bin `[0.9, 1.0]` has 0 matches. Its weighted contribution to ECE is $1/1140 \times 0.8009 = 0.00070$.
> - Both models exhibit the identical small-sample tail artifact in rare high-confidence away predictions. Across all well-populated bins ($|B_m| \ge 29$), both models calibrate smoothly within 0.5%–9.7%, demonstrating that their overall ECE values (2.89% vs 3.00%) represent comparable, robust calibration across well-populated probability ranges.

## 5. Financial Simulation & ROI (Edge >= 5%)

| Model | Odds Source | Staking | Bets | Turnover | Net PnL | ROI % | Win % | Max DD % | Annual Sharpe |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dixon-Coles** | Avg | flat | 796 | 796.0u | -56.3u | -7.1% | 30.5% | 78.3% | -0.10 |
| **Dixon-Coles** | Avg | quarter_kelly | 796 | 1333.4u | -68.5u | -5.1% | 30.5% | 83.1% | -0.26 |
| **Dixon-Coles** | B365 | flat | 766 | 766.0u | -19.1u | -2.5% | 30.9% | 71.2% | 0.06 |
| **Dixon-Coles** | B365 | quarter_kelly | 766 | 1332.5u | -52.8u | -4.0% | 30.9% | 80.1% | -0.05 |
| **XGBoost** | Avg | flat | 928 | 928.0u | -118.1u | -12.7% | 30.1% | 134.2% | -0.75 |
| **XGBoost** | Avg | quarter_kelly | 928 | 840.8u | -94.6u | -11.2% | 30.1% | 96.1% | -0.90 |
| **XGBoost** | B365 | flat | 897 | 897.0u | -73.7u | -8.2% | 31.0% | 114.3% | 0.09 |
| **XGBoost** | B365 | quarter_kelly | 897 | 1036.7u | -89.7u | -8.6% | 31.0% | 95.4% | -0.62 |

## 6. Automated Sanity Verification Gates

| Gate | Criterion | Threshold / Requirement | Measured Value | Status |
| :---: | :--- | :--- | :--- | :---: |
| **Gate 1** | Mathematical Invariants | Sum(P) = 1.0 +/- 1e-5, P(c) >= 0 | `max_dev = 1.11e-16, non-negative = True` | **[PASS]** |
| **Gate 2** | RPS Empirical Sanity Range | Pooled RPS in [0.180, 0.240] | `Pooled RPS = 0.2036` | **[PASS]** |
| **Gate 3** | Cold-Start Safety Fallback | Promoted succeeds via Q25 Elo; fake 404s | `Luton prob_sum = 1.0000` | **[PASS]** |
| **Gate 4** | Execution Budget (Walk-Forward CV) | 3-Fold Walk-Forward CV < 180.0s per model | `XGBoost: 115.85s (1.02s/GW); Dixon-Coles: 125.02s (1.10s/GW)` | **[PASS]** |
| **Gate 5** | Regression Guard | All tests continue to pass | `Zero regressions across full suite` | **[PASS]** |

### Refit Complexity & Execution Budget Analysis (Gate 4)

- **Dixon-Coles Runtime (125.02s / 1.10s per refit)**: Dixon-Coles operates strictly on raw match fixtures (`HomeTeam`, `AwayTeam`, `Date`, `FTHG`, `FTAG`) and does NOT evaluate feature pipelines. Its runtime is driven by numerical optimization of 51–55 parameters ($2N+1$ for $N \in [25, 27]$ clubs across the rolling 4-season window: $(N-1)$ free attack + $N$ defense + $\gamma$ + $\rho$, with $\alpha_{\text{ref}} = 1.0$ pinned). Enabling parameter warm-starting across consecutive gameweeks reduced average optimization iterations by ~38%, reducing total 3-season CV runtime from 181.88s pre-warm-start to 125.02s (1.10s per refit).
- **XGBoost Runtime (115.85s / 1.02s per refit)**: Includes dynamic window-anchored Elo recomputation (105ms) and 120 regularized gradient-boosted trees over 70 features on 1,520 rows (~950ms).
- **Takeaway**: With warm-starting enabled for Dixon-Coles and precomputed bounded features for XGBoost, both models complete 3 full seasons of walk-forward cross-validation (114 sequential refits) in approximately 1.9–2.0 minutes (~0.99–1.05s per gameweek refit), comfortably within the operational budget (< 180s total, < 1.5s per gameweek).
