# MatchSense — Phase 1 Implementation & Training Walkthrough

Phase 1 of **MatchSense** is complete. We built, optimized, and verified the end-to-end Dixon-Coles match prediction engine, feature engineering pipeline, database layer, REST API, test suite, and trained the model on real Premier League data.

---

## 1. Resolution of Data Churn & Season Scope

To address the risk of parameter noise and high estimation variance caused by promotion/relegation churn across 7 seasons (~50+ teams), the historical training dataset was capped to **4 seasons**:
- **Seasons**: `2022-23` (`2223`), `2023-24` (`2324`), `2024-25` (`2425`), and `2025-26` (`2526`).
- **Total Matches**: **1,520 matches**.
- **Unique Teams**: **25 teams** (Arsenal, Aston Villa, Bournemouth, Brentford, Brighton, Burnley, Chelsea, Crystal Palace, Everton, Fulham, Ipswich, Leeds, Leicester, Liverpool, Luton, Manchester City, Manchester Utd, Newcastle, Nottingham Forest, Sheffield Utd, Southampton, Sunderland, Tottenham, West Ham, Wolverhampton).
- **Reference Team**: **Arsenal** (152 matches, $\alpha = 1.0$).
- **Identifiability & Stability**: With 25 teams, exactly 51 parameters (24 free attack + 25 defense + 1 home advantage $\gamma$ + 1 low-score correction $\rho$) are estimated, avoiding underdetermined estimates for short-stint teams while preserving full historical signal where time-decay ($w(t) = e^{-\xi \Delta t}$) has non-negligible weight.

---

## 2. Model Training & Optimization Performance

We vectorized the Dixon-Coles negative log-likelihood function using NumPy arrays and precomputed combinatorial masks:
- **Optimization Algorithm**: Scipy `minimize(method="L-BFGS-B")`.
- **Iterations to Convergence**: **111 iterations**.
- **Training Wall-Clock Time**: **745 milliseconds** (down from ~5 minutes unvectorized).
- **Convergence Status**: Successfully converged (`result.success = True`).

### Fitted Global Parameters
| Parameter | Value | Interpretation |
| :--- | :--- | :--- |
| **Home Advantage ($\gamma$)** | **1.213** | Confirmed $\gamma > 1.0$. Home teams generate ~21.3% more expected goals than away teams, matching empirical Premier League averages. |
| **Dixon-Coles Low-Score Correction ($\rho$)** | **-0.1326** | Negative as expected by Dixon & Coles (1997), adjusting for the slight undersupply of 0-0 and low draws compared to independent Poisson distributions. |
| **Decay Rate ($\xi$)** | **0.005** | Exponential daily time decay giving higher influence to recent matches. |

---

## 3. Team Strength Sanity Check

In Dixon-Coles, higher $\alpha$ indicates stronger attacking output, while lower $\beta$ indicates a tighter defense (conceding fewer expected goals).

### Top 5 Attack Strengths ($\alpha$)
1. **Manchester City**: $\alpha = 1.107$
2. **Arsenal**: $\alpha = 1.000$ (Reference)
3. **Liverpool**: $\alpha = 0.991$
4. **Manchester Utd**: $\alpha = 0.984$
5. **Aston Villa**: $\alpha = 0.871$

### Top 5 Defenses (Lowest Conceded Expected Goals $\beta$)
1. **Arsenal**: $\beta = 0.876$ (Best defensive record)
2. **Manchester City**: $\beta = 1.101$
3. **Brighton**: $\beta = 1.455$
4. **Nottingham Forest**: $\beta = 1.470$
5. **Manchester Utd**: $\beta = 1.473$

### Bottom 5 Defenses (Highest Conceded Expected Goals $\beta$)
1. **Sheffield Utd**: $\beta = 3.205$, $\alpha = 0.513$
2. **Luton**: $\beta = 2.728$, $\alpha = 0.765$
3. **Ipswich**: $\beta = 2.653$, $\alpha = 0.503$
4. **Southampton**: $\beta = 2.636$, $\alpha = 0.376$
5. **Leicester**: $\beta = 2.382$, $\alpha = 0.428$

*Note: All bottom 5 defensive ratings belong to promoted/relegated clubs that struggled defensively in the top flight, validating model calibration on real data.*

---

## 4. Real Matchup Smoke Tests

Using the fitted model (`data/models/dixon_coles_latest.pkl`), concrete predictions were evaluated across key fixtures:

| Fixture | $P(\text{Home Win})$ | $P(\text{Draw})$ | $P(\text{Away Win})$ | Most Likely Score | Outcome Sanity |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Manchester City vs Southampton** | **91.8%** | 6.8% | 1.5% | **3 - 0** | Heavy home favorite vs bottom-table defense |
| **Arsenal vs Luton** | **86.1%** | 10.1% | 3.8% | **3 - 0** | Heavy home favorite vs promoted team |
| **Manchester City vs Luton** | **86.5%** | 9.3% | 4.2% | **3 - 0** | Heavy home favorite vs promoted team |
| **Sheffield Utd vs Manchester City** | 3.2% | 8.8% | **87.9%** | **0 - 3** | Overwhelming away favorite |
| **Arsenal vs Tottenham** | **73.1%** | 19.2% | 7.7% | **2 - 0** | Top-table derby with strong home advantage |
| **Liverpool vs Everton** | **53.0%** | 25.3% | 21.7% | **1 - 1** | Competitive derby with draw as modal score |

---

## 5. Verification & Code Quality Status

- **Automated Tests**: **57 / 57 passed** in 5.27s (`uv run pytest`).
- **Linter**: `uv run ruff check .` passed with **0 errors**.
- **Type Checker**: `uv run mypy backend/ ml/` passed with **0 issues in 27 source files**.
- **Model Artifact**: Serialized to `data/models/dixon_coles_latest.pkl`.
- **Knowledge Graph**: Up to date (`graphify update .` completed with 481 nodes, 645 edges, 37 communities).
