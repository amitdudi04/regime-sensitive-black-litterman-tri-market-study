import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

# Import core analytical modules
from portfolio_optimization import BlackLittermanOptimizer
from backtesting import run_comprehensive_backtest
from stress_testing import HistoricalStressTester


def build_robustness_summary():
    """
    Master orchestrator script to sequentially boot and map metrics from:
    1. The core BL Optimizer (Tau Sensitivity)
    2. The core BL Optimizer (Lambda Sensitivity)
    3. The Rolling Backtester (2018-2024 Out-Of-Sample Net Returns)
    4. The Historical Stress Tester (2008 Deep Crash Geometric Drawdowns)
    """
    print("="*80)
    print("INITIALIZING MASTER ROBUSTNESS AGGREGATION PIPELINE")
    print("="*80)
    
    # ----------------------------------------------------
    # Configuration Space
    # ----------------------------------------------------
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
    base_start = '2019-01-01'  # Keep it slightly tighter for rapid backtester matrix evaluation
    base_end = '2024-01-01'
    save_dir = "results"
    
    views = {
        'AAPL': 0.12,
        'MSFT': 0.10,
        'GOOGL': 0.11,
        'AMZN': 0.14,
        'NVDA': 0.15
    }
    
    confidence = {
        'AAPL': 0.60,
        'MSFT': 0.50,
        'GOOGL': 0.40,
        'AMZN': 0.45,
        'NVDA': 0.65
    }
    
    # Primary Data Output Struct
    summary_data = []
    
    # Ensure export dir exists
    os.makedirs(save_dir, exist_ok=True)
    
    # ----------------------------------------------------
    # Module 1: Optimizer Analytics (Tau + Lambda)
    # ----------------------------------------------------
    print(f"\n[1/4] Booting Core Optimizer ({base_start} to {base_end})...")
    opt = BlackLittermanOptimizer(tickers, base_start, base_end)
    
    print("      >> Executing parameter extraction sweeps...")
    # Silence the deep prints from the components temporarily for the main pipeline
    import sys
    import logging
    
    # Run Tau Sensitivity (0.01 vs 0.20)
    tau_vals = [0.01, 0.2] 
    df_tau = opt.run_tau_sensitivity(views, confidence, tau_values=tau_vals, save_dir=save_dir)
    
    # Tau Variance Metrics: How does the model shift identically from Minimum Uncertainty vs Maximum?
    expected_return_shift = df_tau.loc[0.2, 'Expected Return'] - df_tau.loc[0.01, 'Expected Return']
    sharpe_shift = df_tau.loc[0.2, 'Sharpe Ratio'] - df_tau.loc[0.01, 'Sharpe Ratio']
    
    summary_data.append({
        'Category': 'Tau Sensitivity (\u03C4)',
        'Metric': 'Expected Return Shift (0.01 -> 0.20)',
        'Black-Litterman': f"{(expected_return_shift * 100):.2f}%",
        'Markowitz': 'N/A (Static)',
        'S&P 500': 'N/A'
    })
    summary_data.append({
        'Category': 'Tau Sensitivity (\u03C4)',
        'Metric': 'Sharpe Ratio Shift (0.01 -> 0.20)',
        'Black-Litterman': f"{sharpe_shift:.3f}",
        'Markowitz': 'N/A (Static)',
        'S&P 500': 'N/A'
    })
    
    # Run Lambda Sensitivity (Risk Aversion 1.5 vs 4.0)
    lam_vals = [1.5, 4.0]
    df_lam = opt.run_lambda_sensitivity(views, confidence, lambda_values=lam_vals, save_dir=save_dir)
    
    vol_shift = df_lam.loc[4.0, 'Volatility'] - df_lam.loc[1.5, 'Volatility']
    expected_return_shift_lam = df_lam.loc[4.0, 'Expected Return'] - df_lam.loc[1.5, 'Expected Return']
    
    summary_data.append({
        'Category': 'Lambda Sensitivity (\u03BB)',
        'Metric': 'Volatility Shift (1.5 -> 4.0)',
        'Black-Litterman': f"{(vol_shift * 100):.2f}%",
        'Markowitz': 'N/A (Static)',
        'S&P 500': 'N/A'
    })
    summary_data.append({
        'Category': 'Lambda Sensitivity (\u03BB)',
        'Metric': 'Expected Return Drop (1.5 -> 4.0)',
        'Black-Litterman': f"{(expected_return_shift_lam * 100):.2f}%",
        'Markowitz': 'N/A (Static)',
        'S&P 500': 'N/A'
    })
    
    # ----------------------------------------------------
    # Module 2: The Rolling Backtester
    # ----------------------------------------------------
    print(f"\n[2/4] Booting Portfolio Backtester (252-day Rolling Model)...")
    
    print("      >> Executing iterative Out-of-Sample trajectories...")
    results, _, _ = run_comprehensive_backtest(opt, views)
    
    # Extract Annualized Out-Of-Sample Data via Net Series
    def extract_annualized_net(model_name):
         daily_net = results[model_name]['net']
         ret = daily_net.mean() * 252
         vol = daily_net.std() * np.sqrt(252)
         cum_rets = (1 + daily_net).cumprod()
         drawdowns = (cum_rets - cum_rets.cummax()) / cum_rets.cummax()
         max_dd = drawdowns.min()
         return ret, vol, max_dd
        
    bl_ret, bl_vol, bl_dd = extract_annualized_net('black_litterman')
    mw_ret, mw_vol, mw_dd = extract_annualized_net('markowitz')
    
    # Needs explicit benchmark array aligned
    sp5_returns = results['sp500']
    
    sp5_ret = sp5_returns.mean() * 252
    sp5_cum = (1 + sp5_returns).cumprod()
    sp5_dd = ((sp5_cum - sp5_cum.cummax()) / sp5_cum.cummax()).min()
    
    summary_data.append({
        'Category': 'Rolling Backtest (2018-2024)',
        'Metric': 'Net Annualized Return',
        'Black-Litterman': f"{(bl_ret * 100):.2f}%",
        'Markowitz': f"{(mw_ret * 100):.2f}%",
        'S&P 500': f"{(sp5_ret * 100):.2f}%"
    })
    summary_data.append({
        'Category': 'Rolling Backtest (2018-2024)',
        'Metric': 'Maximum Drawdown',
        'Black-Litterman': f"{(bl_dd * 100):.2f}%",
        'Markowitz': f"{(mw_dd * 100):.2f}%",
        'S&P 500': f"{(sp5_dd * 100):.2f}%"
    })
    summary_data.append({
        'Category': 'Rolling Backtest (2018-2024)',
        'Metric': 'Annual Cost Drag (Fees)',
        'Black-Litterman': f"{(results['cost_impact']['black_litterman'] * 10000):.1f} bps",
        'Markowitz': f"{(results['cost_impact']['markowitz'] * 10000):.1f} bps",
        'S&P 500': '0.0 bps'
    })
    
    # ----------------------------------------------------
    # Module 3: Historical Stress Testing (2008 Crash)
    # ----------------------------------------------------
    print(f"\n[3/4] Booting 2008 Deep Crash Simulator...")
    # Force use safer assets alongside broad targets simulating standard retail logic
    stress_tickers = ['AAPL', 'MSFT', 'JNJ', 'PEP', 'PG']
    stress_views = {'AAPL': 0.15, 'MSFT': 0.12, 'JNJ': 0.08, 'PEP': 0.09, 'PG': 0.07}
    stress_conf = {'AAPL': 0.50, 'MSFT': 0.50, 'JNJ': 0.70, 'PEP': 0.70, 'PG': 0.70}
    
    tester = HistoricalStressTester(stress_tickers)
    tester.run_training_phase(stress_views, stress_conf)
    tester.run_stress_test()
    tester.plot_stress_test(save_dir)
    
    bl_08_dd = tester.results['black_litterman']['Max Drawdown']
    mw_08_dd = tester.results['markowitz']['Max Drawdown']
    sp_08_dd = tester.results['benchmark']['Max Drawdown']
    
    bl_08_spd = tester.results['black_litterman']['Max Underwater Days']
    mw_08_spd = tester.results['markowitz']['Max Underwater Days']
    sp_08_spd = tester.results['benchmark']['Max Underwater Days']
    
    summary_data.append({
        'Category': '2008 Shock Simulator',
        'Metric': 'Crisis Max Drawdown (%)',
        'Black-Litterman': f"{(bl_08_dd * 100):.2f}%",
        'Markowitz': f"{(mw_08_dd * 100):.2f}%",
        'S&P 500': f"{(sp_08_dd * 100):.2f}%"
    })
    summary_data.append({
        'Category': '2008 Shock Simulator',
        'Metric': 'Longest Submerged Period',
        'Black-Litterman': f"{bl_08_spd} days",
        'Markowitz': f"{mw_08_spd} days",
        'S&P 500': f"{sp_08_spd} days"
    })
    
    # ----------------------------------------------------
    # Module 4: Synthesis DataFrame & Export
    # ----------------------------------------------------
    print("\n[4/4] Rendering Final Unified DataFrame and Exporting...")
    master_df = pd.DataFrame(summary_data)
    
    export_path = os.path.join(save_dir, 'robustness_summary.csv')
    master_df.to_csv(export_path, index=False)
    
    print("\n" + "="*80)
    print("FINAL ROBUSTNESS PIPELINE METRICS")
    print("="*80)
    print(master_df.to_string(index=False))
    print("="*80)
    print(f"\n✓ Successfully exported unified robustness metrics to: {export_path}")

if __name__ == "__main__":
    build_robustness_summary()
