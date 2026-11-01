import numpy as np
import pandas as pd
from core.validation import normalized_weights


def compute_asi(rolling_weights_df):
    """
    Mean L1 distance between consecutive target-weight vectors.

    ASI measures optimizer target-weight instability. It is not a dollar
    transaction-cost measure and does not include price drift between rebalances.
    """
    if rolling_weights_df is None or len(rolling_weights_df) < 2:
        return np.nan

    weights = normalized_weights(rolling_weights_df)
    asi_series = weights.diff().abs().sum(axis=1, min_count=1).dropna()
    return float(asi_series.mean())
