"""Reliability diagrams and calibration metrics."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BinSummary:
    bin_lower: float
    bin_upper: float
    count: int
    mean_predicted: float
    observed_frequency: float
    gap: float


@dataclass(frozen=True)
class CalibrationResult:
    ece_home: float
    ece_draw: float
    ece_away: float
    ece_overall: float
    mce_home: float
    mce_draw: float
    mce_away: float
    tables: dict[str, list[BinSummary]]


def _compute_class_calibration(
    pred: np.ndarray, true: np.ndarray, n_bins: int = 10
) -> tuple[float, float, list[BinSummary]]:
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_summaries: list[BinSummary] = []
    n = len(pred)

    ece = 0.0
    mce = 0.0

    for m in range(n_bins):
        b_low = bin_edges[m]
        b_high = bin_edges[m + 1]

        if m == 0:
            mask = (pred >= b_low) & (pred <= b_high)
        else:
            mask = (pred > b_low) & (pred <= b_high)

        count = int(np.sum(mask))
        if count > 0:
            mean_pred = float(np.mean(pred[mask]))
            obs_freq = float(np.mean(true[mask]))
            gap = abs(obs_freq - mean_pred)
            ece += (count / n) * gap
            mce = max(mce, gap)
        else:
            mean_pred = (b_low + b_high) / 2.0
            obs_freq = 0.0
            gap = 0.0

        bin_summaries.append(
            BinSummary(
                bin_lower=float(b_low),
                bin_upper=float(b_high),
                count=count,
                mean_predicted=mean_pred,
                observed_frequency=obs_freq,
                gap=gap,
            )
        )

    return float(ece), float(mce), bin_summaries


def compute_calibration(
    probs: np.ndarray, outcomes: np.ndarray, n_bins: int = 10
) -> CalibrationResult:
    """Compute Expected Calibration Error and reliability tables across H/D/A outcomes."""
    probs = np.asarray(probs, dtype=float)
    outcomes = np.asarray(outcomes, dtype=float)

    ece_h, mce_h, table_h = _compute_class_calibration(probs[:, 0], outcomes[:, 0], n_bins)
    ece_d, mce_d, table_d = _compute_class_calibration(probs[:, 1], outcomes[:, 1], n_bins)
    ece_a, mce_a, table_a = _compute_class_calibration(probs[:, 2], outcomes[:, 2], n_bins)
    ece_overall = (ece_h + ece_d + ece_a) / 3.0

    return CalibrationResult(
        ece_home=ece_h,
        ece_draw=ece_d,
        ece_away=ece_a,
        ece_overall=float(ece_overall),
        mce_home=mce_h,
        mce_draw=mce_d,
        mce_away=mce_a,
        tables={"H": table_h, "D": table_d, "A": table_a},
    )
