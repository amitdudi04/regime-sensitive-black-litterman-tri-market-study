import numpy as np
import pandas as pd
from core.validation import validate_panel


def _clean_returns(values):
    return values.replace([np.inf, -np.inf], np.nan).dropna(how="any")


def compute_simple_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    """Arithmetic returns used for portfolio P&L, turnover and wealth compounding."""
    prices = validate_panel(price_df, kind="prices")
    return prices.pct_change(fill_method=None).iloc[1:]


def compute_log_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    """Continuously compounded returns retained for diagnostics/econometric use."""
    prices = validate_panel(price_df, kind="prices")
    return np.log(prices / prices.shift(1)).iloc[1:]
