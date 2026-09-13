"""Tests for the Dixon-Coles model.

Covers: tau correction, parameter packing, model fitting, prediction
properties, serialization, and reference-team constraint.
"""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ml.models.dixon_coles import DixonColesModel, _tau


class TestTauCorrection:
    """Test the Dixon-Coles low-score correction function."""

    def test_tau_0_0(self):
        """0-0: correction depends on lambda, mu, rho."""
        result = _tau(0, 0, 1.5, 1.2, -0.1)
        expected = 1.0 - 1.5 * 1.2 * (-0.1)
        assert result == pytest.approx(expected)

    def test_tau_0_1(self):
        """0-1: correction depends on lambda and rho."""
        result = _tau(0, 1, 1.5, 1.2, -0.1)
        expected = 1.0 + 1.5 * (-0.1)
        assert result == pytest.approx(expected)

    def test_tau_1_0(self):
        """1-0: correction depends on mu and rho."""
        result = _tau(1, 0, 1.5, 1.2, -0.1)
        expected = 1.0 + 1.2 * (-0.1)
        assert result == pytest.approx(expected)

    def test_tau_1_1(self):
        """1-1: correction is 1 - rho."""
        result = _tau(1, 1, 1.5, 1.2, -0.1)
        expected = 1.0 - (-0.1)
        assert result == pytest.approx(expected)

    def test_tau_other_scores_return_1(self):
        """All scores > 1-1 get no correction."""
        for hg, ag in [(2, 0), (0, 2), (2, 1), (3, 3), (5, 0)]:
            assert _tau(hg, ag, 1.5, 1.2, -0.1) == 1.0

    def test_tau_positive_for_typical_rho(self):
        """Tau should be positive for typical rho values."""
        for rho in [-0.3, -0.1, 0.0, 0.1]:
            for hg in range(2):
                for ag in range(2):
                    result = _tau(hg, ag, 1.5, 1.0, rho)
                    assert result > 0, f"tau({hg},{ag}) = {result} for rho={rho}"


