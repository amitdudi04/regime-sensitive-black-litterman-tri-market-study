import numpy as np
import pandas as pd


def _clean_returns(values):
    return values.replace([np.inf, -np.inf], np.nan).dropna(how="any")


def compute_simple_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    """Arithmetic returns used for portfolio P&L, turnover and wealth compounding."""
    return _clean_returns(price_df.pct_change())


def compute_log_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    """Continuously compounded returns retained for diagnostics/econometric use."""
    return _clean_returns(np.log(price_df / price_df.shift(1)))
