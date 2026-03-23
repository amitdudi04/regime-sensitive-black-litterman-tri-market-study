"""
Backtesting Module for Black-Litterman Portfolio Optimization
==============================================================

Implements rolling window backtesting and performance evaluation.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Optional
import yfinance as yf
import os
import warnings
import logging

logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')


class PortfolioBacktester:
    """Backtesting framework for portfolio optimization strategies."""
    
    def __init__(self, optimizer, window_size=252, rebalance_freq=63, 
                 transaction_cost_rate=0.001, slippage_rate=0.0005):
        """
        Initialize backtester.
        
        Parameters:
        -----------
        optimizer : BlackLittermanOptimizer
            The optimizer object
        window_size : int
            Training window size in days (252 = 1 year)
        rebalance_freq : int
            Rebalancing frequency in days (63 ≈ 1 quarter)
        transaction_cost_rate : float
            Fixed proportional cost per trade (default: 10 bps)
        slippage_rate : float
            Estimated slippage per trade (default: 5 bps)
        """
        self.optimizer = optimizer
        self.window_size = window_size
        self.rebalance_freq = rebalance_freq
        self.tc_rate = transaction_cost_rate
        self.slip_rate = slippage_rate
        self.total_trade_cost_rate = self.tc_rate + self.slip_rate
        self.returns = optimizer.returns
        
        self.backtest_results = {
            'markowitz': {'gross': [], 'net': []},
            'black_litterman': {'gross': [], 'net': []},
            'equal_weight': {'gross': [], 'net': []},
            'turnover': {
                'markowitz': [],
                'black_litterman': [],
                'equal_weight': []
            },
            'cost_impact': {}
        }
        
        # Weight history: list of (date, weight_vector) per model
        self.weight_history = {
            'markowitz': [],
            'black_litterman': [],
            'equal_weight': []
        }

        # Concentration per rebalance
        self.concentration = {
            'markowitz': [],
            'black_litterman': [],
            'equal_weight': []
        }

        # Tau timeline (one value per rebalance)
        self.tau_timeline = []

        self.rebalance_dates = []
    
    def _calculate_returns_vol(self, returns_window):
        """Calculate expected returns and volatility from returns window."""
        mean_returns = returns_window.mean() * 252
        # Use optimizer's covariance estimator if available (Ledoit-Wolf option)
        try:
            cov_matrix = self.optimizer._compute_covariance(returns_window, annualize=True)
        except Exception:
            cov_matrix = returns_window.cov() * 252
        return mean_returns, cov_matrix
    
    def _optimize_weights(self, mean_returns, cov_matrix, method='markowitz'):
        """Optimize portfolio weights."""
        n_assets = len(mean_returns)
        risk_free_rate = self.optimizer.risk_free_rate
        
        def neg_sharpe(weights):
            ret = np.sum(weights * mean_returns)
            vol = np.sqrt(weights @ cov_matrix @ weights)
            return -(ret - risk_free_rate) / vol
        
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))
        x0 = np.array([1/n_assets] * n_assets)
        
        result = minimize(neg_sharpe, x0, method='SLSQP', bounds=bounds,
                         constraints=constraints, options={'ftol': 1e-9})
        
        return result.x
    
    def run_backtest(self, views_dict=None):
        """
        Run rolling window backtest.
        
        Parameters:
        -----------
        views_dict : dict
            Investor views for Black-Litterman model
        """
        logger.info("\n" + "="*60)
        logger.info("BACKTESTING: ROLLING WINDOW ANALYSIS")
        logger.info("="*60)
        logger.info(f"Window size: {self.window_size} days")
        logger.info(f"Rebalance frequency: {self.rebalance_freq} days")
        
        # Default views if not provided
        if views_dict is None:
            views_dict = {
                self.optimizer.ticker_list[0]: 0.12,
                self.optimizer.ticker_list[1]: 0.10
            }
        
        # Store entire daily trajectory logic, not single averaged numbers per period
        # Tracking both Gross (Before Fees) and Net (After Fees)
        markowitz_daily_gross = pd.Series(dtype=float)
        markowitz_daily_net = pd.Series(dtype=float)
        
        bl_daily_gross = pd.Series(dtype=float)
        bl_daily_net = pd.Series(dtype=float)
        
        equal_daily_gross = pd.Series(dtype=float)
        equal_daily_net = pd.Series(dtype=float)
        
        # Track the raw weights over time for deeper turnover analysis
        prev_mw_weights = None
        prev_bl_weights = None
        prev_eq_weights = None
        
        mw_turnover_history = []
        bl_turnover_history = []
        eq_turnover_history = []
        
        test_dates = []
        rebalance_dates = []
        
        # Rolling window
        # prev_test_cum_returns holds cumulative returns per asset for the previous test window
        prev_test_cum_returns = None

        for i in range(self.window_size, len(self.returns), self.rebalance_freq):
            
            # Training window
            train_window = self.returns.iloc[i-self.window_size:i]
            
            if len(train_window) < self.window_size:
                break
            
            # Test window
            test_start = i
            test_end = min(i + self.rebalance_freq, len(self.returns))
            test_window = self.returns.iloc[test_start:test_end]
            
            if len(test_window) == 0:
                break
            
            # Calculate statistics from training window
            mean_returns, cov_matrix = self._calculate_returns_vol(train_window)

            # Regime detection: rolling 60-day volatility
            # Compute 60-day rolling vol per asset inside training window
            try:
                rolling60 = train_window.rolling(window=60).std()
                # Last observed 60-day vol (annualized)
                last60 = rolling60.iloc[-1].mean() * np.sqrt(252)
                median60 = rolling60.median().mean() * np.sqrt(252)
            except Exception:
                last60 = np.sqrt(np.diag(cov_matrix)).mean()
                median60 = last60

            # Regime-sensitive tau
            tau_high_vol = 0.01
            tau_low_vol = 0.05
            if last60 > median60:
                tau = tau_high_vol
            else:
                tau = tau_low_vol
            
            # Markowitz optimization (using current covariance)
            markowitz_weights = self._optimize_weights(mean_returns, cov_matrix, 
                                                       method='markowitz')
            
            # Equal-weight portfolio
            equal_weights = np.array([1/len(self.optimizer.ticker_list)] * 
                                    len(self.optimizer.ticker_list))
            
            # Black-Litterman: use optimizer's BL routine with dynamic tau and the period covariance
            # Ensure ticker order matches expected index for views
            # Temporarily set optimizer covariance to period cov so that optimization uses correct risk
            prev_cov = getattr(self.optimizer, 'cov_matrix', None)
            try:
                self.optimizer.cov_matrix = cov_matrix
                bl_returns = self.optimizer.apply_black_litterman(views_dict, confidence_levels=None, tau=tau, cov_matrix=cov_matrix)
                bl_weights = self.optimizer.optimize_portfolio(bl_returns, min_weight=0.0, max_weight=1.0)
            finally:
                # restore previous covariance
                if prev_cov is not None:
                    self.optimizer.cov_matrix = prev_cov
            # Calculate Drift-Adjusted Turnover vs Previous Weights
            def _drift_adjusted_turnover(new_w, prev_w, prev_cum_returns):
                if prev_w is None or prev_cum_returns is None:
                    return float(np.sum(np.abs(new_w)))
                # Adjust previous weights by growth over the holding period
                prev_adj = prev_w * prev_cum_returns
                # Normalize to ensure full investment
                s = prev_adj.sum()
                if s == 0:
                    prev_adj = prev_w
                else:
                    prev_adj = prev_adj / s
                return float(np.sum(np.abs(new_w - prev_adj)))

            mw_turnover = _drift_adjusted_turnover(markowitz_weights, prev_mw_weights, prev_test_cum_returns)
            bl_turnover = _drift_adjusted_turnover(bl_weights, prev_bl_weights, prev_test_cum_returns)
            eq_turnover = _drift_adjusted_turnover(equal_weights, prev_eq_weights, prev_test_cum_returns)

            mw_turnover_history.append(mw_turnover)
            bl_turnover_history.append(bl_turnover)
            eq_turnover_history.append(eq_turnover)

            # Save state for next rolling window
            prev_mw_weights = markowitz_weights
            prev_bl_weights = bl_weights
            prev_eq_weights = equal_weights
            # compute cumulative returns over this test window to be used at next rebalance
            try:
                prev_test_cum_returns = (1 + test_window).prod().values
            except Exception:
                prev_test_cum_returns = None

            # record weight histories and concentrations aligned with rebalance date (start of test window)
            rebalance_date = test_window.index[0]
            self.rebalance_dates.append(rebalance_date)
            self.weight_history['markowitz'].append((rebalance_date, markowitz_weights))
            self.weight_history['black_litterman'].append((rebalance_date, bl_weights))
            self.weight_history['equal_weight'].append((rebalance_date, equal_weights))

            self.concentration['markowitz'].append(np.sum(markowitz_weights**2))
            self.concentration['black_litterman'].append(np.sum(bl_weights**2))
            self.concentration['equal_weight'].append(np.sum(equal_weights**2))

            # store tau
            self.tau_timeline.append(tau)
            
            # Calculate Transaction Costs
            mw_cost = mw_turnover * self.total_trade_cost_rate
            bl_cost = bl_turnover * self.total_trade_cost_rate
            eq_cost = eq_turnover * self.total_trade_cost_rate
            
            # Calculate ACTUAL out-of-sample daily returns instead of purely average means
            # Dot product of daily asset returns matrix (periods x assets) with weights (assets)
            mw_daily = test_window.dot(markowitz_weights)
            bl_daily = test_window.dot(bl_weights)
            eq_daily = test_window.dot(equal_weights)
            
            # Copy to Net and systematically deduct the rebalance cost from the FIRST DAY of the window
            mw_window_net = mw_daily.copy()
            bl_window_net = bl_daily.copy()
            eq_window_net = eq_daily.copy()
            
            mw_window_net.iloc[0] -= mw_cost
            bl_window_net.iloc[0] -= bl_cost
            eq_window_net.iloc[0] -= eq_cost
            
            # Append pandas Series maintaining index dates
            markowitz_daily_gross = pd.concat([markowitz_daily_gross, mw_daily])
            markowitz_daily_net = pd.concat([markowitz_daily_net, mw_window_net])
            
            bl_daily_gross = pd.concat([bl_daily_gross, bl_daily])
            bl_daily_net = pd.concat([bl_daily_net, bl_window_net])
            
            equal_daily_gross = pd.concat([equal_daily_gross, eq_daily])
            equal_daily_net = pd.concat([equal_daily_net, eq_window_net])
            
            test_dates.append(test_window.index[-1])
            rebalance_dates.append(test_window.index[0])
        
        self.backtest_results = {
            'markowitz': {
                'gross': markowitz_daily_gross.loc[~markowitz_daily_gross.index.duplicated(keep='last')], 
                'net': markowitz_daily_net.loc[~markowitz_daily_net.index.duplicated(keep='last')]
            },
            'black_litterman': {
                'gross': bl_daily_gross.loc[~bl_daily_gross.index.duplicated(keep='last')], 
                'net': bl_daily_net.loc[~bl_daily_net.index.duplicated(keep='last')]
            },
            'equal_weight': {
                'gross': equal_daily_gross.loc[~equal_daily_gross.index.duplicated(keep='last')], 
                'net': equal_daily_net.loc[~equal_daily_net.index.duplicated(keep='last')]
            },
            'turnover': {
                'markowitz': pd.Series(mw_turnover_history, index=rebalance_dates),
                'black_litterman': pd.Series(bl_turnover_history, index=rebalance_dates),
                'equal_weight': pd.Series(eq_turnover_history, index=rebalance_dates)
            },
            'cost_impact': {},
            'dates': test_dates,
            'overall_dates': markowitz_daily_gross.loc[~markowitz_daily_gross.index.duplicated(keep='last')].index # Expose the full timeline
        }
        # Build DataFrames for weight histories and compute ASI / concentration series
        weight_history_dfs = {}
        asi_metrics = {}
        asi_series_dict = {}
        turnover_metrics = {}
        for model_name in ['markowitz', 'black_litterman', 'equal_weight']:
            entries = self.weight_history.get(model_name, [])
            if entries:
                dates = [d for d, w in entries]
                arr = np.vstack([w for d, w in entries])
                df = pd.DataFrame(arr, index=pd.DatetimeIndex(dates), columns=self.optimizer.ticker_list)
            else:
                df = pd.DataFrame(columns=self.optimizer.ticker_list)
            weight_history_dfs[model_name] = df

            # ASI: mean L1 distance between consecutive rebalanced weights
            if not df.empty:
                print("ASI computed using L1 norm weight drift")
                weights_diff = df.diff()
                asi_series = weights_diff.abs().sum(axis=1)
                asi = float(asi_series.mean())
                concentration_series = pd.Series(self.concentration.get(model_name, []), index=df.index)
                turnover_series = pd.Series(self.backtest_results['turnover'][model_name].values, index=df.index)
            else:
                asi = np.nan
                concentration_series = pd.Series(dtype=float)
                turnover_series = pd.Series(dtype=float)

            asi_metrics[model_name] = float(asi) if not np.isnan(asi) else np.nan
            asi_series_dict[model_name] = asi_series
            turnover_metrics[model_name] = turnover_series

        # Attach weight history DataFrames and ASI/turnover/concentration to results
        self.backtest_results['weight_history'] = weight_history_dfs
        self.backtest_results['asi'] = asi_metrics
        self.backtest_results['asi_series'] = asi_series_dict
        self.backtest_results['turnover_series'] = turnover_metrics
        self.backtest_results['concentration'] = {m: pd.Series(self.concentration.get(m, []), index=weight_history_dfs[m].index) if not weight_history_dfs[m].empty else pd.Series(dtype=float) for m in weight_history_dfs}
        self.backtest_results['tau_timeline'] = pd.Series(self.tau_timeline, index=pd.DatetimeIndex(self.rebalance_dates)) if self.rebalance_dates else pd.Series(dtype=float)

        # Export CSVs for weight histories, ASI and turnover
        try:
            results_dir = os.path.join(os.getcwd(), 'results')
            os.makedirs(results_dir, exist_ok=True)
            for model_name, df in weight_history_dfs.items():
                if not df.empty:
                    df.to_csv(os.path.join(results_dir, f'weight_history_{model_name}.csv'))

            # ASI metrics
            asi_df = pd.DataFrame([{'model': k, 'asi': v} for k, v in asi_metrics.items()])
            asi_df.to_csv(os.path.join(results_dir, 'asi_metrics.csv'), index=False)

            # Turnover metrics: one CSV with columns per model
            all_turnover = pd.concat(turnover_metrics, axis=1)
            if not all_turnover.empty:
                all_turnover.columns = [c for c in all_turnover.columns]
                all_turnover.to_csv(os.path.join(results_dir, 'turnover_metrics.csv'))
        except Exception:
            logger.warning('Could not export weight/asi/turnover CSVs.')
        
        logger.info(f"\nBacktest periods: {len(test_dates)}")
        self._print_backtest_summary()
        
        return self.backtest_results
    
    def _print_backtest_summary(self):
        """Print summary statistics from backtest based on daily return series."""
        
        logger.info("\n" + "-"*60)
        logger.info("BACKTEST SUMMARY STATISTICS (Net Annualized)")
        logger.info("-"*60)
        
        for model_name in ['markowitz', 'black_litterman', 'equal_weight']:
            daily_gross = self.backtest_results[model_name]['gross']
            daily_net = self.backtest_results[model_name]['net']
            
            # Annualize metrics
            mean_gross = daily_gross.mean() * 252
            mean_net = daily_net.mean() * 252
            std_net = daily_net.std() * np.sqrt(252)
            
            # Cost Impact
            annual_cost_drag = mean_gross - mean_net
            self.backtest_results['cost_impact'][model_name] = annual_cost_drag
            
            # Drawdown calculation
            cum_returns = (1 + daily_net).cumprod()
            rolling_max = cum_returns.cummax()
            drawdowns = (cum_returns - rolling_max) / rolling_max
            max_drawdown = drawdowns.min()
            
            win_rate = (daily_net > 0).sum() / len(daily_net) * 100
            
            # Turnover
            avg_turnover = self.backtest_results['turnover'][model_name].mean()
            
            logger.info(f"\n{model_name.upper().replace('_', ' ')}")
            logger.info(f"  Gross Annual Return: {mean_gross:8.4%}")
            logger.info(f"  Net Annual Return:   {mean_net:8.4%}")
            logger.info(f"  Annual Volatility:   {std_net:8.4%}")
            logger.info(f"  Cost Drag (bps/yr):  {annual_cost_drag * 10000:8.1f}")
            logger.info(f"  Avg Rebal Turnover:  {avg_turnover:8.4%}")
            logger.info(f"  Max Drawdown:        {max_drawdown:8.4%}")
            logger.info(f"  Daily Win Rate:      {win_rate:8.1f}%")
    
    def calculate_information_ratio(self, benchmark_returns):
        """
        Calculate Information Ratio vs. benchmark using daily net series.
        
        IR = (Portfolio Return - Benchmark Return) / Tracking Error
        (Annualized)
        """
        
        results = {}
        
        for model_name in ['markowitz', 'black_litterman']:
            model_returns = self.backtest_results[model_name]['net']
            
            # Align indices in case of missing data
            aligned = pd.concat([model_returns, benchmark_returns], axis=1).dropna()
            mod_ret = aligned.iloc[:, 0]
            bench_ret = aligned.iloc[:, 1]
            
            active_returns = mod_ret - bench_ret
            # Annualize tracking error
            tracking_error = active_returns.std() * np.sqrt(252)
            
            if tracking_error == 0:
                ir = 0
            else:
                # Annualized active return over annualized tracking error
                annual_active_ret = active_returns.mean() * 252
                ir = annual_active_ret / tracking_error
            
            results[model_name] = {
                'information_ratio': ir,
                'active_return': active_returns.mean() * 252,
                'tracking_error': tracking_error
            }
        
        return results
    
    def calculate_sharpe_ratios(self):
        """Calculate Sharpe ratio for each model during backtest (Annualized)."""
        
        results = {}
        risk_free_rate_daily = self.optimizer.risk_free_rate / 252 
        
        for model_name in ['markowitz', 'black_litterman', 'equal_weight']:
            daily_returns = self.backtest_results[model_name]['net']
            
            excess_returns = daily_returns - risk_free_rate_daily
            # Annualize Sharpe: Multiply daily Sharpe by sqrt(252)
            sharpe = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
            
            results[model_name] = sharpe
        
        return results

    def fetch_and_align_benchmarks(self):
        """Fetch ^GSPC, 000001.SS, and ^BSESN from yfinance and align to backtest dates."""
        start_date = self.backtest_results['overall_dates'][0].strftime('%Y-%m-%d')
        end_date = self.backtest_results['overall_dates'][-1].strftime('%Y-%m-%d')
        
        logger.info("\nFetching benchmark data (S&P 500, Shanghai Comp, BSE Sensex)...")
        # Add 1 day buffer to end_date for yf to catch the last day
        fetch_end = (self.backtest_results['overall_dates'][-1] + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        bench_data = yf.download(['^GSPC', '000001.SS', '^BSESN'], start=start_date, end=fetch_end, progress=False)
        
        # Calculate daily returns
        if isinstance(bench_data.columns, pd.MultiIndex):
            top_level = bench_data.columns.get_level_values(0)
            if 'Adj Close' in top_level:
                bench_prices = bench_data['Adj Close']
            else:
                bench_prices = bench_data['Close']
        else:
            if 'Adj Close' in bench_data.columns:
                bench_prices = bench_data['Adj Close']
            else:
                bench_prices = bench_data['Close']
                
        bench_prices.fillna(method='ffill', inplace=True)
        bench_returns = bench_prices.pct_change().dropna()
        
        # Align to our portfolio out-of-sample timeline exactly
        sp500 = bench_returns['^GSPC'].reindex(self.backtest_results['overall_dates']).fillna(0)
        csi300 = bench_returns['000001.SS'].reindex(self.backtest_results['overall_dates']).fillna(0)
        sensex = bench_returns['^BSESN'].reindex(self.backtest_results['overall_dates']).fillna(0)
        
        self.backtest_results['sp500'] = sp500
        self.backtest_results['csi300'] = csi300
        self.backtest_results['sensex'] = sensex
        return sp500, csi300, sensex


def run_comprehensive_backtest(optimizer, views_dict=None, transaction_cost=0.001, rebalance_freq=63):
    """
    Run comprehensive backtesting analysis.
    
    Parameters:
    -----------
    optimizer : BlackLittermanOptimizer
        The optimizer object
    views_dict : dict
        Investor views for Black-Litterman
    transaction_cost : float
    rebalance_freq : int
    """
    backtester = PortfolioBacktester(
        optimizer, 
        rebalance_freq=rebalance_freq, 
        transaction_cost_rate=transaction_cost
    )
    backtest_results = backtester.run_backtest(views_dict)
    
    # Fetch real-world benchmarks
    sp500, csi300, sensex = backtester.fetch_and_align_benchmarks()
    
    # Calculate additional metrics against SP500 instead of equal weight
    ir_results = backtester.calculate_information_ratio(sp500)
    sharpe_results = backtester.calculate_sharpe_ratios()
    
    logger.info("\n" + "="*60)
    logger.info("INFORMATION RATIO (vs S&P 500)")
    logger.info("="*60)
    
    for model_name, metrics in ir_results.items():
        logger.info(f"\n{model_name.upper().replace('_', ' ')}")
        logger.info(f"  Information Ratio:  {metrics['information_ratio']:8.4f}")
        logger.info(f"  Active Return:      {metrics['active_return']:8.4%}")
        logger.info(f"  Tracking Error:     {metrics['tracking_error']:8.4%}")
    
    logger.info("\n" + "="*60)
    logger.info("SHARPE RATIOS (Out-of-Sample, Annualized)")
    logger.info("="*60)
    
    for model_name, sharpe in sharpe_results.items():
        logger.info(f"{model_name.upper().replace('_', ' '):20s}: {sharpe:8.4f}")
        
    return backtest_results, ir_results, sharpe_results
