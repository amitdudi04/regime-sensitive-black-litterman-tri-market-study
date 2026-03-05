import pandas as pd
from sklearn.covariance import LedoitWolf

def estimate_covariance(returns, annualization_factor=252):
    """
    Implement Ledoit–Wolf covariance shrinkage and annualization.
    """
    lw = LedoitWolf()
    
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
