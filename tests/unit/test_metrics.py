"""Unit tests for probabilistic and categorical evaluation metrics."""

import numpy as np
import pytest

from ml.evaluation.metrics import (
    compute_accuracy,
    compute_brier_score,
    compute_log_loss,
    compute_rps,
)


def test_rps_perfect_prediction():
    """Certain home win prediction when home win occurs should give RPS = 0."""
    probs = np.array([[1.0, 0.0, 0.0]])
    outcomes = np.array([[1, 0, 0]])
    rps = compute_rps(probs, outcomes)
    assert rps[0] == pytest.approx(0.0)


def test_rps_worst_case_prediction():
    """Certain away win prediction when home win occurs should give maximum RPS = 1."""
    probs = np.array([[0.0, 0.0, 1.0]])
    outcomes = np.array([[1, 0, 0]])
    rps = compute_rps(probs, outcomes)
    assert rps[0] == pytest.approx(1.0)


def test_rps_adjacent_error_less_than_severe():
    """Predicting Draw when Home wins should give lower RPS penalty than predicting Away."""
    outcomes = np.array([[1, 0, 0]])
    rps_draw = compute_rps(np.array([[0.0, 1.0, 0.0]]), outcomes)[0]
    rps_away = compute_rps(np.array([[0.0, 0.0, 1.0]]), outcomes)[0]
    assert rps_draw < rps_away


def test_rps_vectorized_shape():
    """RPS should handle 2D batch arrays correctly."""
    probs = np.array([
        [0.6, 0.3, 0.1],
        [0.2, 0.5, 0.3],
        [0.1, 0.2, 0.7],
    ])
    outcomes = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ])
    rps = compute_rps(probs, outcomes)
    assert rps.shape == (3,)
    assert np.all(rps >= 0.0)
    assert np.all(rps <= 1.0)


def test_brier_score_range():
    """Multi-category Brier score ranges from 0.0 to 2.0."""
    probs = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    outcomes = np.array([[1, 0, 0], [1, 0, 0]])
    brier = compute_brier_score(probs, outcomes)
    assert brier[0] == pytest.approx(0.0)
    assert brier[1] == pytest.approx(2.0)


def test_log_loss_clipping():
    """Log loss clips probabilities to prevent -inf log(0)."""
    probs = np.array([[0.0, 1.0, 0.0]])
    outcomes = np.array([[1, 0, 0]])
    loss = compute_log_loss(probs, outcomes, eps=1e-15)
    assert loss[0] > 30.0  # -ln(1e-15) ~ 34.5


def test_accuracy_argmax():
    """Accuracy evaluates whether argmax matches true class."""
    probs = np.array([
        [0.6, 0.3, 0.1],
        [0.2, 0.5, 0.3],
    ])
    outcomes = np.array([
        [1, 0, 0],
        [1, 0, 0],
    ])
    acc = compute_accuracy(probs, outcomes)
    assert acc[0] == 1
    assert acc[1] == 0
