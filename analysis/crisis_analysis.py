"""Reproducible crisis-window drawdown, volatility-spike, and recovery metrics."""

from collections.abc import Mapping
import json

import numpy as np
import pandas as pd

from backtesting.crisis_freeze import define_crisis_intervals, execute_crisis_freeze
from backtesting.paper_backtest import _buy_and_hold_daily_returns
from core.validation import validate_panel

CRISIS_MARKET = {
    "2008_US_GFC": "US",
    "2015_China_Crash": "China",
    "2020_India_Covid": "India",
}


def calculate_crisis_metrics(
    asset_returns: pd.DataFrame,
    weight_history: pd.DataFrame,
    crisis_start: str,
    crisis_end: str,
    *,
    pre_crisis_window: int = 252,
) -> dict[str, object]:
    """Calculate crisis metrics using frozen target weights and an explicit V(t0) target."""
    assets = validate_panel(asset_returns)
    weights = pd.DataFrame(weight_history).copy().sort_index()
    assets.index = pd.DatetimeIndex(pd.to_datetime(assets.index))
    weights.index = pd.DatetimeIndex(pd.to_datetime(weights.index))
    if assets.empty or assets.isna().any().any():
        raise ValueError("Crisis analysis requires complete daily asset returns")
    if pre_crisis_window < 2:
        raise ValueError("pre_crisis_window must be at least two trading days")

    frozen_history = execute_crisis_freeze(
        weights, crisis_start, crisis_end, trading_index=assets.index
    )
    if frozen_history.empty:
        raise ValueError("The crisis interval contains no out-of-sample trading observations")
    frozen_weights = frozen_history.iloc[0].reindex(assets.columns)
    if frozen_weights.isna().any() or not np.isfinite(frozen_weights.to_numpy(dtype=float)).all():
        raise ValueError("Pre-crisis weights do not cover the crisis return universe")
    if (frozen_weights < -1e-10).any() or not np.isclose(float(frozen_weights.sum()), 1.0, atol=1e-6):
        raise ValueError("Frozen crisis weights must be long-only and fully invested")

    crisis_dates = frozen_history.index
    if (assets <= -1.0).any().any():
        raise ValueError("Log-return crisis analysis requires asset simple returns greater than -100%")
    asset_log_returns = np.log1p(assets)
    crisis_returns = asset_log_returns.loc[crisis_dates].dot(frozen_weights.astype(float))
    pre_crisis_assets = asset_log_returns.loc[
        asset_log_returns.index < crisis_dates[0]
    ].tail(pre_crisis_window)
    if len(pre_crisis_assets) < 2:
        raise ValueError("Insufficient pre-crisis observations to estimate baseline volatility")
    pre_crisis_returns = pre_crisis_assets.dot(frozen_weights.astype(float))
    baseline_volatility = float(pre_crisis_returns.std(ddof=1))
    crisis_volatility = float(crisis_returns.std(ddof=1))
    if not np.isfinite(baseline_volatility) or baseline_volatility <= 0:
        raise ValueError("Pre-crisis volatility must be finite and positive")

    crisis_wealth = np.exp(crisis_returns.cumsum())
    # Normalize the first observed crisis value to V(t0)=1.0, so the first
    # log-return observation is not counted as a drawdown from a pre-t0 wealth level.
    crisis_wealth = crisis_wealth / float(crisis_wealth.iloc[0])
    peaks = np.maximum.accumulate(crisis_wealth.to_numpy())
    drawdowns = crisis_wealth.to_numpy() / peaks - 1.0
    trough_position = int(np.argmin(drawdowns))
    trough_date = pd.Timestamp(crisis_returns.index[trough_position])
    max_drawdown = float(drawdowns[trough_position])

    # Keep the pre-crisis target weights frozen from crisis start through recovery.
    # Using the adaptive strategy after the crisis window would change the exposure
    # during recovery and can materially shorten the measured recovery duration.
    recovery_returns = asset_log_returns.loc[
        asset_log_returns.index >= crisis_dates[0]
    ].dot(frozen_weights.astype(float))
    recovery_wealth = np.exp(recovery_returns.cumsum())
    recovery_wealth = recovery_wealth / float(recovery_wealth.iloc[0])
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

    # Additional economically consistent no-trade stress path. The historical
    # weighted-log diagnostic above is preserved separately for paper comparison.
    # Here the last pre-crisis target is purchased before the first event return
    # and then allowed to drift without rebalancing throughout recovery.
    buy_hold_returns = _buy_and_hold_daily_returns(
        assets.loc[assets.index >= crisis_dates[0]], frozen_weights.astype(float)
    )
    buy_hold_wealth = (1.0 + buy_hold_returns).cumprod()
    buy_hold_crisis_wealth = buy_hold_wealth.loc[crisis_dates]
    # Include an initial wealth of one *before* the first crisis observation.
    buy_hold_peak = np.maximum.accumulate(
        np.r_[1.0, buy_hold_crisis_wealth.to_numpy(dtype=float)]
    )[1:]
    buy_hold_drawdown = buy_hold_crisis_wealth.to_numpy(dtype=float) / buy_hold_peak - 1.0
    buy_hold_trough_pos = int(np.argmin(buy_hold_drawdown))
    buy_hold_trough_date = pd.Timestamp(crisis_dates[buy_hold_trough_pos])
    buy_hold_max_drawdown = float(buy_hold_drawdown[buy_hold_trough_pos])
    buy_hold_candidates = buy_hold_wealth.loc[
        buy_hold_wealth.index >= buy_hold_trough_date
    ]
    buy_hold_recovered = buy_hold_candidates.loc[buy_hold_candidates >= 1.0]
    buy_hold_recovery_date = (
        pd.Timestamp(buy_hold_recovered.index[0])
        if not buy_hold_recovered.empty else pd.NaT
    )
    buy_hold_recovery_days = (
        int(buy_hold_returns.index.get_loc(buy_hold_recovery_date)
            - buy_hold_returns.index.get_loc(buy_hold_trough_date))
        if not pd.isna(buy_hold_recovery_date) else None
    )

    return {
        "Max Drawdown": max_drawdown,
        "Buy-Hold Max Drawdown": buy_hold_max_drawdown,
        "Buy-Hold Recovery Trading Days": buy_hold_recovery_days,
        "Buy-Hold Trough Date": buy_hold_trough_date.date().isoformat(),
        "Buy-Hold Recovery Date": (
            None if pd.isna(buy_hold_recovery_date)
            else buy_hold_recovery_date.date().isoformat()
        ),
        "Buy-Hold Wealth Convention": "self-financing, no interim rebalancing, V(before first crisis return)=1",
        "Primary Investment Convention": "Buy-Hold fields; historical weighted-log fields are diagnostics only",
        "Buy-Hold Recovery Target": "crisis-start wealth 1; not the running peak",
        "Buy-Hold Recovery Duration": "trading-index positions from crisis-window MDD trough to recovery",
        "Buy-Hold Peak Wealth At Trough": float(buy_hold_peak[buy_hold_trough_pos]),
        "Buy-Hold Peak Date": (
            "BEFORE_FIRST_CRISIS_RETURN" if buy_hold_peak[buy_hold_trough_pos] == 1.0
            else pd.Timestamp(buy_hold_crisis_wealth.iloc[:buy_hold_trough_pos + 1].idxmax()).date().isoformat()
        ),

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
    model_keys = (
        ("Black-Litterman", "black_litterman"),
        ("Markowitz", "markowitz"),
    )
    for crisis, (start, end) in matching:
        for model, weight_key in model_keys:
            if weight_key not in weight_histories:
                raise ValueError(f"Missing weight history for {model}")
            metrics = calculate_crisis_metrics(
                asset_returns,
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
