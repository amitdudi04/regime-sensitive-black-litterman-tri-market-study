import pandas as pd


def define_crisis_intervals():
    """Return the historical crisis windows used in the working-paper reference."""
    return {
        "2008_US_GFC": ("2008-08-01", "2009-03-09"),
        "2015_China_Crash": ("2015-06-01", "2016-02-01"),
        "2020_India_Covid": ("2020-02-15", "2020-05-01"),
    }


def execute_crisis_freeze(full_weights_df, crisis_start, crisis_end):
    """
    Freeze the last target-weight vector strictly observed before crisis_start.

    This helper operates on a weight-history DataFrame. It does not calculate
    drawdown or recovery by itself; those require the corresponding asset-return
    series and an explicitly defined wealth reference.
    """
    weights = pd.DataFrame(full_weights_df).sort_index()
    start = pd.Timestamp(crisis_start)
    end = pd.Timestamp(crisis_end)

    pre_crisis = weights.loc[weights.index < start]
    if pre_crisis.empty:
        raise ValueError("No pre-crisis weight vector is available")

    frozen = pre_crisis.iloc[-1]
    crisis_index = weights.loc[(weights.index >= start) & (weights.index <= end)].index

    return pd.DataFrame(
        [frozen.values] * len(crisis_index),
        index=crisis_index,
        columns=weights.columns,
    )
