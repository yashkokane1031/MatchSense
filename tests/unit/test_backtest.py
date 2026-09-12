"""Unit tests for financial backtesting and staking simulator."""

import pandas as pd
import pytest

from ml.evaluation.backtest import simulate_betting


@pytest.fixture
def sample_betting_df():
    """Create deterministic fixture dataset across 2 gameweeks."""
    return pd.DataFrame([
        # GW 1: Match 1 - model sees EV on Home: 0.60 * 2.0 - 1 = +0.20 (win: +1.0 unit)
        {
            "Season": "2023-24",
            "Gameweek": 1,
            "Date": "2023-08-12",
            "prob_home": 0.60,
            "prob_draw": 0.25,
            "prob_away": 0.15,
            "AvgH": 2.0,
            "AvgD": 3.4,
            "AvgA": 4.5,
            "FTR": "H",
        },
        # GW 1: Match 2 - model sees EV on Away: 0.40 * 3.0 - 1 = +0.20 (loss: -1.0 unit)
        {
            "Season": "2023-24",
            "Gameweek": 1,
            "Date": "2023-08-12",
            "prob_home": 0.30,
            "prob_draw": 0.30,
            "prob_away": 0.40,
            "AvgH": 2.5,
            "AvgD": 3.2,
            "AvgA": 3.0,
            "FTR": "H",
        },
        # GW 2: Match 3 - EV strictly below 0.05 threshold (no bet)
        {
            "Season": "2023-24",
            "Gameweek": 2,
            "Date": "2023-08-19",
            "prob_home": 0.50,
            "prob_draw": 0.30,
            "prob_away": 0.20,
            "AvgH": 2.0,
            "AvgD": 3.0,
            "AvgA": 4.0,
            "FTR": "H",
        },
    ])


def test_flat_betting_execution(sample_betting_df):
    """Flat staking should place exactly 1.0 unit per qualifying bet."""
    res = simulate_betting(
        sample_betting_df,
        odds_col_prefix="Avg",
        edge_threshold=0.05,
        staking="flat",
    )
    assert res.total_bets == 2
    # Bet 1 won at 2.0 odds -> +1.0 unit PnL
    # Bet 2 lost -> -1.0 unit PnL
    assert res.net_pnl == pytest.approx(0.0)
    assert res.turnover == pytest.approx(2.0)
    assert res.roi == pytest.approx(0.0)
    assert res.win_rate == pytest.approx(0.5)


def test_quarter_kelly_sizing(sample_betting_df):
    """Quarter-Kelly scales bet sizes by EV / (o - 1) with caps."""
    res = simulate_betting(
        sample_betting_df,
        odds_col_prefix="Avg",
        edge_threshold=0.05,
        staking="quarter_kelly",
        initial_bankroll=100.0,
    )
    assert res.total_bets == 2
    assert res.turnover > 0.0
    # Both bets in GW 1 had EV=0.20
    # Bet 1: odds 2.0 -> f* = 0.20 / 1.0 = 0.20 -> 0.25 * 0.20 * 100 = 5.0 (capped at 5.0)
    # Bet 2: odds 3.0 -> f* = 0.20 / 2.0 = 0.10 -> 0.25 * 0.10 * 100 = 2.5
    # Total GW stake = 7.5 <= 25.0 cap (no scaling)
    # PnL: Bet 1 +5.0, Bet 2 -2.5 -> Net PnL = +2.5
    assert res.net_pnl == pytest.approx(2.5)


def test_single_outcome_conflict_guard():
    """If model sees EV on multiple outcomes, must select only the argmax EV."""
    df = pd.DataFrame([
        {
            "Gameweek": 1,
            "Date": "2023-08-12",
            "prob_home": 0.20,
            "prob_draw": 0.40,
            "prob_away": 0.40,
            "AvgH": 3.0,
            "AvgD": 3.0,  # EV = 0.40 * 3.0 - 1 = +0.20
            "AvgA": 3.5,  # EV = 0.40 * 3.5 - 1 = +0.40 (larger EV)
            "FTR": "A",
        }
    ])
    res = simulate_betting(df, odds_col_prefix="Avg", edge_threshold=0.05, staking="flat")
    assert res.total_bets == 1
    assert res.history.iloc[0]["outcome"] == "A"
    assert bool(res.history.iloc[0]["won"]) is True
