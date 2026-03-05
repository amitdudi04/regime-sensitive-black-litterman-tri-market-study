import pandas as pd
import numpy as np

def calculate_asi(rolling_weights_df):
    """
    Compute the Allocation Stability Index (ASI).
    ASI measures the average L1 norm drift between consecutive portfolio weight vectors 
    during rolling out-of-sample backtesting to isolate structural stability penalties.
    """
    if rolling_weights_df is None or len(rolling_weights_df) < 2:
        return np.nan
        
    diffs = rolling_weights_df.diff().dropna()
    l1_norms = diffs.abs().sum(axis=1)
    
    # The average L1 distance across consecutive localized execution blocks
    asi = l1_norms.mean()
    
    return asi
