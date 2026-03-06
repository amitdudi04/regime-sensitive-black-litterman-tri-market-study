import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath('.'))

from pipelines.run_tri_market_pipeline import run_rolling_backtest
from core.data_loader import download_market_data
from core.return_calculations import compute_log_returns

prices = download_market_data(['SPY', 'ASHR', 'INDA'], start_date='2005-01-01', end_date='2025-01-01')
returns = compute_log_returns(prices)

print("Columns:", returns.columns)
# Tri-Market backtest
bl_returns, bl_weights = run_rolling_backtest(returns, np.array([1/3, 1/3, 1/3]), window_size=252, model_type='black_litterman', tau=0.05)
print("Tri-Market Return:", (bl_returns.mean() / bl_returns.std()) * (252 ** 0.5))
print("Tri-Market Return values:", bl_returns.mean() * 252)
