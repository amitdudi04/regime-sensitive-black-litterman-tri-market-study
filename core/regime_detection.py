"""Regime detection utilities.

Provides rolling volatility regime detection used to adjust BL tau.
"""
import pandas as pd
import numpy as np


def rolling_60d_volatility(returns: pd.DataFrame) -> pd.Series:
    """Return mean 60-day rolling annualized volatility across assets.

    Returns a series indexed by date with the cross-sectional mean of 60-day
    vol (annualized) at each date.
    """
    roll_std = returns.rolling(window=60).std()
    roll_vol_ann = roll_std * np.sqrt(252)
    return roll_vol_ann.mean(axis=1)


def is_high_vol_regime(returns: pd.DataFrame, as_of_date=None) -> bool:
    """Determine if the latest period is high vol vs rolling median.

    If as_of_date is None, uses the last available date.
    """
    vol_series = rolling_60d_volatility(returns)
    if vol_series.dropna().empty:
        return False
    if as_of_date is None:
        last = vol_series.dropna().iloc[-1]
    else:
        last = vol_series.reindex(vol_series.index).loc[as_of_date]
    median = vol_series.dropna().median()
    return float(last) > float(median)
