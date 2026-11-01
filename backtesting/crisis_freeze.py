import pandas as pd
from core.validation import normalized_weights


def define_crisis_intervals():
    """Return the historical crisis windows used in the working-paper reference."""
    return {
        "2008_US_GFC": ("2008-08-01", "2009-03-09"),
        "2015_China_Crash": ("2015-06-01", "2016-02-01"),
        "2020_India_Covid": ("2020-02-15", "2020-05-01"),
    }


def execute_crisis_freeze(
    full_weights_df,
    crisis_start,
    crisis_end,
    trading_index=None,
):
    """Freeze the last target-weight vector before a crisis over every requested trading day.

    If trading_index is omitted, retain the legacy behavior of returning only crisis
    dates present in the weight history. The empirical pipeline passes the full daily
    return index so the frozen weights cover the entire crisis window.
    """
    weights = pd.DataFrame(full_weights_df).sort_index()
    if weights.empty:
        raise ValueError("A non-empty portfolio weight history is required")
    weights.index = pd.DatetimeIndex(pd.to_datetime(weights.index))
    if weights.index.hasnans or weights.index.has_duplicates or weights.index.tz is not None:
        raise ValueError("Crisis weights require unique dated observations")
    normalized_weights(weights)
    start = pd.Timestamp(crisis_start)
    end = pd.Timestamp(crisis_end)
    if end < start:
        raise ValueError("crisis_end must be on or after crisis_start")

    pre_crisis = weights.loc[weights.index < start]
    if pre_crisis.empty:
        raise ValueError("No pre-crisis weight vector is available")
    frozen = pre_crisis.iloc[-1]

    if trading_index is None:
        available_index = weights.index
    else:
        available_index = pd.DatetimeIndex(pd.to_datetime(trading_index)).sort_values()
    crisis_index = available_index[(available_index >= start) & (available_index <= end)]
    return pd.DataFrame(
        [frozen.values] * len(crisis_index),
        index=crisis_index,
        columns=weights.columns,
    )
