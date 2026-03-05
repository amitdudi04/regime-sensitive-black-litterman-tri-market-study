import pandas as pd
import numpy as np

def run_rolling_backtest(returns_df, initial_weights, window_size=252):
    """
    Perform rolling out-of-sample portfolio simulation.
    Iteratively recalibrates portfolio constraints using standard historic look-back windows.
    Returns the out-of-sample equity curve and the rolling history of portfolio weights.
    """
    T = len(returns_df)
    portfolio_returns = []
    weights_history = []
    
    # Placeholder loop logic mapping standard out-of-sample flow
    for i in range(window_size, T):
        # Lookback slice
        train_data = returns_df.iloc[i-window_size:i]
        test_return = returns_df.iloc[i]
        
        # Here we would normally plug trailing data into the models/optimizer.py
        current_weight = initial_weights # static placeholder
        
        # Realized performance
        step_return = np.dot(current_weight, test_return)
        
        portfolio_returns.append(step_return)
        weights_history.append(current_weight)
        
    # Translate list to DataFrame Series matching the out-of-sample dates
    oos_dates = returns_df.index[window_size:]
    oos_series = pd.Series(portfolio_returns, index=oos_dates, name='Strategy Return')
    
    # Gather weights history into a structured DataFrame
    weights_history_df = pd.DataFrame(weights_history, index=oos_dates)
    if isinstance(initial_weights, pd.Series):
        weights_history_df.columns = initial_weights.index
        
    return oos_series, weights_history_df
