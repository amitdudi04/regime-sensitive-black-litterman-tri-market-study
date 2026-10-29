"""Optional, source-backed SOE/private descriptive study; never generates paper data.

Requires actual single-security daily returns and *dated* ownership evidence.
ETF basket constituents and a fabricated ownership mapping are not acceptable
substitutes for the missing historical research input.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def evaluate_dated_ownership(
    security_returns: pd.DataFrame,
    ownership_events: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Daily equal-weight, gross descriptive ownership portfolios.

    ownership_events must contain security_id, available_at, and group. A
    classification is eligible only from its declared available_at date onward.
    No costs or private-company inference are assumed. The output is a NEW
    descriptive diagnostic, not a reconstruction of the published Table 6.
    """
    returns = pd.DataFrame(security_returns, dtype=float).copy().sort_index()
    if not isinstance(returns.index, pd.DatetimeIndex) or returns.index.has_duplicates:
        raise ValueError("Security returns require a unique DatetimeIndex")
    if returns.empty or returns.columns.has_duplicates or len(returns.columns) < 2:
        raise ValueError("Provide at least two distinct security return columns")
    if not np.isfinite(returns.dropna().to_numpy()).all() or (returns.dropna() <= -1).any().any():
        raise ValueError("Observed simple returns must be finite and greater than -100%")
    required = {"security_id", "available_at", "group"}
    evidence = pd.DataFrame(ownership_events).copy()
    if not required.issubset(evidence.columns) or evidence.empty:
        raise ValueError("Dated ownership evidence requires security_id, available_at, group")
    evidence["available_at"] = pd.to_datetime(evidence["available_at"], errors="raise")
    if evidence["available_at"].isna().any() or not set(evidence["group"]).issubset({"SOE", "Private"}):
        raise ValueError("Only dated, explicit SOE/Private labels are accepted")
    if evidence.duplicated(["security_id", "available_at"]).any():
        raise ValueError("Ambiguous simultaneous ownership classifications")
    if not set(returns.columns).issubset(set(evidence["security_id"])):
        raise ValueError("Every security must have a dated classification record")
    panel = returns.stack().rename("daily_return").reset_index()
    panel.columns = ["Date", "security_id", "daily_return"]
    panel = panel.sort_values(["Date", "security_id"])
    evidence = evidence.sort_values(["available_at", "security_id"])
    aligned = pd.merge_asof(
        panel, evidence,
        by="security_id", left_on="Date", right_on="available_at",
        direction="backward", allow_exact_matches=True,
    )
    aligned = aligned.dropna(subset=["group"])
    if aligned.empty:
        raise ValueError("No dated ownership evidence was available at return dates")
    portfolio = (
        aligned.groupby(["Date", "group"], observed=True)["daily_return"]
        .mean().unstack("group")
    )
    if any(group not in portfolio for group in ("SOE", "Private")):
        raise ValueError("Both ownership groups need supported return histories")
    portfolio = portfolio[["SOE", "Private"]].dropna()
    if len(portfolio) < 20:
        raise ValueError("At least twenty common dated sessions are required")
    rows = []
    for group in ("SOE", "Private"):
        series = portfolio[group]
        wealth = (1.0 + series).cumprod()
        drawdown = wealth / np.maximum.accumulate(np.r_[1.0, wealth.to_numpy()])[1:] - 1.0
        vol = float(series.std(ddof=1) * np.sqrt(252))
        rows.append({
            "Group": group, "Observations": len(series),
            "Sample Start": series.index.min().date().isoformat(),
            "Sample End": series.index.max().date().isoformat(),
            "Annualized Arithmetic Gross Return": float(series.mean() * 252),
            "Annualized Volatility": vol,
            "Sharpe RF Zero": float(series.mean() * 252 / vol) if vol > 0 else np.nan,
            "Max Drawdown": float(drawdown.min()),
            "Strategy Convention": "daily equal weight; gross; no estimated trading cost",
            "Published Paper Table 6 Reproduced": False,
        })
    return pd.DataFrame(rows), portfolio
