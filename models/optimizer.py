import numpy as np
import pandas as pd
from scipy.optimize import minimize

def compute_mean_variance_weights(expected_returns, cov_matrix, risk_aversion=3.0):
    """
    Compute optimal portfolio weights using standard Mean-Variance optimization.
    """
    n = len(expected_returns)
    init_guess = np.ones(n) / n
    bounds = tuple((0, 1) for _ in range(n)) # Long only constraints
    
    # Fully invested constraint
    constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})
    
    def objective(w):
        port_return = np.dot(w, expected_returns)
        port_var = np.dot(np.dot(w, cov_matrix), w)
        # Maximize risk-adjusted return -> Minimize negative utility
        return -(port_return - (risk_aversion / 2) * port_var)
        
    result = minimize(objective, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    
    if not result.success:
        # Fallback to equal weight on failure
        return pd.Series(init_guess, index=expected_returns.index)
        
    return pd.Series(result.x, index=expected_returns.index)

def compute_black_litterman_weights(posterior_returns, cov_matrix, lambda_risk_aversion=3.0):
    """
    Compute optimal portfolio weights using Black-Litterman outputs.
    Usually the unconstrained solution is (lambda * Sigma)^-1 * E[R] 
    but we map it to standard optimization to include bounds.
    """
    return compute_mean_variance_weights(posterior_returns, cov_matrix, lambda_risk_aversion)
