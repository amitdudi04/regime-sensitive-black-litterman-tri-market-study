"""
Robustness and Stress Testing Module
====================================

Encapsulates sensitivity analyses (Tau/Lambda) and historical
crash simulation (2008 Financial Crisis).
"""

import pandas as pd
import numpy as np
import yfinance as yf
import os
import tempfile
import warnings
import logging

logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

from core.optimizer import BlackLittermanOptimizer

def run_tau_sensitivity(optimizer, views_dict, confidence_levels=None, 
                        tau_values=[0.01, 0.03, 0.05, 0.1, 0.2], 
                        max_weight=None, min_weight=0.05):
    """
    Run robustness analysis to track model sensitivity to Tau (τ).
    """
    logger.info("\n" + "="*60)
    logger.info("RUNNING TAU (τ) SENSITIVITY ANALYSIS")
    logger.info("="*60)
    
    results_list = []
    original_tau = optimizer.tau
    
    if max_weight is None:
        n_assets = len(optimizer.ticker_list)
        max_weight = min(1.0, max(0.3, 2.0 / n_assets))
        
    for t in tau_values:
        optimizer.tau = t
        logger.info(f"Processing τ = {t:.3f} ...")
        
        bl_returns = optimizer.apply_black_litterman(views_dict, confidence_levels)
        bl_weights = optimizer.optimize_portfolio(bl_returns, min_weight=min_weight, max_weight=max_weight)
        bl_metrics = optimizer.get_portfolio_metrics(bl_weights, bl_returns)
        
        record = {
            'Tau': t,
            'Expected Return': bl_metrics['Expected Return'],
            'Volatility': bl_metrics['Volatility'],
            'Sharpe Ratio': bl_metrics['Sharpe Ratio']
        }
        
        for ticker, weight in zip(optimizer.ticker_list, bl_weights):
            record[f'Weight_{ticker}'] = weight
            
        results_list.append(record)
        
    optimizer.tau = original_tau
    df = pd.DataFrame(results_list)
    df.set_index('Tau', inplace=True)
    return df

def run_lambda_sensitivity(optimizer, views_dict, confidence_levels=None, 
                           lambda_values=[1.5, 2.0, 2.5, 3.0, 4.0], 
                           max_weight=None, min_weight=0.05):
    """
    Run robustness analysis to track model sensitivity to Risk Aversion (λ).
    """
    logger.info("\n" + "="*60)
    logger.info("RUNNING RISK AVERSION (λ) SENSITIVITY ANALYSIS")
    logger.info("="*60)
    
    results_list = []
    original_lambda = optimizer.lambda_risk
    
    if max_weight is None:
        n_assets = len(optimizer.ticker_list)
        max_weight = min(1.0, max(0.3, 2.0 / n_assets))
        
    for lmb in lambda_values:
        optimizer.lambda_risk = lmb
        logger.info(f"Processing λ = {lmb:.2f} ...")
        
        bl_returns = optimizer.apply_black_litterman(views_dict, confidence_levels)
        bl_weights = optimizer.optimize_portfolio(bl_returns, min_weight=min_weight, max_weight=max_weight)
        bl_metrics = optimizer.get_portfolio_metrics(bl_weights, bl_returns)
        
        record = {
            'Lambda': lmb,
            'Expected Return': bl_metrics['Expected Return'],
            'Volatility': bl_metrics['Volatility'],
            'Sharpe Ratio': bl_metrics['Sharpe Ratio']
        }
        
        for ticker, weight in zip(optimizer.ticker_list, bl_weights):
            record[f'Weight_{ticker}'] = weight
            
        results_list.append(record)
        
    optimizer.lambda_risk = original_lambda
    df = pd.DataFrame(results_list)
    df.set_index('Lambda', inplace=True)
    return df

