"""Mathematical evaluation metrics for football match prediction."""

import numpy as np


def compute_rps(probs: np.ndarray, outcomes: np.ndarray) -> np.ndarray:
    """Compute Ranked Probability Score for 3-outcome ordered events (H < D < A).

    RPS = 0.5 * [(p_H - y_H)^2 + ((p_H + p_D) - (y_H + y_D))^2]

    Args:
        probs: Array of shape (N, 3) with probabilities for [H, D, A].
        outcomes: One-hot array of shape (N, 3) with actual outcomes for [H, D, A].

    Returns:
        Array of shape (N,) with RPS values in [0, 1].
    """
    probs = np.asarray(probs, dtype=float)
    outcomes = np.asarray(outcomes, dtype=float)

    # Cumulative probabilities
    p_h = probs[:, 0]
    p_hd = p_h + probs[:, 1]

    # Cumulative outcomes
    y_h = outcomes[:, 0]
    y_hd = y_h + outcomes[:, 1]

    # RPS = 0.5 * [(p_H - y_H)^2 + (p_HD - y_HD)^2]
    rps = 0.5 * ((p_h - y_h) ** 2 + (p_hd - y_hd) ** 2)
    return rps


def compute_brier_score(probs: np.ndarray, outcomes: np.ndarray) -> np.ndarray:
    """Compute multi-category Brier score.

    Args:
        probs: Array of shape (N, 3).
        outcomes: One-hot array of shape (N, 3).

    Returns:
        Array of shape (N,) with Brier scores in [0, 2].
    """
    probs = np.asarray(probs, dtype=float)
    outcomes = np.asarray(outcomes, dtype=float)
    return np.sum((probs - outcomes) ** 2, axis=1)


def compute_log_loss(
    probs: np.ndarray, outcomes: np.ndarray, eps: float = 1e-15
) -> np.ndarray:
    """Compute multi-class cross-entropy log-loss.

    Args:
        probs: Array of shape (N, 3).
        outcomes: One-hot array of shape (N, 3).
        eps: Boundary clipping parameter.

    Returns:
        Array of shape (N,) with log-loss values.
    """
    probs = np.clip(np.asarray(probs, dtype=float), eps, 1.0 - eps)
    outcomes = np.asarray(outcomes, dtype=float)
    return -np.sum(outcomes * np.log(probs), axis=1)


def compute_accuracy(probs: np.ndarray, outcomes: np.ndarray) -> np.ndarray:
    """Compute binary classification correctness.

    Args:
        probs: Array of shape (N, 3).
        outcomes: One-hot array of shape (N, 3).

    Returns:
        Integer array of shape (N,) with 1 for correct, 0 for incorrect.
    """
    pred_classes = np.argmax(np.asarray(probs), axis=1)
    true_classes = np.argmax(np.asarray(outcomes), axis=1)
    return (pred_classes == true_classes).astype(int)
