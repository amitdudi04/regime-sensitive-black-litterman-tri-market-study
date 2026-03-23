import sys
import os
import yaml
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.data_loader import download_market_data
from core.return_calculations import compute_log_returns
from core.covariance_estimators import estimate_covariance
from models.black_litterman_model import compute_implied_equilibrium_returns, compute_black_litterman_posterior
from models.optimizer import compute_black_litterman_weights
from backtesting.rolling_backtest import run_rolling_backtest

def run_tau_sensitivity():
    print("Executing robustness parameter grid tracking Tau uncertainty.")
    
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'project_config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        
    start_date = config.get('start_date', '2005-01-01')
    end_date = config.get('end_date', '2025-01-01')
    window_size = config.get('rebalance_window', 252)
    
    tickers = ['SPY', 'ASHR', 'INDA'] 
    prices = download_market_data(tickers, start_date=start_date, end_date=end_date)
    
    if prices.empty:
        print("Data load failed. Exiting.")
        return

    returns = compute_log_returns(prices)
    cov_matrix = estimate_covariance(returns)
    pi = compute_implied_equilibrium_returns(cov_matrix, [1/3, 1/3, 1/3], lambda_risk_aversion=3.0)
    
    tau_grid = [0.01, 0.05, 0.10, 0.15, 0.20]
    results = []
    
    for tau in tau_grid:
        bl_posterior = compute_black_litterman_posterior(pi, cov_matrix, P=None, Q=None, Omega=None, tau=tau)
        bl_weights = compute_black_litterman_weights(bl_posterior, cov_matrix)
        bl_returns, _ = run_rolling_backtest(returns, bl_weights, window_size=window_size)
        
        # Calculate Sharpe mechanically
        sharpe = (bl_returns.mean() / bl_returns.std()) * (252 ** 0.5)
        results.append({
            'Tau': tau,
            'Sharpe': float(sharpe)
        })
        print(f"Tau: {tau} | Sharpe: {sharpe:.4f}")
        
    # Export explicitly
    df = pd.DataFrame(results)
    export_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'v1_final_results', 'tau_sensitivity_results.csv')
    df.to_csv(export_path, index=False)
    print(f"Exported Tau robustness matrix to: {export_path}")

if __name__ == "__main__":
    run_tau_sensitivity()
