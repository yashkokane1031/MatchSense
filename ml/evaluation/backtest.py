"""Financial backtesting engine with pre-gameweek batch staking."""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BacktestResult:
    total_bets: int
    bet_frequency: float
    turnover: float
    net_pnl: float
    roi: float
    win_rate: float
    max_drawdown_units: float
    max_drawdown_pct: float
    annualized_sharpe: float
    per_bet_sharpe: float
    history: pd.DataFrame


def simulate_betting(
    df: pd.DataFrame,
    odds_col_prefix: str = "Avg",
    edge_threshold: float = 0.05,
    staking: str = "flat",
    initial_bankroll: float = 100.0,
) -> BacktestResult:
    """Run financial backtest with gameweek batch sizing and conflict guards.

    Args:
        df: DataFrame containing Gameweek, prob_home, prob_draw, prob_away,
            {prefix}H, {prefix}D, {prefix}A, FTR.
        odds_col_prefix: 'Avg' or 'B365'.
        edge_threshold: Minimum expected value (p * odds - 1).
        staking: 'flat' or 'quarter_kelly'.
        initial_bankroll: Starting bankroll units.

    Returns:
        BacktestResult containing summary metrics and bet history.
    """
    col_h = f"{odds_col_prefix}H"
    col_d = f"{odds_col_prefix}D"
    col_a = f"{odds_col_prefix}A"

    bankroll = float(initial_bankroll)
    peak_bankroll = bankroll
    max_dd_units = 0.0
    max_dd_pct = 0.0

    bet_records: list[dict] = []
    gameweek_returns: list[float] = []

    # Sort chronologically by gameweek/date
    sort_cols = [c for c in ["Season", "Gameweek", "Date"] if c in df.columns]
    if sort_cols:
        df = df.sort_values(sort_cols)

    group_keys = ["Season", "Gameweek"] if "Season" in df.columns else ["Gameweek"]
    grouped = df.groupby(group_keys if len(group_keys) > 1 else group_keys[0], sort=False)

    for _, gw_matches in grouped:
        gw_pre_bankroll = bankroll
        gw_bets: list[dict] = []

        for _, row in gw_matches.iterrows():
            odds = {
                "H": float(row[col_h]),
                "D": float(row[col_d]),
                "A": float(row[col_a]),
            }
            probs = {
                "H": float(row["prob_home"]),
                "D": float(row["prob_draw"]),
                "A": float(row["prob_away"]),
            }

            # Calculate EV: p * o - 1
            evs = {c: probs[c] * odds[c] - 1.0 for c in ["H", "D", "A"]}
            best_outcome = max(evs, key=lambda c: evs[c])
            max_ev = evs[best_outcome]

            if max_ev >= edge_threshold:
                best_odds = odds[best_outcome]
                best_prob = probs[best_outcome]

                if staking == "flat":
                    raw_stake = 1.0
                elif staking == "quarter_kelly":
                    denom = max(1e-4, best_odds - 1.0)
                    f_star = max_ev / denom
                    # Quarter Kelly with 5% max bankroll cap per bet
                    raw_stake = min(0.25 * f_star * gw_pre_bankroll, 0.05 * gw_pre_bankroll)
                    raw_stake = max(0.0, raw_stake)
                else:
                    raise ValueError(f"Unknown staking strategy: {staking}")

                gw_bets.append({
                    "outcome": best_outcome,
                    "odds": best_odds,
                    "prob": best_prob,
                    "ev": max_ev,
                    "raw_stake": raw_stake,
                    "actual": str(row["FTR"]),
                })

        # Apply 25% Gameweek Exposure Cap strictly to Quarter-Kelly
        if staking == "quarter_kelly" and gw_bets:
            tot_gw_stake = sum(b["raw_stake"] for b in gw_bets)
            max_allowed = 0.25 * gw_pre_bankroll
            scale = min(1.0, max_allowed / tot_gw_stake) if tot_gw_stake > 0 else 1.0
            for b in gw_bets:
                b["stake"] = b["raw_stake"] * scale
        else:
            for b in gw_bets:
                b["stake"] = b["raw_stake"]

        # Batch settlement
        gw_pnl = 0.0
        for b in gw_bets:
            won = (b["outcome"] == b["actual"])
            pnl = b["stake"] * (b["odds"] - 1.0) if won else -b["stake"]
            b["won"] = won
            b["pnl"] = pnl
            gw_pnl += pnl
            bet_records.append(b)

        bankroll += gw_pnl
        peak_bankroll = max(peak_bankroll, bankroll)
        dd_units = peak_bankroll - bankroll
        dd_pct = (dd_units / peak_bankroll * 100.0) if peak_bankroll > 0 else 0.0
        max_dd_units = max(max_dd_units, dd_units)
        max_dd_pct = max(max_dd_pct, dd_pct)

        # Weekly return for Sharpe
        gw_ret = gw_pnl / gw_pre_bankroll if gw_pre_bankroll > 0 else 0.0
        gameweek_returns.append(gw_ret)

    total_bets = len(bet_records)
    total_matches = len(df)
    bet_freq = (total_bets / total_matches * 100.0) if total_matches > 0 else 0.0
    turnover = sum(b["stake"] for b in bet_records)
    net_pnl = sum(b["pnl"] for b in bet_records)
    roi = (net_pnl / turnover * 100.0) if turnover > 0 else 0.0
    win_rate = (sum(1 for b in bet_records if b["won"]) / total_bets) if total_bets > 0 else 0.0

    # Annualized Gameweek Sharpe (38 weeks per season)
    if len(gameweek_returns) > 1 and float(np.std(gameweek_returns)) > 0:
        ann_sharpe = float(np.mean(gameweek_returns) / np.std(gameweek_returns) * np.sqrt(38))
    else:
        ann_sharpe = 0.0

    # Per-bet trade Sharpe
    if total_bets > 1:
        bet_returns = [b["pnl"] / b["stake"] for b in bet_records if b["stake"] > 0]
        if bet_returns and float(np.std(bet_returns)) > 0:
            per_bet_sharpe = float(np.mean(bet_returns) / np.std(bet_returns))
        else:
            per_bet_sharpe = 0.0
    else:
        per_bet_sharpe = 0.0

    return BacktestResult(
        total_bets=total_bets,
        bet_frequency=float(bet_freq),
        turnover=float(turnover),
        net_pnl=float(net_pnl),
        roi=float(roi),
        win_rate=float(win_rate),
        max_drawdown_units=float(max_dd_units),
        max_drawdown_pct=float(max_dd_pct),
        annualized_sharpe=ann_sharpe,
        per_bet_sharpe=per_bet_sharpe,
        history=pd.DataFrame(bet_records),
    )