class TestDixonColesModel:
    """Test model fitting and prediction on sample data."""

    def test_fit_returns_self(self, sample_matches):
        """fit() should return self for method chaining."""
        model = DixonColesModel(xi=0.005)
        result = model.fit(sample_matches)
        assert result is model

    def test_fit_sets_teams(self, fitted_model, sample_matches):
        """After fitting, model should know all teams from the data."""
        expected_teams = sorted(
            set(sample_matches["HomeTeam"]) | set(sample_matches["AwayTeam"])
        )
        assert fitted_model._teams == expected_teams

    def test_reference_team_alpha_is_one(self, fitted_model):
        """The reference team's attack strength must be exactly 1.0."""
        ref_team = fitted_model._reference_team
        assert fitted_model._attack[ref_team] == 1.0

    def test_home_advantage_positive(self, fitted_model):
        """Home advantage (gamma) should be > 1.0 (home teams score more)."""
        assert fitted_model._home_advantage > 1.0

    def test_probabilities_sum_to_one(self, fitted_model):
        """Outcome probabilities must sum to ~1.0."""
        proba = fitted_model.predict_proba("Arsenal", "Chelsea")
        total = proba["prob_home"] + proba["prob_draw"] + proba["prob_away"]
        assert total == pytest.approx(1.0, abs=0.01)

    def test_score_distribution_shape(self, fitted_model):
        """Score distribution should be (max_goals+1, max_goals+1)."""
        dist = fitted_model.predict_score_distribution("Arsenal", "Chelsea", max_goals=6)
        assert dist.shape == (7, 7)

    def test_score_distribution_sums_to_one(self, fitted_model):
        """Score distribution should sum to ~1.0 after normalization."""
        dist = fitted_model.predict_score_distribution("Arsenal", "Chelsea")
        assert dist.sum() == pytest.approx(1.0, abs=0.01)

    def test_score_distribution_non_negative(self, fitted_model):
        """All score probabilities must be >= 0."""
        dist = fitted_model.predict_score_distribution("Arsenal", "Chelsea")
        assert (dist >= 0).all()

    def test_predict_most_likely_score(self, fitted_model):
        """Most likely score should be reasonable (not negative, not absurd)."""
        home, away = fitted_model.predict_most_likely_score("Arsenal", "Chelsea")
        assert 0 <= home <= 5
        assert 0 <= away <= 5

    def test_unknown_team_raises(self, fitted_model):
        """Predicting with unknown team should raise ValueError when allow_unknown=False."""
        with pytest.raises(ValueError, match="Unknown team"):
            fitted_model.predict_proba("Arsenal", "Nonexistent FC")

    def test_allow_unknown_team(self, sample_matches):
        """Predicting with unknown team should succeed when allow_unknown=True."""
        model = DixonColesModel(allow_unknown=True)
        model.fit(sample_matches)
        probs = model.predict_proba("Arsenal", "Nonexistent FC")
        assert pytest.approx(sum(probs.values()), abs=1e-5) == 1.0
        assert probs["prob_home"] > probs["prob_away"]

    def test_unfitted_model_raises(self):
        """Predicting without fit() should raise RuntimeError."""
        model = DixonColesModel()
        with pytest.raises(RuntimeError, match="not been fitted"):
            model.predict_proba("Arsenal", "Chelsea")

    def test_serialization_roundtrip(self, fitted_model):
        """Save and load should produce identical predictions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_model.pkl"
            fitted_model.save(path)

            loaded = DixonColesModel.load(path)

            # Compare predictions
            orig = fitted_model.predict_proba("Arsenal", "Liverpool")
            loaded_pred = loaded.predict_proba("Arsenal", "Liverpool")

            assert orig["prob_home"] == pytest.approx(loaded_pred["prob_home"], abs=1e-6)
            assert orig["prob_draw"] == pytest.approx(loaded_pred["prob_draw"], abs=1e-6)
            assert orig["prob_away"] == pytest.approx(loaded_pred["prob_away"], abs=1e-6)

    def test_get_team_strengths(self, fitted_model):
        """get_team_strengths() should return dict for all teams."""
        strengths = fitted_model.get_team_strengths()
        assert len(strengths) == len(fitted_model._teams)
        for team, s in strengths.items():
            assert "attack" in s
            assert "defense" in s
            assert s["attack"] > 0
            assert s["defense"] > 0

    def test_model_info(self, fitted_model):
        """get_model_info() should return expected metadata."""
        info = fitted_model.get_model_info()
        assert info["model_name"] == "dixon_coles"
        assert info["is_fitted"] is True
        assert info["n_teams"] == len(fitted_model._teams)
        assert info["n_matches"] == 20


class TestMediumScaleConvergence:
    """Test model convergence at realistic scale.

    This catches optimization bugs that pass on 5-team/20-match data
    but fail silently at scale.
    """

    @pytest.fixture
    def medium_dataset(self) -> pd.DataFrame:
        """Generate a synthetic 25-team, 500-match dataset."""
        rng = np.random.default_rng(42)
        teams = [f"Team_{i:02d}" for i in range(25)]
        rows = []

        for _ in range(500):
            ht = rng.choice(teams)
            at = rng.choice([t for t in teams if t != ht])
            hg = rng.poisson(1.4)  # Home team slight advantage
            ag = rng.poisson(1.1)
            result = "H" if hg > ag else ("D" if hg == ag else "A")
            rows.append({
                "Date": pd.Timestamp("2024-01-01") + pd.Timedelta(days=int(rng.integers(0, 300))),
                "HomeTeam": ht,
                "AwayTeam": at,
                "FTHG": int(hg),
                "FTAG": int(ag),
                "FTR": result,
                "Season": "2024-25",
            })

        return pd.DataFrame(rows).sort_values("Date").reset_index(drop=True)

    def test_converges_at_scale(self, medium_dataset):
        """Model should converge on 25-team, 500-match dataset."""
        model = DixonColesModel(xi=0.005)
        model.fit(medium_dataset)

        # Probabilities should still sum to 1
        proba = model.predict_proba("Team_00", "Team_01")
        total = proba["prob_home"] + proba["prob_draw"] + proba["prob_away"]
        assert total == pytest.approx(1.0, abs=0.02)

        # All attack/defense params should be positive and finite
        for team, s in model.get_team_strengths().items():
            assert 0 < s["attack"] < 10, f"{team} attack out of range: {s['attack']}"
            assert 0 < s["defense"] < 10, f"{team} defense out of range: {s['defense']}"


class TestTwoPassSmallSampleRegularization:
    """Test two-pass joint optimization with parameter exclusion for small-sample boundary collapse."""

    @pytest.fixture
    def base_matches(self) -> pd.DataFrame:
        """Create a stable base dataset of 6 teams with 15 matches each."""
        rng = np.random.default_rng(123)
        teams = ["Arsenal", "Chelsea", "Liverpool", "ManCity", "Tottenham", "Newcastle"]
        rows = []
        for i in range(90):
            ht = rng.choice(teams)
            at = rng.choice([t for t in teams if t != ht])
            hg = rng.integers(1, 4)
            ag = rng.integers(0, 3)
            rows.append({
                "Date": pd.Timestamp("2024-01-01") + pd.Timedelta(days=i),
                "HomeTeam": ht,
                "AwayTeam": at,
                "FTHG": int(hg),
                "FTAG": int(ag),
                "FTR": "H" if hg > ag else ("D" if hg == ag else "A"),
                "Season": "2024-25",
            })
        return pd.DataFrame(rows)

    def test_two_pass_triggered_on_boundary_collapse(self, base_matches):
        """When a team with <5 matches scores 0 goals, Pass 2 is triggered with parameter exclusion."""
        # Add Coventry with 2 matches and 0 goals scored
        coventry_matches = pd.DataFrame([
            {"Date": pd.Timestamp("2024-04-01"), "HomeTeam": "Arsenal", "AwayTeam": "Coventry", "FTHG": 2, "FTAG": 0, "FTR": "H", "Season": "2024-25"},
            {"Date": pd.Timestamp("2024-04-05"), "HomeTeam": "Coventry", "AwayTeam": "Chelsea", "FTHG": 0, "FTAG": 1, "FTR": "A", "Season": "2024-25"},
        ])
        full_df = pd.concat([base_matches, coventry_matches], ignore_index=True).sort_values("Date")

        model = DixonColesModel(xi=0.005)
        model.fit(full_df)

        assert model._pass2_triggered is True
        assert "Coventry" in model._pass2_pinned["attack"]
        pinned_prior = model._pass2_pinned["attack"]["Coventry"]
        assert model._attack["Coventry"] == pytest.approx(pinned_prior)
        assert model._has_boundary_collapse is False

        # Verify predictions work and sum to 1
        probs = model.predict_proba("Coventry", "Arsenal")
        assert sum(probs.values()) == pytest.approx(1.0)

    def test_multi_team_simultaneous_collapse_on_same_side(self, base_matches):
        """Multiple small-sample teams collapsing on the same side (attack) are all pinned simultaneously in Pass 2."""
        new_matches = pd.DataFrame([
            {"Date": pd.Timestamp("2024-04-01"), "HomeTeam": "Arsenal", "AwayTeam": "Promoted_A", "FTHG": 3, "FTAG": 0, "FTR": "H", "Season": "2024-25"},
            {"Date": pd.Timestamp("2024-04-02"), "HomeTeam": "Promoted_A", "AwayTeam": "Chelsea", "FTHG": 0, "FTAG": 2, "FTR": "A", "Season": "2024-25"},
            {"Date": pd.Timestamp("2024-04-03"), "HomeTeam": "Liverpool", "AwayTeam": "Promoted_B", "FTHG": 1, "FTAG": 0, "FTR": "H", "Season": "2024-25"},
            {"Date": pd.Timestamp("2024-04-04"), "HomeTeam": "Promoted_B", "AwayTeam": "ManCity", "FTHG": 0, "FTAG": 4, "FTR": "A", "Season": "2024-25"},
        ])
        full_df = pd.concat([base_matches, new_matches], ignore_index=True).sort_values("Date")

        model = DixonColesModel(xi=0.005)
        model.fit(full_df)

        assert model._pass2_triggered is True
        assert "Promoted_A" in model._pass2_pinned["attack"]
        assert "Promoted_B" in model._pass2_pinned["attack"]
        assert model._attack["Promoted_A"] == pytest.approx(model._pass2_pinned["attack"]["Promoted_A"])
        assert model._attack["Promoted_B"] == pytest.approx(model._pass2_pinned["attack"]["Promoted_B"])

        # Model converged and produces valid probabilities
        assert model._converged is True
        probs_a = model.predict_proba("Promoted_A", "Promoted_B")
        assert sum(probs_a.values()) == pytest.approx(1.0)

    def test_no_pass2_when_no_collapse(self, base_matches):
        """Pass 2 is not triggered when all teams have normal scoring or sufficient sample size."""
        model = DixonColesModel(xi=0.005)
        model.fit(base_matches)

        assert model._pass2_triggered is False
        assert len(model._pass2_pinned) == 0
        assert model._has_boundary_collapse is False

