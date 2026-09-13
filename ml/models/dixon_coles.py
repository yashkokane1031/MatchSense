"""Dixon-Coles model for football match prediction.

Implements the Dixon & Coles (1997) extension to independent Poisson models:
- Per-team attack (alpha) and defense (beta) strengths
- Home advantage factor (gamma)
- Low-score correction parameter (rho) for 0-0, 0-1, 1-0, 1-1 scorelines
- Time-decay weighting so recent matches matter more

Identifiability: One team's alpha is fixed at 1.0 (reference team) and excluded
from the parameter vector. This avoids fighting the optimizer's gradient assumptions
with in-loop normalization.

Reference: Dixon, M. J. & Coles, S. G. (1997). Modelling association football
scores and inefficiencies in the football betting market.
"""

import logging
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import gammaln
from scipy.stats import poisson

from ml.models.base import BasePredictor

logger = logging.getLogger(__name__)


def _tau(
    home_goals: int, away_goals: int, lambda_: float, mu: float, rho: float
) -> float:
    """Dixon-Coles correction factor for low-scoring matches.

    Adjusts the joint probability P(X=x, Y=y) for scorelines where the
    independence assumption breaks down most severely.

    Args:
        home_goals: Goals scored by home team.
        away_goals: Goals scored by away team.
        lambda_: Expected goals for home team.
        mu: Expected goals for away team.
        rho: Correction parameter (typically small and negative).

    Returns:
        Multiplicative correction factor. Returns 1.0 for scorelines
        above 1-1 (no correction applied).
    """
    if home_goals == 0 and away_goals == 0:
        return 1.0 - lambda_ * mu * rho
    elif home_goals == 0 and away_goals == 1:
        return 1.0 + lambda_ * rho
    elif home_goals == 1 and away_goals == 0:
        return 1.0 + mu * rho
    elif home_goals == 1 and away_goals == 1:
        return 1.0 - rho
    else:
        return 1.0


def _time_decay_weights(dates: pd.Series, xi: float = 0.005) -> np.ndarray:
    """Compute exponential time-decay weights for each match.

    More recent matches receive higher weight. The decay rate xi controls
    how quickly old matches lose influence.

    Args:
        dates: Series of match dates.
        xi: Decay rate per day. Default 0.005 means a match 200 days ago
            has weight ~0.37 (1/e) relative to the most recent match.

    Returns:
        Array of weights, one per match, in [0, 1].
    """
    max_date = dates.max()
    days_ago = (max_date - dates).dt.days.values.astype(float)
    return np.exp(-xi * days_ago)


