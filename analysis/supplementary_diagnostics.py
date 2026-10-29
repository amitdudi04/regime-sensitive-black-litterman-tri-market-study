"""Supplementary diagnostics, clearly separated from manuscript replication.

Outputs are fresh, ex-post measurements of the current portfolio model.
They are not the original manuscript's regime, ownership or bootstrap results.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from analysis.regime_detection import fit_markov_regime_model, compute_regime_performance
from analysis.statistical_tests import circular_block_bootstrap_sharpe_difference


def run_supplementary_diagnostics(
    market: str,
    benchmark_returns: pd.Series,
    bl_returns: pd.Series,
    mv_returns: pd.Series,
    *,
    bootstrap_iterations: int = 2000,
    block_size: int = 20,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return regime performance, daily classifications and Sharpe uncertainty.

    Regime probabilities are smoothed over the entire sample (ex-post, NOT a
    trading signal). Bootstrap is paired on common return dates. No manuscript
    statistic is silently substituted from this diagnostic.
    """
    df = pd.concat(
        [
            pd.Series(benchmark_returns, name="benchmark"),
            pd.Series(bl_returns, name="bl"),
            pd.Series(mv_returns, name="mv"),
        ],
        axis=1,
        join="inner",
    ).dropna().sort_index()
    if len(df) < 80:
        raise ValueError("Too few aligned daily observations for supplementary diagnostics")
    if not df.index.is_unique:
        raise ValueError("Repeated dates would invalidate aligned diagnostics")
    classifications, fit = fit_markov_regime_model(df["benchmark"])
    regime = compute_regime_performance(df["bl"], df["mv"], classifications)
    regime.insert(0, "Market", market)
    regime["Regime Classification"] = "ex-post smoothed, full-sample"
    regime["OOS Start"] = df.index.min().date().isoformat()
    regime["OOS End"] = df.index.max().date().isoformat()
    regime["Total Paired Observations"] = len(df)
    if int(regime["Observations"].sum()) != len(df):
        raise RuntimeError("Regime partition does not cover all paired observations")
    result = circular_block_bootstrap_sharpe_difference(
        df["bl"], df["mv"],
        block_size=block_size, iterations=bootstrap_iterations, seed=seed,
    )
    p = float(result["p_value"])
    if not np.isfinite(p) or not 0 <= p <= 1:
        raise ValueError("Invalid bootstrap probability")
    boot = pd.DataFrame([{
        "Market": market,
        "Test": "paired circular-block bootstrap Sharpe difference",
        "Observed Sharpe Difference BL minus Markowitz":
            result["observed_sharpe_difference"],
        "Null Centered Two-sided P-value": p,
        "Block Size": block_size,
        "Iterations": bootstrap_iterations,
        "Seed": seed,
        "Paired Observations": len(df),
        "OOS Start": df.index.min().date().isoformat(),
        "OOS End": df.index.max().date().isoformat(),
        "Return Convention": "simple net returns; RF=0; arithmetic annualization",
        "Historical Paper Test Reproduction": False,
    }])
    probabilities = classifications.copy()
    probabilities.insert(0, "Market", market)
    probabilities.index.name = "Date"
    return regime, probabilities, boot
