"""Reproducible crisis-window drawdown, volatility-spike, and recovery metrics."""

from collections.abc import Mapping
import json

import numpy as np
import pandas as pd

from backtesting.crisis_freeze import define_crisis_intervals, execute_crisis_freeze

CRISIS_MARKET = {
    "2008_US_GFC": "US",
    "2015_China_Crash": "China",
    "2020_India_Covid": "India",
}


def calculate_crisis_metrics(
    asset_returns: pd.DataFrame,
    strategy_returns: pd.Series,
    weight_history: pd.DataFrame,
    crisis_start: str,
    crisis_end: str,
    *,
    pre_crisis_window: int = 252,
) -> dict[str, object]:
    """Calculate crisis metrics using frozen target weights and an explicit V(t0) target."""
    assets = pd.DataFrame(asset_returns).copy().sort_index()
    strategy = pd.Series(strategy_returns).copy().sort_index()
    weights = pd.DataFrame(weight_history).copy().sort_index()
    assets.index = pd.DatetimeIndex(pd.to_datetime(assets.index))
    strategy.index = pd.DatetimeIndex(pd.to_datetime(strategy.index))
    weights.index = pd.DatetimeIndex(pd.to_datetime(weights.index))

    common = assets.index.intersection(strategy.index).sort_values()
    assets = assets.reindex(common)
    strategy = strategy.reindex(common)
    if assets.empty or strategy.isna().any() or assets.isna().any().any():
        raise ValueError("Crisis analysis requires aligned, complete daily asset and strategy returns")
    if pre_crisis_window < 2:
        raise ValueError("pre_crisis_window must be at least two trading days")

    frozen_history = execute_crisis_freeze(
        weights, crisis_start, crisis_end, trading_index=common
    )
    if frozen_history.empty:
        raise ValueError("The crisis interval contains no out-of-sample trading observations")
    frozen_weights = frozen_history.iloc[0].reindex(assets.columns)
    if frozen_weights.isna().any() or not np.isfinite(frozen_weights.to_numpy(dtype=float)).all():
        raise ValueError("Pre-crisis weights do not cover the crisis return universe")
    if (frozen_weights < -1e-10).any() or not np.isclose(float(frozen_weights.sum()), 1.0, atol=1e-6):
        raise ValueError("Frozen crisis weights must be long-only and fully invested")

    crisis_dates = frozen_history.index
    crisis_returns = assets.loc[crisis_dates].dot(frozen_weights.astype(float))
    pre_crisis_assets = assets.loc[assets.index < crisis_dates[0]].tail(pre_crisis_window)
    if len(pre_crisis_assets) < 2:
        raise ValueError("Insufficient pre-crisis observations to estimate baseline volatility")
    pre_crisis_returns = pre_crisis_assets.dot(frozen_weights.astype(float))
    baseline_volatility = float(pre_crisis_returns.std(ddof=1))
    crisis_volatility = float(crisis_returns.std(ddof=1))
    if not np.isfinite(baseline_volatility) or baseline_volatility <= 0:
        raise ValueError("Pre-crisis volatility must be finite and positive")

    crisis_wealth = (1.0 + crisis_returns).cumprod()
    peaks = np.maximum.accumulate(np.concatenate(([1.0], crisis_wealth.to_numpy())))[1:]
    drawdowns = crisis_wealth.to_numpy() / peaks - 1.0
    trough_position = int(np.argmin(drawdowns))
    trough_date = pd.Timestamp(crisis_returns.index[trough_position])
    max_drawdown = float(drawdowns[trough_position])

    # Replace only the crisis-window strategy returns with the frozen-weight series.
    # Post-crisis recovery then follows the ordinary out-of-sample strategy path.
    recovery_returns = strategy.loc[strategy.index >= crisis_dates[0]].copy()
    recovery_returns.loc[crisis_returns.index] = crisis_returns
    recovery_wealth = (1.0 + recovery_returns).cumprod()
    recovery_candidates = recovery_wealth.loc[recovery_wealth.index >= trough_date]
    recovered = recovery_candidates.loc[recovery_candidates >= 1.0]
    recovery_date = pd.Timestamp(recovered.index[0]) if not recovered.empty else pd.NaT
    if pd.isna(recovery_date):
        recovery_days: int | None = None
    else:
        recovery_days = int(
            recovery_returns.index.get_loc(recovery_date)
            - recovery_returns.index.get_loc(trough_date)
        )

    return {
        "Max Drawdown": max_drawdown,
        "Volatility Spike": (
            crisis_volatility / baseline_volatility if baseline_volatility > 0 else np.nan
        ),
        "Recovery Trading Days": recovery_days,
        "Crisis First Trading Day": crisis_dates[0].date().isoformat(),
        "Crisis Last Trading Day": crisis_dates[-1].date().isoformat(),
        "Trough Date": trough_date.date().isoformat(),
        "Recovery Date": None if pd.isna(recovery_date) else recovery_date.date().isoformat(),
        "Pre-Crisis Observations": int(len(pre_crisis_returns)),
        "Crisis Observations": int(len(crisis_returns)),
        "Frozen Weights": {str(key): float(value) for key, value in frozen_weights.items()},
    }


def build_crisis_summary(
    market: str,
    asset_returns: pd.DataFrame,
    strategy_returns: Mapping[str, pd.Series],
    weight_histories: Mapping[str, pd.DataFrame],
    *,
    intervals: Mapping[str, tuple[str, str]] | None = None,
) -> pd.DataFrame:
    """Create a long-form summary for the crisis assigned to the specified market."""
    all_intervals = dict(intervals or define_crisis_intervals())
    matching = [
        (crisis, dates)
        for crisis, dates in all_intervals.items()
        if CRISIS_MARKET.get(crisis) == market
    ]
    if not matching:
        raise ValueError(f"No configured crisis interval for market {market!r}")

    rows: list[dict[str, object]] = []
    for crisis, (start, end) in matching:
        for model, strategy in strategy_returns.items():
            weight_key = {
                "Black-Litterman": "black_litterman",
                "Markowitz": "markowitz",
            }.get(model, model)
            if weight_key not in weight_histories:
                raise ValueError(f"Missing weight history for {model}")
            metrics = calculate_crisis_metrics(
                asset_returns,
                strategy,
                weight_histories[weight_key],
                start,
                end,
            )
            metrics["Frozen Weights"] = json.dumps(
                metrics["Frozen Weights"], sort_keys=True
            )
            rows.append(
                {
                    "Crisis": crisis,
                    "Market": market,
                    "Model": model,
                    "Requested Crisis Start": start,
                    "Requested Crisis End": end,
                    **metrics,
                }
            )
    return pd.DataFrame(rows)