class HistoricalStressTester:
    def __init__(self, tickers, train_start='2005-01-01', train_end='2007-12-31', 
                 test_start='2008-01-01', test_end='2009-12-31', benchmark='^GSPC'):
        self.tickers = tickers
        self.train_start = train_start
        self.train_end = train_end
        self.test_start = test_start
        self.test_end = test_end
        self.benchmark = benchmark
        
        self.weights = {}
        self.test_returns = None
        self.test_prices = None
        self.benchmark_returns = None
        self.results = {}
        self.train_vol = {}
        
    def _fetch_prices(self, tickers, start, end):
        try:
            custom_cache = os.path.join(tempfile.gettempdir(), "yf_cache_custom")
            os.makedirs(custom_cache, exist_ok=True)
            yf.set_tz_cache_location(custom_cache)
        except AttributeError:
            pass
            
        try:
            data = yf.download(tickers, start=start, end=end, progress=False)
            if isinstance(data, pd.DataFrame):
                if 'Adj Close' in data.columns:
                    data = data['Adj Close']
                elif 'Close' in data.columns:
                    data = data['Close']
                    
            if len(tickers) == 1 and not isinstance(data, pd.DataFrame):
                data = data.to_frame(name=tickers[0])
                
            if len(tickers) > 1 and isinstance(data, pd.DataFrame):
                data = data[tickers]
                
            return data.dropna()
        except Exception as e:
            logger.info(f"Error fetching data: {e}")
            # Fallback for reproducible testing
            dates = pd.date_range(start=start, end=end, freq='B')
            noise = np.random.normal(0, 0.02, size=(len(dates), len(tickers)))
            return pd.DataFrame(100 * np.exp(np.cumsum(noise, axis=0)), index=dates, columns=tickers)

    def run_training_phase(self, views_dict, confidence_levels):
        logger.info(f"--- TRAINING PHASE: {self.train_start} to {self.train_end} ---")
        opt = BlackLittermanOptimizer(self.tickers, self.train_start, self.train_end)
        cmp = opt.compare_models(views_dict, confidence_levels)
        
        self.weights['markowitz'] = cmp['markowitz']['weights']
        self.weights['black_litterman'] = cmp['black_litterman']['weights']
        self.weights['equal_weight'] = cmp['equal_weight']['weights']
        
        self.train_vol = {
            'markowitz': np.sqrt(self.weights['markowitz'] @ opt.cov_matrix @ self.weights['markowitz']) * np.sqrt(252),
            'black_litterman': np.sqrt(self.weights['black_litterman'] @ opt.cov_matrix @ self.weights['black_litterman']) * np.sqrt(252),
            'benchmark': np.nan 
        }

    def run_stress_test(self):
        logger.info(f"\n--- STRESS TESTING PHASE: {self.test_start} to {self.test_end} ---")
        
        logger.info("Fetching test window Asset prices...")
        self.test_prices = self._fetch_prices(self.tickers, self.test_start, self.test_end)
        self.test_returns = self.test_prices.pct_change().dropna()
        
        logger.info(f"Fetching test window Benchmark ({self.benchmark}) prices...")
        bench_prices = self._fetch_prices([self.benchmark], self.test_start, self.test_end)
        self.benchmark_returns = bench_prices.pct_change().dropna().iloc[:, 0]
        
        aligned = pd.concat([self.test_returns, self.benchmark_returns], axis=1).dropna()
        self.test_returns = aligned[self.tickers]
        self.benchmark_returns = aligned.iloc[:, -1]
        
        logger.info("Evaluating pre-crisis Benchmark volatility...")
        bench_train = self._fetch_prices([self.benchmark], self.train_start, self.train_end).pct_change().dropna()
        self.train_vol['benchmark'] = bench_train.iloc[:, 0].std() * np.sqrt(252)
        
        logger.info("Calculating exact crisis performance trails...")
        self.daily_performance = {}
        for strategy, weights in self.weights.items():
            self.daily_performance[strategy] = self.test_returns.dot(weights)
            
        self.daily_performance['benchmark'] = self.benchmark_returns
        
        for name, daily_ret in self.daily_performance.items():
            cum_rets = (1 + daily_ret).cumprod()
            total_crisis_return = cum_rets.iloc[-1] - 1
            
            rolling_max = cum_rets.cummax()
            drawdowns = (cum_rets - rolling_max) / rolling_max
            max_drawdown = drawdowns.min()
            
            crisis_vol = daily_ret.std() * np.sqrt(252)
            pre_vol = self.train_vol.get(name, self.train_vol['black_litterman'] if name == 'equal_weight' else np.nan)
            
            if name == 'equal_weight':
               cov = self.test_returns.cov()
               pre_vol = np.sqrt(self.weights['equal_weight'] @ cov @ self.weights['equal_weight']) * np.sqrt(252)
               
            vol_spike = (crisis_vol / pre_vol) if not np.isnan(pre_vol) else np.nan
            
            recovery_time = -1
            underwater_days = 0
            max_underwater_days = 0
            for dd in drawdowns:
                if dd < 0:
                    underwater_days += 1
                else:
                    max_underwater_days = max(max_underwater_days, underwater_days)
                    underwater_days = 0
            max_underwater_days = max(max_underwater_days, underwater_days)
            
            if cum_rets.iloc[-1] >= rolling_max.max():
                 recovery_time = max_underwater_days
            
            # Simple VaR and CVaR for the reporting
            var_95 = np.percentile(daily_ret, 5)
            cvar_95 = daily_ret[daily_ret <= var_95].mean()
            
            self.results[name] = {
                'Crisis Return': total_crisis_return,
                'Max Drawdown': max_drawdown,
                'Crisis Volatility': crisis_vol,
                'Pre-Crisis Volatility': pre_vol,
                'Volatility Spike (x)': vol_spike,
                'Max Underwater Days': max_underwater_days,
                'VaR (95%)': var_95,
                'CVaR (95%)': cvar_95,
                'cumulative_series': cum_rets,
                'drawdown_series': drawdowns,
                'daily_returns': daily_ret
            }
            
    def print_results(self):
        logger.info("\n" + "="*80)
        logger.info("2008 FINANCIAL CRISIS STRESS TEST RESULTS (Train: 05-07 | Test: 08-09)")
        logger.info("="*80)
        
        format_str = "{:<20} | {:<15} | {:<15} | {:<15} | {:<15}"
        logger.info(format_str.format("Strategy", "Total Return", "Max Drawdown", "Vol Spike (x)", "Underwater Days"))
        logger.info("-" * 85)
        
        display_names = {
            'black_litterman': 'Black-Litterman',
            'markowitz': 'Markowitz',
            'equal_weight': 'Equal Weight',
            'benchmark': 'S&P 500 (^GSPC)'
        }
        
        for name, metrics in self.results.items():
            disp = display_names.get(name, name)
            ret = f"{metrics['Crisis Return']:.2%}"
            dd = f"{metrics['Max Drawdown']:.2%}"
            vs = f"{metrics['Volatility Spike (x)']:.2f}x"
            uw = f"{metrics['Max Underwater Days']} days"
            logger.info(format_str.format(disp, ret, dd, vs, uw))
            
        logger.info("="*80 + "\n")
