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

    def _unpack_parameters(self, params: np.ndarray) -> tuple[
        dict[str, float], dict[str, float], float, float
    ]:
        """Unpack a flat parameter vector into named parameters.

        Returns:
            Tuple of (attack_dict, defense_dict, home_advantage, rho).
        """
        n = len(self._teams)
        n_free_alpha = n - 1  # One alpha is fixed

        non_ref_teams = [t for t in self._teams if t != self._reference_team]

        attack = {self._reference_team: 1.0}  # Fixed reference
        for i, team in enumerate(non_ref_teams):
            attack[team] = params[i]

        defense = {}
        for i, team in enumerate(self._teams):
            defense[team] = params[n_free_alpha + i]

        gamma = params[n_free_alpha + n]
        rho = params[n_free_alpha + n + 1]

        return attack, defense, gamma, rho

    def _neg_log_likelihood(
        self,
        params: np.ndarray,
        home_indices: np.ndarray,
        away_indices: np.ndarray,
        home_goals: np.ndarray,
        away_goals: np.ndarray,
        weights: np.ndarray,
        ref_idx: int,
        non_ref_indices: np.ndarray,
        mask_0_0: np.ndarray,
        mask_0_1: np.ndarray,
        mask_1_0: np.ndarray,
        mask_1_1: np.ndarray,
        log_fact_home: np.ndarray,
        log_fact_away: np.ndarray,
    ) -> float:
        """Vectorized negative log-likelihood (to minimize).

        L = -Σ w(t) * [log(τ) + log(Poisson(x;λ)) + log(Poisson(y;μ))]
        """
        n = len(self._teams)
        n_free_alpha = n - 1

        attack = np.empty(n, dtype=float)
        attack[ref_idx] = 1.0
        attack[non_ref_indices] = params[:n_free_alpha]

        defense = params[n_free_alpha : n_free_alpha + n]
        gamma = params[n_free_alpha + n]
        rho = params[n_free_alpha + n + 1]

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

    def fit(self, matches: pd.DataFrame) -> "DixonColesModel":
        """Fit the Dixon-Coles model on historical match data.

        Args:
            matches: DataFrame with columns: HomeTeam, AwayTeam, FTHG, FTAG, Date.
                Must be sorted by date.

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
        non_ref_teams = [t for t in self._teams if t != self._reference_team]
        non_ref_indices = np.array([self._team_to_idx[t] for t in non_ref_teams], dtype=int)

        mask_0_0 = (home_goals == 0) & (away_goals == 0)
        mask_0_1 = (home_goals == 0) & (away_goals == 1)
        mask_1_0 = (home_goals == 1) & (away_goals == 0)
        mask_1_1 = (home_goals == 1) & (away_goals == 1)

        log_fact_home = gammaln(home_goals + 1.0)
        log_fact_away = gammaln(away_goals + 1.0)

        # Initial parameters: all attack/defense at 1.0, gamma=1.3 (typical home advantage)
        n_free_alpha = n - 1
        initial_params = np.concatenate([
            np.ones(n_free_alpha),    # attack (free teams)
            np.ones(n),               # defense (all teams)
            [1.3],                    # gamma (home advantage)
            [-0.05],                  # rho (Dixon-Coles correction)
        ])

        # Parameter bounds
        bounds = (
            [(0.01, 5.0)] * n_free_alpha  # attack > 0
            + [(0.01, 5.0)] * n           # defense > 0
            + [(0.5, 3.0)]                # gamma (reasonable home advantage range)
            + [(-1.0, 1.0)]               # rho
        )

        logger.info(
            "Fitting Dixon-Coles: %d teams, %d matches, %d parameters",
            n, len(matches), len(initial_params),
        )

        result = minimize(
            self._neg_log_likelihood,
            initial_params,
            args=(
                home_indices,
                away_indices,
                home_goals,
                away_goals,
                weights,
                ref_idx,
                non_ref_indices,
                mask_0_0,
                mask_0_1,
                mask_1_0,
                mask_1_1,
                log_fact_home,
                log_fact_away,
            ),
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": 1000, "ftol": 1e-10},
        )

        if not result.success:
            logger.warning("Optimization did not converge: %s", result.message)
        else:
            logger.info("Optimization converged in %d iterations", result.nit)

        # Unpack fitted parameters
        self._attack, self._defense, self._home_advantage, self._rho = (
            self._unpack_parameters(result.x)
        )
        self._is_fitted = True
        self._n_matches = len(matches)
        self._fit_date = str(matches["Date"].max().date())

        logger.info(
            "Fitted: home_advantage=%.3f, rho=%.4f",
            self._home_advantage, self._rho,
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
