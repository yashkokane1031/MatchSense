# Dixon-Coles Convergence Audit: Walk-Forward CV (114 Gameweek Refits)

## Audit Summary

| Metric | Value |
| :--- | :---: |
| **Total fits** | 114 |
| **Converged** | 92 (80.7%) |
| **Failed to converge** | **22 (19.3%)** |

### Per-Fold Breakdown

| Fold (Test Season) | Total Fits | Failures | Failure Rate | Avg Teams ($N$) | Avg `nfev` | Avg Elapsed |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **2023-24** (Fold 1) | 38 | **0** | **0.0%** | 26.0 | 6,861 | 0.955s |
| **2024-25** (Fold 2) | 38 | **9** | **23.7%** | 27.0 | 12,550 | 1.648s |
| **2025-26** (Fold 3) | 38 | **13** | **34.2%** | 27.0 | 11,703 | 1.638s |

> [!CAUTION]
> **22 out of 114 fits (19.3%) silently used non-converged parameters.** All 22 failures occur exclusively in 27-team windows (55 parameters) and cluster in the second half of each affected fold season. The code logs a warning but unconditionally accepts the partial result — predictions from these gameweeks came from a parameter vector that L-BFGS-B gave up on, not one it found the optimum for.

---

## Detailed Failure Map

All 22 failures share the same characteristics:
- `teams = 27`, `params = 55`
- `nfev = 15,008` (hit L-BFGS-B's default `maxfun` ceiling)
- `message = "STOP: TOTAL NO. OF F,G EVALUATIONS EXCEEDS LIMIT"`

### Fold 2 (2024-25): 9 failures

| Gameweek | `nit` | `nfev` | NLL | Reference Team | Elapsed |
| :---: | :---: | :---: | :---: | :--- | :---: |
| GW 17 | 244 | 15,008 | 615.60 | Manchester City | 1.93s |
| GW 28 | 241 | 15,008 | 712.10 | Aston Villa | 1.94s |
| GW 31 | 240 | 15,008 | 664.15 | Aston Villa | 1.94s |
| GW 33 | 248 | 15,008 | 683.15 | Aston Villa | 1.93s |
| GW 34 | 248 | 15,008 | 693.95 | Aston Villa | 1.91s |
| GW 35 | 240 | 15,008 | 686.13 | Aston Villa | 1.91s |
| GW 36 | 251 | 15,008 | 701.87 | Aston Villa | 1.92s |
| GW 37 | 240 | 15,008 | 711.32 | Arsenal | 2.02s |
| GW 38 | 243 | 15,064 | 708.16 | Arsenal | 2.16s |

### Fold 3 (2025-26): 13 failures

| Gameweek | `nit` | `nfev` | NLL | Reference Team | Elapsed |
| :---: | :---: | :---: | :---: | :--- | :---: |
| GW 25 | 242 | 15,008 | 673.61 | Arsenal | 1.93s |
| GW 27 | 243 | 15,008 | 692.53 | Arsenal | 1.93s |
| GW 28 | 242 | 15,008 | 686.63 | Arsenal | 1.99s |
| GW 29 | 248 | 15,008 | 690.11 | Arsenal | 1.96s |
| GW 30 | 245 | 15,008 | 712.10 | Arsenal | 1.96s |
| GW 31 | 256 | 15,008 | 699.63 | Arsenal | 1.99s |
| GW 32 | 248 | 15,008 | 642.10 | Arsenal | 1.94s |
| GW 33 | 241 | 15,008 | 655.90 | Everton | 2.03s |
| GW 34 | 243 | 15,008 | 664.08 | Chelsea | 1.95s |
| GW 35 | 241 | 15,008 | 660.17 | Arsenal | 1.94s |
| GW 36 | 237 | 15,008 | 678.18 | Everton | 1.94s |
| GW 37 | 238 | 15,008 | 674.61 | Aston Villa | 1.88s |
| GW 38 | 246 | 15,008 | 683.08 | Arsenal | 1.97s |

---

## Root Cause Analysis

1. **L-BFGS-B default `maxfun`**: For a 55-parameter problem, `scipy.optimize.minimize(method="L-BFGS-B")` defaults to `maxfun = 15 * len(x0) * (len(x0) + 1) / 2` which equals `15 * 55 * 56 / 2 = 23,100` — but in practice the code sets `maxiter=1000` and the effective `maxfun` default caps at ~15,000. All 22 failures hit exactly `nfev = 15,008`.

2. **Structural ill-conditioning in 27-team windows**: Windows containing 27 clubs have 5–7 clubs with only one season of top-flight fixtures (e.g. Luton, Sheffield United, Burnley, Ipswich, Southampton, Leicester). Their attack/defense parameters are supported by only ~38 highly time-decayed matches, creating near-flat directions in the log-likelihood surface that L-BFGS-B's line search struggles with.

3. **Cold-start initialization**: Every single refit starts from the same flat prior (`α = 1.0, β = 1.0, γ = 1.3, ρ = -0.05`) regardless of what the previous gameweek converged to. Since consecutive gameweeks shift the 1,520-match window by only ~10 matches, the true MLE parameters are nearly identical between adjacent gameweeks — but the optimizer has to rediscover them from scratch each time.

## Code Bug

```python
# ml/models/dixon_coles.py lines 312-321
if not result.success:
    logger.warning("Optimization did not converge: %s", result.message)  # ← logged
else:
    logger.info("Optimization converged in %d iterations", result.nit)

# ← UNCONDITIONAL: uses result.x whether converged or not
self._attack, self._defense, self._home_advantage, self._rho = (
    self._unpack_parameters(result.x)
)
self._is_fitted = True  # ← marked as fitted regardless
```

No exception, no retry, no flag stored, no way for `walk_forward.py` to detect the problem.

---

## Correlation with Fold-Level Performance Degradation

| Fold | Non-Convergence Rate | Dixon-Coles RPS | Accuracy |
| :--- | :---: | :---: | :---: |
| 2023-24 (0 failures) | 0.0% | **0.1905** | **57.6%** |
| 2024-25 (9 failures) | 23.7% | 0.2000 | 52.9% |
| 2025-26 (13 failures) | 34.2% | 0.2116 | 46.3% |

The pattern is consistent: the fold with zero non-convergence has the best metrics, and performance degrades monotonically with increasing failure rate. This does not prove causation (season difficulty could independently explain both), but it means the current results cannot rule out non-convergence as a contributing factor to the cross-fold degradation.
