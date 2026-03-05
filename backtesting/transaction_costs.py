import numpy as np
import pandas as pd

def calculate_turnover(weights_df):
    """
    Calculate turnover as the sum of absolute weight changes over time.
    Turnover = Sum(|W_t - W_{t-1}|)
    """
    weight_diff = weights_df.diff().abs()
    # Assume 100% turnover for the first period instantiation
    weight_diff.iloc[0] = weights_df.iloc[0]
    
    period_turnover = weight_diff.sum(axis=1)
    return period_turnover

def apply_transaction_costs(gross_returns_series, turnover_series, friction_rate=0.001):
    """
    Calculate the net performance decay factoring in continuous institutional turnover drag.
    Net Return = Gross Return - (Turnover * friction_rate)
    """
    transaction_cost_drag = turnover_series * friction_rate
    net_returns = gross_returns_series - transaction_cost_drag
    
    return net_returns, transaction_cost_drag
