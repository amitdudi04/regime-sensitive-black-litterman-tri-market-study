import pandas as pd
import numpy as np

def compute_log_returns(price_df):
    """
    Compute log returns and clean missing values.
    Returns stationary logarithmic return matrices.
    """
    # Logarithmic return formula: ln(P_t / P_t-1)
    log_returns = np.log(price_df / price_df.shift(1))
    
    # Clean initial NA from shift and any infinite values
    log_returns = log_returns.replace([np.inf, -np.inf], np.nan)
    log_returns = log_returns.dropna()
    
    return log_returns
