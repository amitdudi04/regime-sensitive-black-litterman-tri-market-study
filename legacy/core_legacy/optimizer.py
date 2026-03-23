"""
Black-Litterman Model Implementation
=====================================

A comprehensive implementation of the Black-Litterman portfolio optimization model
with advanced risk metrics and backtesting capabilities.

Author: Portfolio Optimization Research Team
Date: February 2026
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm
import matplotlib.pyplot as plt
import yfinance as yf
import logging
import warnings
from typing import List, Dict, Optional, Tuple, Any
from sklearn.covariance import LedoitWolf

# Configure structured logging
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore')


class BlackLittermanOptimizer:
    """
    Implements the Black-Litterman model for portfolio optimization.
    
    The Black-Litterman model combines market-implied returns with investor views
    using Bayesian statistics to create more stable and realistic portfolio weights.
    """
    
    def __init__(self, 
                 ticker_list: List[str], 
                 start_date: str, 
                 end_date: str, 
                 risk_free_rate: float = 0.03, 
                 use_market_cap_weights: bool = False, 
                 name_mapping: Optional[Dict[str, str]] = None,
                 covariance_method: str = 'sample'):
        """
        Initialize the optimizer with historical data.
        
        Parameters:
        -----------
        ticker_list : List[str]
            List of stock tickers (e.g., ['AAPL', 'MSFT', 'GOOGL'])
        start_date : str
            Start date for historical data (YYYY-MM-DD)
        end_date : str
            End date for historical data (YYYY-MM-DD)
        risk_free_rate : float
            Risk-free rate assumption (default: 3%)
        use_market_cap_weights : bool
            Approximate market cap weights using average price * volume (default: False)
        name_mapping : Optional[Dict[str, str]]
            Dictionary mapping raw tickers to readable asset names
        """
        self.original_tickers = ticker_list.copy()
        self.name_mapping = name_mapping
        self.ticker_list = [name_mapping.get(t, t) for t in ticker_list] if name_mapping else ticker_list.copy()
        
        self.start_date = start_date
        self.end_date = end_date
        self.risk_free_rate = risk_free_rate
        self.use_market_cap_weights = use_market_cap_weights
        
        # Fetch and process data
        self.prices = self._fetch_data()
        self.returns = np.log(self.prices / self.prices.shift(1)).dropna()
        
        # Covariance estimation method: 'sample' or 'ledoit'
        self.covariance_method = covariance_method
        self.cov_matrix = self._compute_covariance(self.returns)
        
        # Historical mean returns (will be overridden by market-implied returns)
        self.historical_mean = self.returns.mean() * 252  # Annualized
        
        # Market weights (initially equal-weight, can be customized)
        self.market_weights = np.array([1/len(ticker_list)] * len(ticker_list))
        
        if self.use_market_cap_weights:
            try:
                logger.debug("Fetching volume data to approximate market cap weights...")
                raw_data = yf.download(self.original_tickers, start=self.start_date, end=self.end_date, progress=False)
                
                if isinstance(raw_data, pd.DataFrame):
                    if 'Volume' in raw_data.columns and 'Close' in raw_data.columns:
                        avg_price = raw_data['Close'].mean()
                        avg_vol = raw_data['Volume'].mean()
                        approx_mcap = avg_price * avg_vol
                        
                        if isinstance(approx_mcap, pd.Series):
                            if self.name_mapping:
                                approx_mcap.rename(index=self.name_mapping, inplace=True)
                            mcap_vals = approx_mcap.reindex(self.ticker_list).fillna(1.0).values
                        else:
                            mcap_vals = np.array([approx_mcap])
                            
                        if np.sum(mcap_vals) > 0:
                            self.market_weights = mcap_vals / np.sum(mcap_vals)
                            logger.info("Market Cap weights approximated successfully.")
            except Exception as e:
                logger.warning(f"Could not compute market cap weights, falling back to equal weights. Error: {e}")
                
        # Risk aversion coefficient
        self.lambda_risk = 2.5
        
        # Black-Litterman parameters
        self.tau = 0.05  # Scaling factor for uncertainty
        self.bl_views = None
        self.bl_returns = None
        
        logger.info(f"Optimizer initialized with {len(ticker_list)} assets ({start_date} to {end_date})")
    
    def _fetch_data(self) -> pd.DataFrame:
        """Fetch historical price data from Yahoo Finance."""
        logger.debug(f"Fetching historical price data for {len(self.original_tickers)} tickers...")
        try:
            import time
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    import tempfile
                    import os
                    try:
                        custom_cache = os.path.join(tempfile.gettempdir(), f"yf_cache_custom_{attempt}")
                        if not os.path.exists(custom_cache):
                            os.makedirs(custom_cache, exist_ok=True)
                        yf.set_tz_cache_location(custom_cache)
                    except AttributeError:
                        pass
                        
                    logger.info(f"YFINANCE DOWNLOAD INITIATED (Attempt {attempt+1}/{max_retries}): Start='{self.start_date}', End='{self.end_date}', Tickers={self.original_tickers}")
                    data = yf.download(self.original_tickers, start=self.start_date, end=self.end_date, 
                                      progress=False)
                    
                    if isinstance(data, pd.DataFrame):
                        if isinstance(data.columns, pd.MultiIndex):
                            level_0 = data.columns.get_level_values(0)
                            level_1 = data.columns.get_level_values(1)
                            
                            if 'Adj Close' in level_0:
                                data = data['Adj Close']
                            elif 'Close' in level_0:
                                data = data['Close']
                            elif 'Adj Close' in level_1:
                                data = data.xs('Adj Close', axis=1, level=1)
                            elif 'Close' in level_1:
                                data = data.xs('Close', axis=1, level=1)
                            else:
                                raise ValueError(f"Could not find price data in multi-index columns: {data.columns.tolist()}")
                        else:
                            if 'Adj Close' in data.columns:
                                data = data['Adj Close']
                            elif 'Close' in data.columns:
                                data = data['Close']
                            elif len(self.original_tickers) == 1:
                                if self.original_tickers[0] in data.columns:
                                    data = data[[self.original_tickers[0]]]
                                else:
                                    for col in ['Adj Close', 'Close', 'Price']:
                                        if col in data.columns:
                                            data = data[[col]]
                                            data.columns = [self.original_tickers[0]]
                                            break
                            else:
                                raise ValueError(f"Could not find price metrics in columns: {data.columns.tolist()}")
                    
                    if isinstance(data, pd.Series):
                        col_name = self.original_tickers[0] if len(self.original_tickers) == 1 else 'Price'
                        data = data.to_frame(name=col_name)
                    
                    if data is None or data.empty:
                        raise ValueError(f"No data retrieved for tickers: {self.original_tickers}. Check ticker symbols and date range.")
                    
                    logger.debug(f"Data fetched: {data.shape[0]} rows, {data.shape[1]} columns")
                    
                    if self.name_mapping:
                        data.rename(columns=self.name_mapping, inplace=True)
                        
                    return data.dropna()
                except Exception as e:
                    logger.warning(f"Error fetching data on attempt {attempt+1}: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                    else:
                        raise e
        
        except Exception as e:
            raise RuntimeError(f"Error fetching data for {self.ticker_list}: {str(e)}")

    def _compute_covariance(self, returns: pd.DataFrame, annualize: bool = True) -> pd.DataFrame:
        """Compute covariance matrix using selected estimator.

        Parameters:
        - returns: daily returns DataFrame
        - annualize: if True, scale by 252
        """
        if self.covariance_method == 'ledoit':
            try:
                lw = LedoitWolf().fit(returns.dropna().values)
                cov = pd.DataFrame(lw.covariance_, index=self.ticker_list, columns=self.ticker_list)
            except Exception:
                cov = returns.cov()
        else:
            cov = returns.cov()

        if annualize:
            cov = cov * 252
        return cov

    
    def calculate_market_implied_returns(self) -> pd.Series:
        """
        Calculate market-implied returns using the CAPM reverse-solving method.
        
        Formula: Π = λ * Σ * w_m
        
        Where:
        - Π = market-implied excess returns
        - λ = risk aversion coefficient
        - Σ = covariance matrix
        - w_m = market weights
        """
        implied_returns = self.lambda_risk * (self.cov_matrix / 252).dot(self.market_weights)
        logger.debug(f"Calculated Market-Implied Returns for {len(self.ticker_list)} assets.")
        return implied_returns
    
    def set_investor_views(self, views_dict: Dict[str, float], confidence_levels: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Set investor views for the Black-Litterman model.
        
        Parameters:
        -----------
        views_dict : dict
            Dictionary of views, e.g., {'AAPL': 0.08, 'MSFT': 0.10}
            Values are expected returns (annualized)
        confidence_levels : dict or float
            Confidence in views (0-1). Default: 0.25 for all views
        """
        self.bl_views = views_dict
        
        if confidence_levels is None:
            confidence_levels = {ticker: 0.25 for ticker in views_dict.keys()}
        elif isinstance(confidence_levels, (int, float)):
            confidence_levels = {ticker: confidence_levels for ticker in views_dict.keys()}
        
        logger.debug(f"Applied Investor Views: {len(views_dict)} active views.")
        return confidence_levels
    
    def apply_black_litterman(self, views_dict: Dict[str, float], confidence_levels: Optional[Dict[str, float]] = None, tau: Optional[float] = None, cov_matrix: Optional[pd.DataFrame] = None) -> pd.Series:
        """
        Apply the Black-Litterman model to combine market-implied returns with views.
        
        Formula:
        E(R) = [τΣ^(-1) + P^T Ω^(-1) P]^(-1) [τΣ^(-1) Π + P^T Ω^(-1) Q]
        
        Where:
        - τ = tau (scaling factor)
        - Σ = covariance matrix
        - P = view matrix
        - Q = view return vector
        - Ω = uncertainty matrix (diagonal)
        - Π = market-implied returns
        """
        # Market-implied returns
        if tau is None:
            tau = self.tau

        if cov_matrix is None:
            cov_matrix = self.cov_matrix

        implied_returns = self.calculate_market_implied_returns()
        
        # If no views provided, return market-implied returns
        if not views_dict or len(views_dict) == 0:
            logger.info("No views provided. Black-Litterman defaulting purely to Market Equilibrium returns.")
            self.bl_returns = implied_returns
            return implied_returns
        
        # Investor views
        conf_levels = self.set_investor_views(views_dict, confidence_levels)
        
        # Build view matrix P and view returns Q
        P = np.zeros((len(views_dict), len(self.ticker_list)))
        Q = np.zeros(len(views_dict))
        
        view_tickers = list(views_dict.keys())
        for i, ticker in enumerate(view_tickers):
            idx = self.ticker_list.index(ticker)
            P[i, idx] = 1.0
            Q[i] = views_dict[ticker]
        
        # Uncertainty matrix Ω (diagonal)
        omega = np.zeros((len(views_dict), len(views_dict)))
        for i, ticker in enumerate(view_tickers):
            conf = conf_levels[ticker]
            # Uncertainty is inversely proportional to confidence
            omega[i, i] = (1 - conf) / conf
        
        # Black-Litterman formula (respect units carefully)
        inv_cov = np.linalg.inv(cov_matrix)

        left_matrix = np.linalg.inv(
            (1.0 / tau) * inv_cov + P.T @ np.linalg.inv(omega) @ P
        )

        right_vector = ((1.0 / tau) * inv_cov @ implied_returns + 
                       P.T @ np.linalg.inv(omega) @ Q)

        bl_returns = left_matrix @ right_vector
        logger.info(f"Black-Litterman Posterior Returns computed successfully.")
        
        self.bl_returns = bl_returns
        return bl_returns
    
    def optimize_portfolio(self, expected_returns: pd.Series, min_weight: float = 0, max_weight: float = 1) -> np.ndarray:
        """
        Optimize portfolio weights to maximize Sharpe Ratio.
        
        Objective: max (E(R_p) - R_f) / σ_p
        
        Subject to:
        - Σ w_i = 1
        - min_weight ≤ w_i ≤ max_weight
        """
        n_assets = len(expected_returns)
        
        # Objective: negative Sharpe ratio (minimize) + L2 Regularization
        # Regularization encourages more diversified weights instead of just hugging min/max constraints
        l2_lambda = 20.0  # Strong diversification penalty required to counteract huge historical outperformance of single assets
        
        def objective(weights):
            portfolio_return = np.sum(weights * expected_returns)
            portfolio_vol = np.sqrt(weights @ self.cov_matrix @ weights)
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol
            
            # L2 penalty: sum of squared weights. Minimizing negative sharpe + l2 penalty 
            # forces the optimizer to prefer smaller, more distributed weights where possible
            l2_penalty = l2_lambda * np.sum(weights**2)
            
            return -sharpe_ratio + l2_penalty
        
        # Constraints
        constraints = (
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # weights sum to 1
        )
        
        # Bounds
        bounds = tuple((min_weight, max_weight) for _ in range(n_assets))
        
        # Initial guess
        x0 = np.array([1/n_assets] * n_assets)
        
        # Optimize
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, 
                         constraints=constraints, options={'ftol': 1e-9})
        
        return result.x
    
    def get_portfolio_metrics(self, weights: np.ndarray, returns: Optional[pd.Series] = None) -> Dict[str, float]:
        """
        Calculate comprehensive portfolio risk metrics.
        
        Returns:
        --------
        dict : Dictionary containing Sharpe ratio, volatility, VaR, CVaR, etc.
        """
        if returns is None:
            returns = self.bl_returns
        
        # Basic metrics
        # Note: If `returns` are daily unannualized (like bl_returns), we must annualize them here
        # to match the scale of the annualized Volatility derived from the covariance matrix.
        # Check an arbitrary asset's expected return to guess if it's already annualized or daily.
        is_annualized = np.mean(returns) > 0.01  # True if average return > 1% (annualized scale)
        annualization_factor = 252 if not is_annualized else 1
        
        portfolio_return = np.sum(weights * returns) * annualization_factor
        portfolio_vol = np.sqrt(weights @ self.cov_matrix @ weights) # Covariance matrix is already annualized
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol
        
        # Calculate portfolio daily returns for risk metrics
        portfolio_daily_returns = (self.returns @ weights).values
        
        # Value at Risk (95%)
        var_95 = np.percentile(portfolio_daily_returns, 5)
        
        # Conditional Value at Risk (95%)
        cvar_95 = portfolio_daily_returns[portfolio_daily_returns <= var_95].mean()
        
        # Maximum Drawdown
        cumulative_returns = (1 + portfolio_daily_returns).cumprod()
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdown)
        
        metrics = {
            'Expected Return': portfolio_return,
            'Volatility': portfolio_vol,
            'Sharpe Ratio': sharpe_ratio,
            'VaR (95%)': var_95,
            'CVaR (95%)': cvar_95,
            'Max Drawdown': max_drawdown
        }
        
        return metrics
    
    def compare_models(self, views_dict: Dict[str, float], confidence_levels: Optional[Dict[str, float]] = None, 
                       max_weight: Optional[float] = None, min_weight: float = 0.05) -> Dict[str, Any]:
        """
        Compare Markowitz Mean-Variance with Black-Litterman model.
        
        Returns:
        --------
        dict : Comparison results including weights and metrics
        """
        print("\n" + "="*60)
        print("PORTFOLIO COMPARISON")
        print("="*60)
        
        # Ensure views use mapped names to match self.ticker_list
        if self.name_mapping and views_dict:
            mapped_views = {self.name_mapping.get(k, k): v for k, v in views_dict.items()}
            views_dict = mapped_views
            
            if confidence_levels and isinstance(confidence_levels, dict):
                mapped_conf = {self.name_mapping.get(k, k): v for k, v in confidence_levels.items()}
                confidence_levels = mapped_conf
        
        
        if max_weight is None:
            n_assets = len(self.ticker_list)
            max_weight = min(1.0, max(0.3, 2.0 / n_assets))
            
        logger.debug(f"Applying constraints - Min: {min_weight:.1%}, Max: {max_weight:.1%} per asset")
        
        # Markowitz optimization (using historical mean returns)
        markowitz_weights = self.optimize_portfolio(self.historical_mean, min_weight=min_weight, max_weight=max_weight)
        markowitz_metrics = self.get_portfolio_metrics(markowitz_weights, self.historical_mean)
        
        # Black-Litterman optimization
        bl_returns = self.apply_black_litterman(views_dict, confidence_levels)
        bl_weights = self.optimize_portfolio(bl_returns, min_weight=min_weight, max_weight=max_weight)
        bl_metrics = self.get_portfolio_metrics(bl_weights, bl_returns)
        
        # Equal-weight portfolio (benchmark)
        equal_weights = np.array([1/len(self.ticker_list)] * len(self.ticker_list))
        equal_metrics = self.get_portfolio_metrics(equal_weights, bl_returns)
        
        logger.info("Successfully computed matrices for Markowitz, Black-Litterman, and Equal-Weight benchmark models.")
        
        return {
            'markowitz': {
                'weights': markowitz_weights,
                'metrics': markowitz_metrics
            },
            'black_litterman': {
                'weights': bl_weights,
                'metrics': bl_metrics,
                'expected_returns': list(bl_returns)
            },
            'equal_weight': {
                'weights': equal_weights,
                'metrics': equal_metrics
            }
        }

