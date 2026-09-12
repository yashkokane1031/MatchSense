"""Property-based tests for Poisson model properties.

Uses Hypothesis to verify mathematical invariants that must hold
for ANY valid team matchup, not just hand-picked test cases.
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from ml.models.dixon_coles import DixonColesModel, _tau


class TestPoissonProperties:
    """Property-based tests for Dixon-Coles model."""

    @given(
        lambda_=st.floats(min_value=0.5, max_value=3.0),
        mu=st.floats(min_value=0.5, max_value=3.0),
        rho=st.floats(min_value=-0.15, max_value=0.05),
    )
    @settings(max_examples=200)
    def test_tau_is_positive(self, lambda_: float, mu: float, rho: float):
        """τ must be positive for typical football scoring rates and empirical ρ."""
        for hg in range(2):
            for ag in range(2):
                result = _tau(hg, ag, lambda_, mu, rho)
                assert result > 0, (
                    f"τ({hg},{ag}, λ={lambda_:.3f}, μ={mu:.3f}, ρ={rho:.3f}) = {result}"
                )

    @given(
        lambda_=st.floats(min_value=0.1, max_value=5.0),
        mu=st.floats(min_value=0.1, max_value=5.0),
    )
    @settings(max_examples=100)
    def test_tau_is_one_for_high_scores(self, lambda_: float, mu: float):
        """τ must be exactly 1.0 for all scores where both teams score 2+."""
        for hg in range(2, 6):
            for ag in range(2, 6):
                assert _tau(hg, ag, lambda_, mu, -0.1) == 1.0

    def test_score_distribution_sums_to_one(self, fitted_model: DixonColesModel):
        """Score distribution must sum to ~1.0 for any valid matchup."""
        for home in fitted_model._teams[:3]:
            for away in [t for t in fitted_model._teams[:3] if t != home]:
                dist = fitted_model.predict_score_distribution(home, away)
                assert dist.sum() == pytest.approx(1.0, abs=0.02), (
                    f"{home} vs {away}: sum={dist.sum()}"
                )

    def test_probabilities_non_negative(self, fitted_model: DixonColesModel):
        """All probabilities must be >= 0."""
        for home in fitted_model._teams[:3]:
            for away in [t for t in fitted_model._teams[:3] if t != home]:
                dist = fitted_model.predict_score_distribution(home, away)
                assert (dist >= 0).all(), f"{home} vs {away}: negative probability found"

    def test_outcome_probs_sum_to_one(self, fitted_model: DixonColesModel):
        """P(H) + P(D) + P(A) must sum to ~1.0 for any matchup."""
        for home in fitted_model._teams[:3]:
            for away in [t for t in fitted_model._teams[:3] if t != home]:
                proba = fitted_model.predict_proba(home, away)
                total = proba["prob_home"] + proba["prob_draw"] + proba["prob_away"]
                assert total == pytest.approx(1.0, abs=0.02), (
                    f"{home} vs {away}: prob sum={total}"
                )

    def test_outcome_probs_in_valid_range(self, fitted_model: DixonColesModel):
        """Each probability must be in [0, 1]."""
        for home in fitted_model._teams[:3]:
            for away in [t for t in fitted_model._teams[:3] if t != home]:
                proba = fitted_model.predict_proba(home, away)
                for key in ["prob_home", "prob_draw", "prob_away"]:
                    assert 0 <= proba[key] <= 1, f"{home} vs {away}: {key}={proba[key]}"
