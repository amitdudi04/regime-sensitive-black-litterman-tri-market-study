import numpy as np
import pandas as pd

def compute_implied_equilibrium_returns(cov_matrix, market_cap_weights, lambda_risk_aversion):
    """
    Derives the neutral Equilibrium Implied Returns (Pi) from observable market capitalization weights.
    Formula: Pi = lambda * Sigma * w_mkt
    """
    w = np.array(market_cap_weights)
    sigma = cov_matrix.values
    
    pi = lambda_risk_aversion * np.dot(sigma, w)
    return pd.Series(pi, index=cov_matrix.index)

def compute_black_litterman_posterior(pi, cov_matrix, P, Q, Omega, tau):
    """
    Implement the Black–Litterman Bayesian posterior expected return calculation.
    """
    sigma = cov_matrix.values
    inv_tau_sigma = np.linalg.inv(tau * sigma)
    
    # If there are no views, posterior == prior
    if P is None or len(P) == 0:
        return pi
        
    inv_omega = np.linalg.inv(Omega)
    
    # Pre-compute components
    pt_inv_omega_p = np.dot(np.dot(P.T, inv_omega), P)
    pt_inv_omega_q = np.dot(np.dot(P.T, inv_omega), Q)
    
    # Compute inverse term
    inv_term = np.linalg.inv(inv_tau_sigma + pt_inv_omega_p)
    
    # Compute expected term
    exp_term = np.dot(inv_tau_sigma, pi.values) + pt_inv_omega_q
    
    # Final posterior E[R]
    posterior_er = np.dot(inv_term, exp_term)
    
    return pd.Series(posterior_er, index=cov_matrix.index)
