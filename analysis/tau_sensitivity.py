"""Reproducible fixed-tau sensitivity analysis on the main out-of-sample sample."""

from collections.abc import Iterable
from dataclasses import replace

import numpy as np
import pandas as pd

from backtesting.paper_backtest import BacktestConfig, run_paper_backtest


def run_tau_sensitivity(
    returns: pd.DataFrame,
    config: BacktestConfig,
    tau_values: Iterable[float],
    *,
    market: str = "US",
) -> pd.DataFrame:
    """Run each fixed tau on the same universe, sample, and net-return convention."""
    values = [float(value) for value in tau_values]
    if not values or any(not np.isfinite(value) or value <= 0 for value in values):
        raise ValueError("tau_values must contain finite, positive values")
    if len(set(values)) != len(values):
        raise ValueError("tau_values must be unique")

    rows: list[dict[str, object]] = []
    for tau in values:
        fixed_config = replace(config, tau_low_vol=tau, tau_high_vol=tau)
        packet = run_paper_backtest(returns, fixed_config)
        series = packet["daily_returns"]["black_litterman_net"].dropna()
        if len(series) < 2:
            raise ValueError(f"Tau {tau} produced fewer than two out-of-sample returns")
        volatility = float(series.std(ddof=1))
        sharpe = (
            float(series.mean() / volatility * np.sqrt(252.0))
            if np.isfinite(volatility) and volatility > 0
            else np.nan
        )
        rows.append(
            {
                "Tau": tau,
                "Market": market,
                "Sharpe Ratio": sharpe,
                "OOS Start": series.index.min().date().isoformat(),
                "OOS End": series.index.max().date().isoformat(),
                "OOS Observations": int(len(series)),
                "Return Series": "black_litterman_net",
                "Return Convention": "simple net returns; arithmetic annualization; zero risk-free rate",
                "Tau Rule": "fixed: tau_low_vol equals tau_high_vol",
                "Equilibrium Weight Method": packet["equilibrium_weight_method"],
            }
        )
    return pd.DataFrame(rows)
