import numpy as np
import pandas as pd


def compute_asi(rolling_weights_df):
    """
    Mean L1 distance between consecutive target-weight vectors.

    ASI measures optimizer target-weight instability. It is not a dollar
    transaction-cost measure and does not include price drift between rebalances.
    """
    if rolling_weights_df is None or len(rolling_weights_df) < 2:
        return np.nan

    weights = pd.DataFrame(rolling_weights_df, dtype=float)
    asi_series = weights.diff().abs().sum(axis=1).dropna()
    return float(asi_series.mean())
