import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath('.'))

from pipelines.run_tri_market_pipeline import run_rolling_backtest
from core.data_loader import download_market_data
from core.return_calculations import compute_log_returns
from backtesting.allocation_stability_index import calculate_asi

prices = download_market_data(['SPY', 'ASHR', 'INDA'], start_date='2005-01-01', end_date='2025-01-01')
returns = compute_log_returns(prices)

bl_returns, bl_weights = run_rolling_backtest(returns, np.array([1/3, 1/3, 1/3]), window_size=252, model_type='black_litterman', tau=0.05)

print("Columns:", getattr(bl_weights, 'columns', 'None'))

print("Global ASI:", calculate_asi(bl_weights))
if isinstance(bl_weights, pd.DataFrame):
    print("US ASI:", calculate_asi(bl_weights.iloc[:, 0].to_frame()))
    print("China ASI:", calculate_asi(bl_weights.iloc[:, 1].to_frame()))
    print("India ASI:", calculate_asi(bl_weights.iloc[:, 2].to_frame()))
