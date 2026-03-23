import pandas as pd
import numpy as np

def compute_asi(rolling_weights_df):
    """
    Compute the Allocation Stability Index (ASI).
    ASI measures the average L1 norm drift between consecutive portfolio weight vectors 
    during rolling out-of-sample backtesting to isolate structural stability penalties.
    """
    if rolling_weights_df is None or len(rolling_weights_df) < 2:
        return np.nan
        
    print("ASI computed using L1 norm weight drift")
    
    weights_diff = rolling_weights_df.diff()
    asi_series = weights_diff.abs().sum(axis=1)
    asi_value = float(asi_series.mean())
    
    return asi_value
