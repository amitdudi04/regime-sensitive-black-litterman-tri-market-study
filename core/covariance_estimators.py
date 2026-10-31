import pandas as pd
import numpy as np
from sklearn.covariance import LedoitWolf
from core.validation import validate_panel

def estimate_covariance(returns, annualization_factor=252):
    """
    Implement Ledoit–Wolf covariance shrinkage and annualization.
    """
    returns = validate_panel(returns)
    if len(returns) < 2 or not np.isfinite(annualization_factor) or annualization_factor <= 0:
        raise ValueError("Covariance requires two observations and positive finite annualization")
    lw = LedoitWolf(assume_centered=False)
    
    # Fit the estimator on the continuous return data
    lw.fit(returns)
    
    # Extract the shrinkage matrix
    daily_cov = lw.covariance_
    
    # Scale via explicit annualization logic utilizing standard geometric scalars
    annualized_cov = daily_cov * annualization_factor
    
    # Convert back to DataFrame for label alignment
    annualized_cov_df = pd.DataFrame(
        annualized_cov, 
        index=returns.columns, 
        columns=returns.columns
    )
    
    return annualized_cov_df
