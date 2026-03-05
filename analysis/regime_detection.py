import pandas as pd
import numpy as np
from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
import warnings

warnings.filterwarnings("ignore")

def fit_markov_regime_model(market_returns):
    """
    Fit a two-state Markov Regime Switching model to the market return series.
    R_t = mu_s + e_t
    e_t ~ N(0, sigma_s^2)
    where s in {0, 1} represents hidden market regimes (Low Vol VS High Vol).
    """
    # Clean data structure for statsmodels
    returns_clean = market_returns.dropna()
    
    # Fit 2-state model with switching variance
    # k_regimes=2: Two hidden states
    # trend='c': Constant mean in each state
    # switching_variance=True: Different volatility in each state
    model = MarkovRegression(returns_clean, k_regimes=2, trend='c', switching_variance=True)
    res = model.fit(disp=False)
    
    # Identify which state is "High Volatility" vs "Low Volatility"
    # res.params contains sigma2[0] and sigma2[1]
    vol_0 = res.params.get('sigma2[0]', 0)
    vol_1 = res.params.get('sigma2[1]', 0)
    
    high_vol_state = 1 if vol_1 > vol_0 else 0
    low_vol_state = 0 if vol_1 > vol_0 else 1
    
    # Get smoothed probabilities of being in each regime
    smoothed_probs = res.smoothed_marginal_probabilities
    
    # Most likely regime classification
    # Creating a standardized Output DataFrame
    classifications = pd.DataFrame(index=returns_clean.index)
    classifications['Prob_Low_Vol'] = smoothed_probs[low_vol_state]
    classifications['Prob_High_Vol'] = smoothed_probs[high_vol_state]
    
    # 0 = Low Volatility, 1 = High Volatility
    classifications['Regime'] = np.where(classifications['Prob_High_Vol'] > 0.5, 'High_Vol', 'Low_Vol')
    
    return classifications, res

def compute_regime_performance(bl_returns, mv_returns, regime_classifications):
    """
    Calculate performance metrics isolated strictly by market regime.
    """
    # 1. Join portfolio returns firmly with regime classifications
    df = pd.DataFrame({
        'BL_Return': bl_returns,
        'MV_Return': mv_returns
    }).join(regime_classifications[['Regime']], how='inner').dropna()
    
    summary_data = []
    
    # 2. Split observations into Low/High volatility blocks
    for regime in ['Low_Vol', 'High_Vol']:
        regime_df = df[df['Regime'] == regime]
        
        if len(regime_df) == 0:
            continue
            
        # 3. Compute metrics for Black-Litterman
        bl_mean = regime_df['BL_Return'].mean() * 252
        bl_vol = regime_df['BL_Return'].std() * (252 ** 0.5)
        bl_sharpe = bl_mean / bl_vol if bl_vol != 0 else 0
        
        # Compute metrics for Markowitz
        mv_mean = regime_df['MV_Return'].mean() * 252
        mv_vol = regime_df['MV_Return'].std() * (252 ** 0.5)
        mv_sharpe = mv_mean / mv_vol if mv_vol != 0 else 0
        
        summary_data.append({
            'Regime': regime,
            'BL Sharpe': float(bl_sharpe),
            'Markowitz Sharpe': float(mv_sharpe),
            'BL Return': float(bl_mean),
            'MV Return': float(mv_mean)
        })
        
    return pd.DataFrame(summary_data)
