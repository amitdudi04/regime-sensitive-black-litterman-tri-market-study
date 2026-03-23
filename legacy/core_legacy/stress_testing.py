import pandas as pd
import numpy as np
import yfinance as yf
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

from legacy.core_legacy.optimizer import BlackLittermanOptimizer

class HistoricalStressTester:
    def __init__(self, ticker_list, train_start='2005-01-01', train_end='2007-12-31', 
                 test_start='2008-01-01', test_end='2009-12-31', benchmark='^GSPC', name_mapping=None, global_prices=None):
        """
        Initialize stress tester with distinct pre-crisis (training) and intra-crisis (testing) windows.
        """
        self.global_prices = global_prices
        self.original_tickers = ticker_list.copy()
        self.name_mapping = name_mapping
        self.tickers = [name_mapping.get(t, t) for t in ticker_list] if name_mapping else ticker_list.copy()
        
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
        
    def _fetch_prices(self, tickers, start_date, end_date, name_mapping=None):
        """Helper to slice from the main ETF data instead of downloading separately."""
        if self.global_prices is not None:
            data = self.global_prices.copy()
            # If the user asks for benchmark and it's not in global_prices, download it only.
            if len(tickers) == 1 and tickers[0] not in data.columns:
                logger.info(f"Downloading benchmark {tickers[0]} as it's not in main dataset...")
                data = yf.download(tickers, start=start_date, end=end_date, progress=False)
                if isinstance(data.columns, pd.MultiIndex):
                    level_0 = data.columns.get_level_values(0)
                    if 'Adj Close' in level_0:
                        data = data['Adj Close']
                    else:
                        data = data['Close']
                else:
                    if 'Adj Close' in data.columns:
                        data = data['Adj Close']
                    else:
                        data = data['Close']
            else:
                try:
                    # Verify if start_date bounds exceed global_prices limitations
                    start_dt = pd.to_datetime(start_date)
                    tz_idx0 = data.index[0]
                    if start_dt.tz_localize(None) < tz_idx0.tz_localize(None):
                        logger.info(f"Requested start date {start_date} predates global dataset. Fetching live API data...")
                        downloaded = yf.download(tickers, start=start_date, end=end_date, progress=False)
                        if isinstance(downloaded.columns, pd.MultiIndex):
                            level_0 = downloaded.columns.get_level_values(0)
                            if 'Adj Close' in level_0:
                                downloaded = downloaded['Adj Close']
                            else:
                                downloaded = downloaded['Close']
                        else:
                            if 'Adj Close' in downloaded.columns:
                                downloaded = downloaded['Adj Close']
                            else:
                                downloaded = downloaded['Close']
                                
                        valid_cols = [c for c in tickers if c in downloaded.columns]
                        data = downloaded.loc[:, valid_cols]
                    else:
                        data = data.loc[start_date:end_date, tickers]
                except KeyError:
                    # In case of missing columns, just take intersection
                    valid_cols = [c for c in tickers if c in data.columns]
                    data = data.loc[start_date:end_date, valid_cols]
        else:
            # Fallback legacy mode if no global_prices supplied
            data = yf.download(tickers, start=start_date, end=end_date, progress=False)
            if isinstance(data.columns, pd.MultiIndex):
                level_0 = data.columns.get_level_values(0)
                if 'Adj Close' in level_0:
                    data = data['Adj Close']
                else:
                    data = data['Close']
            else:
                if 'Adj Close' in data.columns:
                    data = data['Adj Close']
                else:
                    data = data['Close']
                    
        if isinstance(data, pd.Series):
            mapped_name = name_mapping.get(tickers[0], tickers[0]) if name_mapping else tickers[0]
            data = data.to_frame(name=mapped_name if len(tickers) == 1 else 'Price')
        
        if len(tickers) > 1 and isinstance(data, pd.DataFrame):
            if name_mapping:
                data.rename(columns=name_mapping, inplace=True)
            mapped_tickers = [name_mapping.get(t, t) for t in tickers] if name_mapping else tickers
            # Intersect with available columns
            mapped_tickers = [t for t in mapped_tickers if t in data.columns]
            data = data[mapped_tickers] 
        elif name_mapping and isinstance(data, pd.DataFrame): 
            data.rename(columns=name_mapping, inplace=True)
            
        return data.dropna()

    def run_training_phase(self, views_dict, confidence_levels):
        """Train standard optimization bounds on pre-crisis pure data natively."""
        logger.info(f"--- TRAINING PHASE: {self.train_start} to {self.train_end} ---")
        opt = BlackLittermanOptimizer(self.original_tickers, self.train_start, self.train_end, name_mapping=self.name_mapping)
        
        cmp = opt.compare_models(views_dict, confidence_levels)
        
        self.weights['markowitz'] = cmp['markowitz']['weights']
        self.weights['black_litterman'] = cmp['black_litterman']['weights']
        self.weights['equal_weight'] = cmp['equal_weight']['weights']
        
        # Track pre-crisis volatility directly from opt cov_matrix to calculate Volatility Spike later
        self.train_vol = {
            'markowitz': np.sqrt(self.weights['markowitz'] @ opt.cov_matrix @ self.weights['markowitz']),
            'black_litterman': np.sqrt(self.weights['black_litterman'] @ opt.cov_matrix @ self.weights['black_litterman']),
            'benchmark': np.nan  # Will compute SP500 later
        }

    def run_stress_test(self):
        """Evaluate pre-crisis allocations natively across the unseen 2008 collapse window."""
        logger.info(f"\n--- STRESS TESTING PHASE: {self.test_start} to {self.test_end} ---")
        
        # Fetch exact asset array outputs from crisis window
        logger.info("Fetching test window Asset prices...")
        self.test_prices = self._fetch_prices(self.original_tickers, self.test_start, self.test_end, name_mapping=self.name_mapping)
        self.test_returns = np.log(self.test_prices / self.test_prices.shift(1)).dropna()
        
        # Fetch S&P 500 equivalent window actively
        logger.info(f"Fetching test window Benchmark ({self.benchmark}) prices...")
        bench_prices = self._fetch_prices([self.benchmark], self.test_start, self.test_end)
        self.benchmark_returns = np.log(bench_prices / bench_prices.shift(1)).dropna().iloc[:, 0]
        
        # Align timelines natively to identical market days
        aligned = pd.concat([self.test_returns, self.benchmark_returns], axis=1).dropna()
        self.test_returns = aligned[self.tickers]
        self.benchmark_returns = aligned.iloc[:, -1]
        
        # Pre-crisis Benchmark Volatility evaluation
        logger.info("Evaluating pre-crisis Benchmark volatility...")
        bench_train = self._fetch_prices([self.benchmark], self.train_start, self.train_end)
        bench_train_ret = np.log(bench_train / bench_train.shift(1)).dropna()
        self.train_vol['benchmark'] = bench_train_ret.iloc[:, 0].std() * np.sqrt(252)
        
        logger.info("Calculating exact crisis performance trails...")
        self.daily_performance = {}
        for strategy, weights in self.weights.items():
            self.daily_performance[strategy] = self.test_returns.dot(weights)
            
        self.daily_performance['benchmark'] = self.benchmark_returns
        
        # Derive core mathematics actively
        for name, daily_ret in self.daily_performance.items():
            # 1. Total Crisis Yield
            cum_rets = (1 + daily_ret).cumprod()
            total_crisis_return = cum_rets.iloc[-1] - 1
            
            # 2. Maximum Drawdown Trace
            rolling_max = cum_rets.cummax()
            drawdowns = (cum_rets - rolling_max) / rolling_max
            max_drawdown = drawdowns.min()
            
            # 3. Volatility Spike Mapping
            crisis_vol = daily_ret.std() * np.sqrt(252)
            pre_vol = self.train_vol.get(name, self.train_vol['black_litterman'] if name == 'equal_weight' else np.nan)
            
            if name == 'equal_weight':
               pre_vol = np.sqrt(self.weights['equal_weight'] @ self.test_returns.cov() @ self.weights['equal_weight']) * np.sqrt(252) # Re-estimating from tests since we don't have train equal weight cov matrix cached 
               
            vol_spike = (crisis_vol / pre_vol) if not np.isnan(pre_vol) else np.nan
            
            # 4. Crisis Recovery Logic Trace
            # To accurately measure the exact time-to-recovery (trough-to-peak duration), Evaluate against extended data horizons
            max_underwater_days = 0
            
            if hasattr(self, 'global_prices') and self.global_prices is not None and not self.global_prices.empty:
                ext_end = self.global_prices.index[-1].strftime('%Y-%m-%d')
                
                if name == 'benchmark':
                    ext_prices = self._fetch_prices([self.benchmark], self.test_start, ext_end)
                    ext_ret = np.log(ext_prices / ext_prices.shift(1)).dropna().iloc[:, 0]
                else:
                    ext_prices = self._fetch_prices(self.original_tickers, self.test_start, ext_end, name_mapping=self.name_mapping)
                    ext_ret_assets = np.log(ext_prices / ext_prices.shift(1)).dropna()
                    weights_arr = self.weights[name]
                    ext_ret = ext_ret_assets[self.tickers].dot(weights_arr)
                    
                ext_cum = (1 + ext_ret).cumprod()
                
                # We identify the major trough uniquely within the tested crisis window
                crisis_ext = ext_cum.loc[:self.test_end]
                if not crisis_ext.empty:
                    rmax = crisis_ext.cummax()
                    dds = (crisis_ext - rmax) / rmax
                    dd_trough_idx = dds.idxmin()
                    
                    if pd.notna(dd_trough_idx):
                        # CORRECT FINANCIAL DEFINITION:
                        # Pre-crisis peak = portfolio value at the START of the crisis period (t0).
                        # This is the reference level that defines recovery, per standard drawdown
                        # recovery methodology in quantitative asset management research.
                        # Searching for a local max within the falling crisis window is incorrect,
                        # as it finds a spurious intermediate point in an already-declining series.
                        peak_idx = ext_cum.index[0]
                        peak_val = ext_cum.iloc[0]
                        
                        # Recovery: first date AFTER the trough where portfolio >= crisis-start value.
                        post_trough = ext_cum.loc[dd_trough_idx:]
                        recovery_points = post_trough[post_trough >= peak_val]
                        if not recovery_points.empty:
                            recovery_idx = recovery_points.index[0]
                            # Duration = trading days from trough to recovery (not peak to recovery)
                            trough_pos = ext_cum.index.get_loc(dd_trough_idx)
                            recovery_pos = ext_cum.index.get_loc(recovery_idx)
                            max_underwater_days = recovery_pos - trough_pos
                        else:
                            # Portfolio did not recover within the dataset horizon
                            trough_pos = ext_cum.index.get_loc(dd_trough_idx)
                            max_underwater_days = len(ext_cum) - 1 - trough_pos
            else:
                # Fallback to local truncation if extended arrays map invalid
                if cum_rets.empty:
                    max_underwater_days = 0
                else:
                    dd_trough_idx = drawdowns.idxmin()
                    if pd.notna(dd_trough_idx):
                        # CORRECT FINANCIAL DEFINITION (fallback path):
                        # Pre-crisis peak = portfolio value at the START of the crisis period.
                        peak_idx = cum_rets.index[0]
                        peak_val = cum_rets.iloc[0]
                        post_trough = cum_rets.loc[dd_trough_idx:]
                        recovery_points = post_trough[post_trough >= peak_val]
                        if not recovery_points.empty:
                            recovery_idx = recovery_points.index[0]
                            # Duration = trading days from trough to recovery
                            trough_pos = cum_rets.index.get_loc(dd_trough_idx)
                            recovery_pos = cum_rets.index.get_loc(recovery_idx)
                            max_underwater_days = recovery_pos - trough_pos
                        else:
                            trough_pos = cum_rets.index.get_loc(dd_trough_idx)
                            max_underwater_days = len(cum_rets) - 1 - trough_pos
                    else:
                        max_underwater_days = 0
            
            self.results[name] = {
                'Crisis Return': total_crisis_return,
                'Max Drawdown': max_drawdown,
                'Crisis Volatility': crisis_vol,
                'Pre-Crisis Volatility': pre_vol,
                'Volatility Spike (x)': vol_spike,
                'Max Underwater Days': max_underwater_days,
                'cumulative_series': cum_rets,
                'drawdown_series': drawdowns
            }
            
    def print_results(self):
        """Log the output matrix natively to terminal."""
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

def main():
    # Execute a fully automated testing isolation using a diversified tech + defensive setup
    tickers = ['AAPL', 'MSFT', 'JNJ', 'PEP', 'PG']
    
    views = {
        'AAPL': 0.15,
        'MSFT': 0.12,
        'JNJ': 0.08,
        'PEP': 0.09,
        'PG': 0.07
    }
    
    confidence = {
        'AAPL': 0.50,
        'MSFT': 0.50,
        'JNJ': 0.70,
        'PEP': 0.70,
        'PG': 0.70
    }
    
    tester = HistoricalStressTester(tickers)
    tester.run_training_phase(views, confidence)
    tester.run_stress_test()
    tester.print_results()
    tester.plot_stress_test()

if __name__ == '__main__':
    main()
