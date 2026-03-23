import pandas as pd
import statsmodels.api as sm
import numpy as np
import pandas_datareader.data as web

def load_factor_data(index_dates):
    """
    Load Fama-French 4-factor data aligning to the portfolio dates using pandas-datareader.
    Data is natively sourced live from the Kenneth French Data Library.
    """
    start = index_dates.min().strftime('%Y-%m-%d')
    end = index_dates.max().strftime('%Y-%m-%d')
    
    # 1. Fetch live explicit factors (Market, Size, Value, Risk-Free)
    ff3_daily = web.DataReader('F-F_Research_Data_Factors_daily', 'famafrench', start, end)[0]
    
    # 2. Fetch standard Momentum factor 
    mom_daily = web.DataReader('F-F_Momentum_Factor_daily', 'famafrench', start, end)[0]
    
    factors = pd.concat([ff3_daily, mom_daily], axis=1)
    
    # Ken French library returns percentages (e.g., 1.5 instead of 0.015). Convert to formal decimals.
    factors = factors / 100.0
    
    factors.rename(columns={'Mkt-RF': 'MKT', 'Mom   ': 'MOM', 'Mom': 'MOM'}, inplace=True)
    
    factors.index = pd.to_datetime(factors.index.astype(str))
    
    # Index alignment against trading days without NA drop bleeding
    aligned_factors = factors.reindex(index_dates).ffill().bfill()
    
    return aligned_factors

def prepare_excess_returns(portfolio_returns, rf_rate_series):
    """
    Compute Rp - Rf
    """
    excess_return = portfolio_returns - rf_rate_series
    return excess_return.dropna()

def run_factor_regression(portfolio_returns, model_name="Portfolio"):
    """
    Run OLS regression on authentic Fama-French factors (MKT, SMB, HML, MOM).
    Rp - Rf = alpha + B1*MKT + B2*SMB + B3*HML + B4*MOM + e
    Returns dictionary of summary statistics natively.
    """
    # 1. Load authentic Fama-French library arrays 
    factors = load_factor_data(portfolio_returns.index)
    
    # 2. Ensure factor data and portfolio return series share identical dates safely
    if isinstance(portfolio_returns, pd.Series):
        pf_df = portfolio_returns.to_frame('Portfolio')
    else:
        pf_df = portfolio_returns
        
    data = pf_df.join(factors, how="inner").dropna()
    
    # 3. Prepare excess returns against authentic risk-free rates
    excess_returns = data.iloc[:, 0] - data['RF']
    
    Y = excess_returns
    X = data[['MKT', 'SMB', 'HML', 'MOM']]
    X = sm.add_constant(X)
    
    # 4. Fit OLS Model utilizing statsmodels native framework
    model = sm.OLS(Y, X).fit()
    
    return {
        'Model': model_name,
        'Alpha': float(model.params.get('const', 0)),
        'Alpha_t_stat': float(model.tvalues.get('const', 0)),
        'R_squared': float(model.rsquared),
        'MKT_beta': float(model.params.get('MKT', 0)),
        'MKT_t_stat': float(model.tvalues.get('MKT', 0)),
        'SMB_beta': float(model.params.get('SMB', 0)),
        'SMB_t_stat': float(model.tvalues.get('SMB', 0)),
        'HML_beta': float(model.params.get('HML', 0)),
        'HML_t_stat': float(model.tvalues.get('HML', 0)),
        'MOM_beta': float(model.params.get('MOM', 0)),
        'MOM_t_stat': float(model.tvalues.get('MOM', 0)),
        'P_value_Alpha': float(model.pvalues.get('const', 1.0))
    }
