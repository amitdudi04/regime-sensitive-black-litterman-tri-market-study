import os
import sys
import numpy as np

sys.path.append(os.path.abspath('.'))

from pipelines.run_tri_market_pipeline import run_rolling_backtest
from core.data_loader import download_market_data
from core.return_calculations import compute_log_returns
from core.covariance_estimators import estimate_covariance
from models.black_litterman_model import compute_implied_equilibrium_returns, compute_black_litterman_posterior
from models.optimizer import compute_black_litterman_weights

prices = download_market_data(['SPY', 'ASHR', 'INDA'], start_date='2005-01-01', end_date='2025-01-01')
returns = compute_log_returns(prices)
initial_weights = np.array([1/3, 1/3, 1/3])

T = len(returns)
portfolio_returns = []
weights_history = []
window_size = 252
rebalance_freq = 63
tau = 0.05
current_weight = initial_weights

for i in range(window_size, T):
    train_data = returns.iloc[i-window_size:i]
    test_return = returns.iloc[i]
    
    if (i - window_size) % rebalance_freq == 0 and (i - window_size) > 0:
        cov_matrix = estimate_covariance(train_data)
        expected_returns = train_data.mean() * 252
        
        n_assets = len(train_data.columns)
        market_weights = [1/n_assets] * n_assets
        pi = compute_implied_equilibrium_returns(cov_matrix, market_weights, lambda_risk_aversion=3.0)
        
        P = np.eye(n_assets)
        Q = pi.values + (expected_returns.values - pi.values) * 0.1 # Very mild conviction
        # Omega is variance of views, standard formula: tau * P * Sigma * P^T
        tau_cov = tau * cov_matrix.values
        Omega = np.diag(np.diag(tau_cov)) * 10.0 # Increase uncertainty
        
        bl_posterior = compute_black_litterman_posterior(pi, cov_matrix, P=P, Q=Q, Omega=Omega, tau=tau)
        res = compute_black_litterman_weights(bl_posterior, cov_matrix)
        current_weight = res.values
        
    weights_history.append(current_weight.copy())

import pandas as pd
df = pd.DataFrame(weights_history)
diffs = df.diff().dropna()
print("ASI:", diffs.abs().sum(axis=1).mean())
