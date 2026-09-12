"""Unit tests for calibration and expected calibration error (ECE)."""

import numpy as np
import pytest

from ml.evaluation.calibration import compute_calibration


def test_perfect_calibration():
    """Synthesized well-calibrated distribution should have low ECE."""
    np.random.seed(42)
    p = np.random.uniform(0.1, 0.9, 2000)
    y = (np.random.uniform(0, 1, 2000) < p).astype(int)
    probs = np.column_stack([p, (1 - p) / 2, (1 - p) / 2])
    outcomes = np.column_stack([y, np.zeros(2000), 1 - y])

    res = compute_calibration(probs, outcomes, n_bins=5)
    assert res.ece_home < 0.06  # Close to 0 with finite sample noise
    assert len(res.tables["H"]) == 5


def test_extreme_miscalibration():
    """Predicting 0.95 when actual frequency is 0.0 should have ECE and MCE approx 0.95."""
    probs = np.array([[0.95, 0.025, 0.025]] * 100)
    outcomes = np.array([[0, 1, 0]] * 100)
    res = compute_calibration(probs, outcomes, n_bins=10)
    assert res.ece_home == pytest.approx(0.95, abs=0.01)
    assert res.mce_home == pytest.approx(0.95, abs=0.01)


def test_empty_bins_handled_gracefully():
    """Bins with 0 counts should not cause division by zero."""
    probs = np.array([[0.2, 0.5, 0.3], [0.25, 0.45, 0.3]])
    outcomes = np.array([[1, 0, 0], [0, 1, 0]])
    res = compute_calibration(probs, outcomes, n_bins=10)
    assert res.ece_overall >= 0.0
    assert len(res.tables["H"]) == 10