class DixonColesModel(BasePredictor):
    """Dixon-Coles model with time-decay weighting.

    Parameters are estimated via maximum likelihood using scipy.optimize.
    One team's attack strength is fixed at 1.0 for identifiability.
    """

    def __init__(self, xi: float = 0.005, allow_unknown: bool = False):
        """Initialize the model.

        Args:
            xi: Time-decay rate per day. Higher = more aggressive decay.
            allow_unknown: If True, unknown/newly promoted teams use empirical
                promoted priors (25th percentile attack, 75th percentile defense)
                instead of raising ValueError.
        """
        self.xi = xi
        self.allow_unknown = allow_unknown

        # Populated after fit()
        self._teams: list[str] = []
        self._team_to_idx: dict[str, int] = {}
        self._reference_team: str = ""
        self._attack: dict[str, float] = {}
        self._defense: dict[str, float] = {}
        self._home_advantage: float = 1.0
        self._rho: float = 0.0
        self._is_fitted: bool = False
        self._n_matches: int = 0
        self._fit_date: str = ""

        # Convergence diagnostics (populated after fit)
        self._converged: bool | None = None
        self._convergence_message: str = ""
        self._fit_nfev: int = 0
        self._fit_nit: int = 0
        self._fit_nll: float = float("inf")

        # Two-pass small-sample regularization diagnostics
        self._pass2_triggered: bool = False
        self._pass2_pinned: dict[str, dict[str, float]] = {}
        self._has_boundary_collapse: bool = False

    @property
    def model_name(self) -> str:
        return "dixon_coles"

    def _build_parameter_vector(self) -> np.ndarray:
        """Pack model parameters into a flat vector for the optimizer.

        Layout: [alpha_2, ..., alpha_N, beta_1, ..., beta_N, gamma, rho]
        Note: alpha_1 (reference team) is fixed at 1.0 and excluded.
        """
        # All attack params EXCEPT the reference team
        non_ref_teams = [t for t in self._teams if t != self._reference_team]
        alphas = [self._attack.get(t, 1.0) for t in non_ref_teams]
        betas = [self._defense.get(t, 1.0) for t in self._teams]
        return np.array(alphas + betas + [self._home_advantage, self._rho])

    def _unpack_parameters(
        self,
        params: np.ndarray,
        free_attack_indices: np.ndarray | None = None,
        free_defense_indices: np.ndarray | None = None,
        attack_template: np.ndarray | None = None,
        defense_template: np.ndarray | None = None,
    ) -> tuple[dict[str, float], dict[str, float], float, float]:
        """Unpack a flat parameter vector into named parameters.

        Supports standard (Pass 1) or reduced (Pass 2) parameter vectors.

        Returns:
            Tuple of (attack_dict, defense_dict, home_advantage, rho).
        """
        n = len(self._teams)
        if (
            free_attack_indices is None
            or free_defense_indices is None
            or attack_template is None
            or defense_template is None
        ):
            # Standard Pass 1 layout: (N-1) free alphas, N defenses, gamma, rho
            ref_idx = self._team_to_idx.get(self._reference_team, 0)
            non_ref_indices = np.array([i for i in range(n) if i != ref_idx], dtype=int)
            att = np.zeros(n, dtype=float)
            att[ref_idx] = 1.0
            n_free_att = n - 1
            att[non_ref_indices] = params[:n_free_att]
            defe = np.asarray(params[n_free_att : n_free_att + n], dtype=float)
            gamma = float(params[n_free_att + n])
            rho = float(params[n_free_att + n + 1])
        else:
            n_free_att = len(free_attack_indices)
            n_free_def = len(free_defense_indices)
            att = attack_template.copy()
            att[free_attack_indices] = params[:n_free_att]
            defe = defense_template.copy()
            defe[free_defense_indices] = params[n_free_att : n_free_att + n_free_def]
            gamma = float(params[-2])
            rho = float(params[-1])

        attack_dict = {team: float(att[i]) for i, team in enumerate(self._teams)}
        defense_dict = {team: float(defe[i]) for i, team in enumerate(self._teams)}
        return attack_dict, defense_dict, gamma, rho

    def _neg_log_likelihood(
        self,
        params: np.ndarray,
        home_indices: np.ndarray,
        away_indices: np.ndarray,
        home_goals: np.ndarray,
        away_goals: np.ndarray,
        weights: np.ndarray,
        free_attack_indices: np.ndarray,
        free_defense_indices: np.ndarray,
        attack_template: np.ndarray,
        defense_template: np.ndarray,
        mask_0_0: np.ndarray,
        mask_0_1: np.ndarray,
        mask_1_0: np.ndarray,
        mask_1_1: np.ndarray,
        log_fact_home: np.ndarray,
        log_fact_away: np.ndarray,
    ) -> float:
        """Vectorized negative log-likelihood (to minimize).

        L = -Σ w(t) * [log(τ) + log(Poisson(x;λ)) + log(Poisson(y;μ))]
        Supports arbitrary fixed parameters in attack_template and defense_template.
        """
        n_free_att = len(free_attack_indices)
        n_free_def = len(free_defense_indices)

        attack = attack_template.copy()
        attack[free_attack_indices] = params[:n_free_att]

        defense = defense_template.copy()
        defense[free_defense_indices] = params[n_free_att : n_free_att + n_free_def]

        gamma = params[-2]
        rho = params[-1]

        # Expected goals
        lambdas = attack[home_indices] * defense[away_indices] * gamma
        mus = attack[away_indices] * defense[home_indices]

        # Guard against non-positive rates
        if np.any(lambdas <= 0.0) or np.any(mus <= 0.0):
            return 1e10

        # Dixon-Coles low-score correction vector
        tau = np.ones(len(home_goals), dtype=float)
        if mask_0_0.any():
            tau[mask_0_0] = 1.0 - (lambdas[mask_0_0] * mus[mask_0_0] * rho)
        if mask_0_1.any():
            tau[mask_0_1] = 1.0 + (lambdas[mask_0_1] * rho)
        if mask_1_0.any():
            tau[mask_1_0] = 1.0 + (mus[mask_1_0] * rho)
        if mask_1_1.any():
            tau[mask_1_1] = 1.0 - rho

        # Guard against non-positive correction
        if np.any(tau <= 0.0):
            return 1e10

        # Vectorized log-likelihood: log(Poisson(k, mu)) = k*log(mu) - mu - gammaln(k+1)
        log_lik = np.sum(
            weights
            * (
                np.log(tau)
                + (home_goals * np.log(lambdas) - lambdas - log_fact_home)
                + (away_goals * np.log(mus) - mus - log_fact_away)
            )
        )

        return -float(log_lik)

    def get_warm_start_params(self) -> np.ndarray | None:
        """Return the current parameter vector for warm-starting a subsequent fit.

        Returns:
            Flat parameter vector if fitted, else None.
        """
        if not self._is_fitted:
            return None
        return self._build_parameter_vector()

    def fit(
        self,
        matches: pd.DataFrame,
        warm_start_params: np.ndarray | None = None,
    ) -> "DixonColesModel":
        """Fit the Dixon-Coles model on historical match data.

        Args:
            matches: DataFrame with columns: HomeTeam, AwayTeam, FTHG, FTAG, Date.
                Must be sorted by date.
            warm_start_params: Optional parameter vector from a prior fit to use
                as the initial guess. If the team set has changed, this is ignored
                and the flat prior is used instead.

        Returns:
            Self, for method chaining.
        """
        # Extract unique teams
        self._teams = sorted(set(matches["HomeTeam"]) | set(matches["AwayTeam"]))
        self._team_to_idx = {team: i for i, team in enumerate(self._teams)}
        n = len(self._teams)

        # Reference team: choose the one with the most matches (most stable estimate)
        team_match_counts = pd.concat([
            matches["HomeTeam"].value_counts(),
            matches["AwayTeam"].value_counts(),
        ]).groupby(level=0).sum()
        self._reference_team = str(team_match_counts.idxmax())
        logger.info("Reference team (alpha=1.0): %s (%d matches)",
                     self._reference_team, team_match_counts[self._reference_team])

        # Compute time-decay weights
        weights = _time_decay_weights(matches["Date"], self.xi)

        # Prepare vectorized data arrays and masks
        home_indices = np.array([self._team_to_idx[t] for t in matches["HomeTeam"].values], dtype=int)
        away_indices = np.array([self._team_to_idx[t] for t in matches["AwayTeam"].values], dtype=int)
        home_goals = np.asarray(matches["FTHG"].to_numpy(), dtype=float)
        away_goals = np.asarray(matches["FTAG"].to_numpy(), dtype=float)

        ref_idx = self._team_to_idx[self._reference_team]

        mask_0_0 = (home_goals == 0) & (away_goals == 0)
        mask_0_1 = (home_goals == 0) & (away_goals == 1)
        mask_1_0 = (home_goals == 1) & (away_goals == 0)
        mask_1_1 = (home_goals == 1) & (away_goals == 1)

        log_fact_home = gammaln(home_goals + 1.0)
        log_fact_away = gammaln(away_goals + 1.0)

        # Free parameters and templates for Pass 1:
        # Reference team alpha is fixed at 1.0; all other parameters are free.
        free_att_pass1 = np.array([i for i in range(n) if i != ref_idx], dtype=int)
        free_def_pass1 = np.array(range(n), dtype=int)
        att_tmpl_pass1 = np.zeros(n, dtype=float)
        att_tmpl_pass1[ref_idx] = 1.0
        def_tmpl_pass1 = np.zeros(n, dtype=float)

        n_free_alpha = len(free_att_pass1)
        n_params = n_free_alpha + len(free_def_pass1) + 2  # 2N+1

        use_warm_start = (
            warm_start_params is not None
            and len(warm_start_params) == n_params
        )
        if use_warm_start:
            initial_params = warm_start_params.copy()
            logger.info("Using warm-start from previous fit (%d params)", n_params)
        else:
            initial_params = np.concatenate([
                np.ones(n_free_alpha),        # attack (free teams)
                np.ones(len(free_def_pass1)), # defense (all teams)
                [1.3],                        # gamma (home advantage)
                [-0.05],                      # rho (Dixon-Coles correction)
            ])
            if warm_start_params is not None:
                logger.info(
                    "Warm-start params incompatible (got %d, need %d); using flat prior",
                    len(warm_start_params), n_params,
                )

        bounds_pass1 = (
            [(0.01, 5.0)] * n_free_alpha
            + [(0.01, 5.0)] * len(free_def_pass1)
            + [(0.5, 3.0)]
            + [(-1.0, 1.0)]
        )

        if use_warm_start:
            for i, (lo, hi) in enumerate(bounds_pass1):
                initial_params[i] = np.clip(initial_params[i], lo, hi)

        logger.info(
            "Fitting Dixon-Coles (Pass 1): %d teams, %d matches, %d parameters",
            n, len(matches), n_params,
        )

        opt_args_pass1 = (
            home_indices, away_indices, home_goals, away_goals, weights,
            free_att_pass1, free_def_pass1,
            att_tmpl_pass1, def_tmpl_pass1,
            mask_0_0, mask_0_1, mask_1_0, mask_1_1,
            log_fact_home, log_fact_away,
        )

        result = minimize(
            self._neg_log_likelihood,
            initial_params,
            args=opt_args_pass1,
            method="L-BFGS-B",
            bounds=bounds_pass1,
            options={"maxiter": 2000, "maxfun": 50000, "ftol": 1e-10},
        )

        if not result.success:
            logger.warning(
                "Pass 1 optimization did not converge (nfev=%d, nit=%d): %s. "
                "Retrying with doubled limits from current x.",
                result.nfev, result.nit, result.message,
            )
            result = minimize(
                self._neg_log_likelihood,
                result.x,
                args=opt_args_pass1,
                method="L-BFGS-B",
                bounds=bounds_pass1,
                options={"maxiter": 4000, "maxfun": 100000, "ftol": 1e-10},
            )

        self._converged = bool(result.success)
        self._convergence_message = (
            str(result.message) if not result.success else "converged"
        )
        self._fit_nfev = int(result.nfev)
        self._fit_nit = int(result.nit)
        self._fit_nll = float(result.fun)

        if not result.success:
            logger.warning(
                "Optimization did not converge after retry: %s "
                "(nfev=%d, nit=%d, NLL=%.2f)",
                result.message, result.nfev, result.nit, result.fun,
            )
        else:
            logger.info(
                "Pass 1 converged in %d iterations (%d f/g evals)",
                result.nit, result.nfev,
            )

        # Unpack Pass 1 parameters
        att_pass1 = att_tmpl_pass1.copy()
        att_pass1[free_att_pass1] = result.x[:len(free_att_pass1)]
        def_pass1 = def_tmpl_pass1.copy()
        def_pass1[free_def_pass1] = result.x[len(free_att_pass1) : len(free_att_pass1) + len(free_def_pass1)]
        gam_pass1 = float(result.x[-2])
        rho_pass1 = float(result.x[-1])

        # Small-sample boundary collapse detection:
        # If any team with < 5 matches collapsed to boundary (<= 0.15),
        # pin at empirical prior and run Pass 2 with reduced free parameter vector.
        established_att = [att_pass1[self._team_to_idx[t]] for t in self._teams if team_match_counts.get(t, 0) >= 10]
        established_def = [def_pass1[self._team_to_idx[t]] for t in self._teams if team_match_counts.get(t, 0) >= 10]
        p25_att = float(np.percentile(established_att, 25)) if established_att else 1.0
        p75_def = float(np.percentile(established_def, 75)) if established_def else 1.0

        pinned_att: dict[int, float] = {}
        pinned_def: dict[int, float] = {}
        for t in self._teams:
            cnt = team_match_counts.get(t, 0)
            if cnt < 5:
                idx = self._team_to_idx[t]
                if att_pass1[idx] <= 0.15:
                    pinned_att[idx] = p25_att
                    logger.info(
                        "Small-sample team '%s' attack collapsed (%.4f <= 0.15); pinning to empirical prior %.4f for Pass 2",
                        t, att_pass1[idx], p25_att,
                    )
                if def_pass1[idx] <= 0.15:
                    pinned_def[idx] = p75_def
                    logger.info(
                        "Small-sample team '%s' defense collapsed (%.4f <= 0.15); pinning to empirical prior %.4f for Pass 2",
                        t, def_pass1[idx], p75_def,
                    )

        if pinned_att or pinned_def:
            self._pass2_triggered = True
            self._pass2_pinned = {
                "attack": {self._teams[idx]: val for idx, val in pinned_att.items()},
                "defense": {self._teams[idx]: val for idx, val in pinned_def.items()},
            }

            free_att_pass2 = np.array([i for i in range(n) if i != ref_idx and i not in pinned_att], dtype=int)
            free_def_pass2 = np.array([i for i in range(n) if i not in pinned_def], dtype=int)

            att_tmpl_pass2 = np.zeros(n, dtype=float)
            att_tmpl_pass2[ref_idx] = 1.0
            for idx, val in pinned_att.items():
                att_tmpl_pass2[idx] = val

            def_tmpl_pass2 = np.zeros(n, dtype=float)
            for idx, val in pinned_def.items():
                def_tmpl_pass2[idx] = val

            init_pass2 = np.concatenate([
                att_pass1[free_att_pass2],
                def_pass1[free_def_pass2],
                [gam_pass1],
                [rho_pass1],
            ])
            bounds_pass2 = (
                [(0.01, 5.0)] * len(free_att_pass2)
                + [(0.01, 5.0)] * len(free_def_pass2)
                + [(0.5, 3.0)]
                + [(-1.0, 1.0)]
            )

            logger.info(
                "Starting Pass 2 joint re-optimization: %d free parameters (excluded %d pinned parameters)",
                len(init_pass2), len(pinned_att) + len(pinned_def),
            )

            opt_args_pass2 = (
                home_indices, away_indices, home_goals, away_goals, weights,
                free_att_pass2, free_def_pass2,
                att_tmpl_pass2, def_tmpl_pass2,
                mask_0_0, mask_0_1, mask_1_0, mask_1_1,
                log_fact_home, log_fact_away,
            )

            res2 = minimize(
                self._neg_log_likelihood,
                init_pass2,
                args=opt_args_pass2,
                method="L-BFGS-B",
                bounds=bounds_pass2,
                options={"maxiter": 2000, "maxfun": 50000, "ftol": 1e-10},
            )

            if not res2.success:
                logger.warning(
                    "Pass 2 optimization did not converge: %s. Retrying with doubled limits.",
                    res2.message,
                )
                res2 = minimize(
                    self._neg_log_likelihood,
                    res2.x,
                    args=opt_args_pass2,
                    method="L-BFGS-B",
                    bounds=bounds_pass2,
                    options={"maxiter": 4000, "maxfun": 100000, "ftol": 1e-10},
                )

            self._converged = bool(res2.success)
            self._convergence_message = (
                str(res2.message) if not res2.success else "converged"
            )
            self._fit_nfev += int(res2.nfev)
            self._fit_nit += int(res2.nit)
            self._fit_nll = float(res2.fun)

            final_att = att_tmpl_pass2.copy()
            final_att[free_att_pass2] = res2.x[:len(free_att_pass2)]
            final_def = def_tmpl_pass2.copy()
            final_def[free_def_pass2] = res2.x[len(free_att_pass2) : len(free_att_pass2) + len(free_def_pass2)]
            final_gamma = float(res2.x[-2])
            final_rho = float(res2.x[-1])

            delta_gamma = final_gamma - gam_pass1
            delta_rho = final_rho - rho_pass1
            logger.info(
                "Pass 2 joint re-optimization converged in %d iterations (%d evals). "
                "Shifts: home_advantage %.4f -> %.4f (%+.4f), rho %.4f -> %.4f (%+.4f)",
                res2.nit, res2.nfev, gam_pass1, final_gamma, delta_gamma, rho_pass1, final_rho, delta_rho,
            )
        else:
            final_att = att_pass1
            final_def = def_pass1
            final_gamma = gam_pass1
            final_rho = rho_pass1

        # Store unpacked parameter dictionaries
        self._attack = {team: float(final_att[i]) for i, team in enumerate(self._teams)}
        self._defense = {team: float(final_def[i]) for i, team in enumerate(self._teams)}
        self._home_advantage = final_gamma
        self._rho = final_rho
        self._is_fitted = True
        self._n_matches = len(matches)
        self._fit_date = str(matches["Date"].max().date())

        # Post-Pass 2 check: verify if any small-sample team still has boundary collapse
        persistent_collapse = []
        for t in self._teams:
            if team_match_counts.get(t, 0) < 5:
                if self._attack[t] <= 0.02 or self._defense[t] <= 0.02:
                    persistent_collapse.append(t)
        if persistent_collapse:
            self._has_boundary_collapse = True
            logger.warning(
                "Small-sample boundary collapse persisted after Pass 2 for teams: %s",
                persistent_collapse,
            )
        else:
            self._has_boundary_collapse = False

        logger.info(
            "Fitted: home_advantage=%.3f, rho=%.4f, converged=%s, pass2=%s",
            self._home_advantage, self._rho, self._converged, self._pass2_triggered,
        )

        return self

    def predict_proba(self, home_team: str, away_team: str) -> dict[str, float]:
        """Predict outcome probabilities for a match."""
        self._check_fitted()
        if not self.allow_unknown:
            self._check_teams(home_team, away_team)

        dist = self.predict_score_distribution(home_team, away_team)

        # Sum matrix regions
        prob_home = float(np.tril(dist, k=-1).sum())  # Below diagonal: home > away
        prob_draw = float(np.trace(dist))               # Diagonal: home == away
        prob_away = float(np.triu(dist, k=1).sum())    # Above diagonal: away > home

        # Guard against floating-point inaccuracies
        probs = np.array([prob_home, prob_draw, prob_away], dtype=float)
        probs = np.clip(probs, 0.0, 1.0)
        prob_sum = probs.sum()
        if prob_sum > 0:
            probs /= prob_sum

        return {
            "prob_home": float(probs[0]),
            "prob_draw": float(probs[1]),
            "prob_away": float(probs[2]),
        }

    def predict_score_distribution(
        self, home_team: str, away_team: str, max_goals: int = 8
    ) -> np.ndarray:
        """Predict the joint score probability distribution."""
        self._check_fitted()
        if not self.allow_unknown:
            self._check_teams(home_team, away_team)

        att_vals = list(self._attack.values())
        def_vals = list(self._defense.values())
        default_att = float(np.percentile(att_vals, 25)) if att_vals else 1.0
        default_def = float(np.percentile(def_vals, 75)) if def_vals else 1.0

        att_home = self._attack.get(home_team, default_att)
        def_away = self._defense.get(away_team, default_def)
        att_away = self._attack.get(away_team, default_att)
        def_home = self._defense.get(home_team, default_def)

        lambda_ = att_home * def_away * self._home_advantage
        mu = att_away * def_home

        # Build joint probability matrix with Dixon-Coles correction
        dist = np.zeros((max_goals + 1, max_goals + 1))
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                tau = max(0.0, _tau(i, j, lambda_, mu, self._rho))
                dist[i, j] = tau * poisson.pmf(i, lambda_) * poisson.pmf(j, mu)

        # Normalize to account for truncation at max_goals
        total = dist.sum()
        if total > 0:
            dist /= total
        else:
            # Fallback to independent Poisson if total <= 0
            for i in range(max_goals + 1):
                for j in range(max_goals + 1):
                    dist[i, j] = poisson.pmf(i, lambda_) * poisson.pmf(j, mu)
            dist /= dist.sum()

        return dist

    def get_team_strengths(self) -> dict[str, dict[str, float]]:
        """Return attack/defense strengths for all teams."""
        self._check_fitted()
        return {
            team: {"attack": self._attack[team], "defense": self._defense[team]}
            for team in self._teams
        }

    def get_model_info(self) -> dict:
        """Return metadata about the fitted model."""
        return {
            "model_name": self.model_name,
            "n_teams": len(self._teams),
            "n_matches": self._n_matches,
            "fit_date": self._fit_date,
            "home_advantage": self._home_advantage,
            "rho": self._rho,
            "xi": self.xi,
            "reference_team": self._reference_team,
            "is_fitted": self._is_fitted,
            "pass2_triggered": self._pass2_triggered,
            "has_boundary_collapse": self._has_boundary_collapse,
        }

    def save(self, path: str | Path) -> None:
        """Serialize the fitted model to disk.

        Args:
            path: File path to save to (typically .pkl).
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "teams": self._teams,
            "reference_team": self._reference_team,
            "attack": self._attack,
            "defense": self._defense,
            "home_advantage": self._home_advantage,
            "rho": self._rho,
            "xi": self.xi,
            "allow_unknown": self.allow_unknown,
            "n_matches": self._n_matches,
            "fit_date": self._fit_date,
            "pass2_triggered": self._pass2_triggered,
            "has_boundary_collapse": self._has_boundary_collapse,
        }
        with open(path, "wb") as f:
            pickle.dump(state, f)
        logger.info("Model saved to %s", path)

    @classmethod
    def load(cls, path: str | Path) -> "DixonColesModel":
        """Deserialize a fitted model from disk.

        Args:
            path: File path to load from.

        Returns:
            Fitted DixonColesModel instance.
        """
        with open(path, "rb") as f:
            state = pickle.load(f)

        model = cls(xi=state["xi"], allow_unknown=state.get("allow_unknown", False))
        model._teams = state["teams"]
        model._team_to_idx = {t: i for i, t in enumerate(model._teams)}
        model._reference_team = state["reference_team"]
        model._attack = state["attack"]
        model._defense = state["defense"]
        model._home_advantage = state["home_advantage"]
        model._rho = state["rho"]
        model._n_matches = state["n_matches"]
        model._fit_date = state["fit_date"]
        model._pass2_triggered = state.get("pass2_triggered", False)
        model._has_boundary_collapse = state.get("has_boundary_collapse", False)
        model._is_fitted = True

        logger.info("Model loaded from %s (%d teams, %d matches)",
                     path, len(model._teams), model._n_matches)
        return model

    def _check_fitted(self) -> None:
        """Raise if model has not been fitted."""
        if not self._is_fitted:
            raise RuntimeError("Model has not been fitted. Call fit() first.")

    def _check_teams(self, home_team: str, away_team: str) -> None:
        """Raise if either team is unknown."""
        for team in [home_team, away_team]:
            if team not in self._attack:
                known = ", ".join(sorted(self._teams))
                raise ValueError(
                    f"Unknown team '{team}'. Known teams: {known}"
                )
