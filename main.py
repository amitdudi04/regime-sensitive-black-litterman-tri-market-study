"""
Final Production Research Workflow
==================================

Master execution script orchestrating:
1. Baseline Markowitz vs Black-Litterman comparisons
2. Comprehensive rolling out-of-sample backtesting
3. Transaction Cost accounting
4. Sensitivity logic (Tau and Lambda bounds)
5. Historical crash isolation (2008 Financial Crisis stress test)

Outputs generated systematically to unified CSV grids and 
a consolidated visual dashboard payload.
"""

import os
import pandas as pd
import numpy as np

# Set reproducibility seed
np.random.seed(42)

# Import internal modules
from portfolio_optimization import BlackLittermanOptimizer
from backtesting import run_comprehensive_backtest
from robustness import (
    run_tau_sensitivity, 
    run_lambda_sensitivity,
    HistoricalStressTester
)
import visualizations as viz


def _export_performance_summary(final_results, save_dir="results"):
    """
    Format and export final performance metrics across Baseline and Rolling Backtests.
    Includes Expected Return, Volatility, Sharpe, Drawdown, VaR, CVaR etc.
    """
    os.makedirs(save_dir, exist_ok=True)
    
    rows = []
    
    # Extract baseline static optimization metrics
    baseline = final_results.get("baseline_metrics", {})
    for model_name, model_data in baseline.items():
        metrics = model_data.get('metrics', {})
        rows.append({
            'Category': 'Static In-Sample Optimization',
            'Model': model_name.replace('_', ' ').title(),
            'Expected Return': metrics.get('Expected Return'),
            'Volatility': metrics.get('Volatility'),
            'Sharpe Ratio': metrics.get('Sharpe Ratio'),
            'Max Drawdown': metrics.get('Max Drawdown'),
            'VaR (95%)': metrics.get('VaR (95%)'),
            'CVaR (95%)': metrics.get('CVaR (95%)'),
            'Performance Type': 'Gross'
        })
        
    # Extract out-of-sample rolling benchmark returns
    backtest = final_results.get("benchmark_metrics", {})
    models = ['markowitz', 'black_litterman', 'equal_weight']
    
    for m in models:
        try:
            # Extract Gross metrics
            gross_rets = backtest[m]['gross']
            gross_mean = gross_rets.mean() * 252
            gross_vol = gross_rets.std() * np.sqrt(252)
            gross_sharpe = gross_mean / gross_vol
            cum_rets = (1 + gross_rets).cumprod()
            gross_dd = ((cum_rets - cum_rets.cummax()) / cum_rets.cummax()).min()
            var_95 = np.percentile(gross_rets, 5)
            cvar_95 = gross_rets[gross_rets <= var_95].mean()
            
            rows.append({
                'Category': 'Rolling Out-of-Sample Backtest',
                'Model': m.replace('_', ' ').title(),
                'Expected Return': gross_mean,
                'Volatility': gross_vol,
                'Sharpe Ratio': gross_sharpe,
                'Max Drawdown': gross_dd,
                'VaR (95%)': var_95,
                'CVaR (95%)': cvar_95,
                'Performance Type': 'Gross'
            })
            
            # Extract Net metrics
            net_rets = backtest[m]['net']
            net_mean = net_rets.mean() * 252
            net_vol = net_rets.std() * np.sqrt(252)
            net_sharpe = net_mean / net_vol
            cum_rets_n = (1 + net_rets).cumprod()
            net_dd = ((cum_rets_n - cum_rets_n.cummax()) / cum_rets_n.cummax()).min()
            n_var_95 = np.percentile(net_rets, 5)
            n_cvar_95 = net_rets[net_rets <= n_var_95].mean()
            
            rows.append({
                'Category': 'Rolling Out-of-Sample Backtest',
                'Model': m.replace('_', ' ').title(),
                'Expected Return': net_mean,
                'Volatility': net_vol,
                'Sharpe Ratio': net_sharpe,
                'Max Drawdown': net_dd,
                'VaR (95%)': n_var_95,
                'CVaR (95%)': n_cvar_95,
                'Performance Type': 'Net (After Costs)'
            })
        except Exception as e:
            pass
            
            
    df = pd.DataFrame(rows)
    export_path = os.path.join(save_dir, "final_performance_summary.csv")
    df.to_csv(export_path, index=False)
    print(f"Generated {export_path}")

def _export_robustness_summary(final_results, save_dir="results"):
    """
    Format and export extreme sensitivity boundaries and crash isolation states.
    """
    os.makedirs(save_dir, exist_ok=True)
    
    rows = []
    
    # Compile Tau boundaries
    tau_df = final_results.get("tau_sensitivity")
    if tau_df is not None and not tau_df.empty:
        tau_min = tau_df.iloc[0]
        tau_max = tau_df.iloc[-1]
        
        rows.append({
            'Category': 'Tau Sensitivity',
            'Metric': 'Expected Return (Max Certainty vs Min Certainty)',
            'Base Value': tau_min['Expected Return'],
            'Stressed Value': tau_max['Expected Return']
        })
        rows.append({
            'Category': 'Tau Sensitivity',
            'Metric': 'Sharpe Ratio Decay',
            'Base Value': tau_min['Sharpe Ratio'],
            'Stressed Value': tau_max['Sharpe Ratio']
        })
        
    # Compile Lambda Risk Aversion boundaries
    lmb_df = final_results.get("lambda_sensitivity")
    if lmb_df is not None and not lmb_df.empty:
        lmb_min = lmb_df.iloc[0]
        lmb_max = lmb_df.iloc[-1]
        rows.append({
            'Category': 'Risk Aversion (Lambda)',
            'Metric': 'Volatility Collapse',
            'Base Value': lmb_min['Volatility'],
            'Stressed Value': lmb_max['Volatility']
        })
    
    # Compiling 2008 Crash Metrics
    stress = final_results.get("stress_test", {})
    if stress:
        try:
            bl_stress = stress['black_litterman']
            bench_stress = stress['benchmark']
            
            rows.append({
                'Category': '2008 Crash Simulation',
                'Metric': 'Crisis Total Return',
                'Base Value': bl_stress['Crisis Return'],
                'Stressed Value': bench_stress['Crisis Return']
            })
            rows.append({
                'Category': '2008 Crash Simulation',
                'Metric': 'Maximum Geometric Drawdown',
                'Base Value': bl_stress['Max Drawdown'],
                'Stressed Value': bench_stress['Max Drawdown']
            })
            rows.append({
                'Category': '2008 Crash Simulation',
                'Metric': 'Volatility Spike Multiple',
                'Base Value': bl_stress['Volatility Spike (x)'],
                'Stressed Value': bench_stress['Volatility Spike (x)']
            })
            rows.append({
                'Category': '2008 Crash Simulation',
                'Metric': 'Daily 95% CVaR',
                'Base Value': bl_stress.get('CVaR (95%)'),
                'Stressed Value': bench_stress.get('CVaR (95%)')
            })
        except Exception as e:
            pass

    df = pd.DataFrame(rows)
    export_path = os.path.join(save_dir, "robustness_summary.csv")
    df.to_csv(export_path, index=False)
    print(f"Generated {export_path}")

def main():
    print("="*80)
    print("   MASTER RESEARCH WORKFLOW: PORTFOLIO OPTIMIZATION & ROBUSTNESS   ")
    print("="*80)
    
    final_results = {}
    
    # Configuration setup
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
    start_dt = '2019-01-01'
    end_dt = '2025-01-01'
    views = {'AAPL': 0.12, 'MSFT': 0.10, 'NVDA': 0.15, 'GOOGL': 0.11, 'AMZN': 0.14}
    confidence = {'AAPL': 0.60, 'MSFT': 0.50, 'NVDA': 0.65, 'GOOGL': 0.55, 'AMZN': 0.60}
    
    try:
        # -------------------------------------------------------------
        # Phase 1: Baseline Initialization
        # -------------------------------------------------------------
        print("\n[1/6] Running Baseline Markowitz vs Black-Litterman Comparison...")
        opt = BlackLittermanOptimizer(tickers, start_dt, end_dt)
        baseline_metrics = opt.compare_models(views, confidence)
        final_results["baseline_metrics"] = baseline_metrics
        
        # -------------------------------------------------------------
        # Phase 2: Rolling Backtest + Benchmarks + Constraints
        # -------------------------------------------------------------
        print("\n[2/6] Executing Transaction Cost-Adjusted Rolling Backtest...")
        backtest_out, ir_metrics, sharpe_ratios = run_comprehensive_backtest(opt, views)
        final_results["benchmark_metrics"] = backtest_out
        final_results["transaction_cost_metrics"] = ir_metrics
        
        # -------------------------------------------------------------
        # Phase 3: Robustness Analysis (Tau & Lambda Sensitivity)
        # -------------------------------------------------------------
        print("\n[3/6] Running Tau and Lambda Sensitivity Analyses...")
        tau_df = run_tau_sensitivity(opt, views, confidence)
        lmb_df = run_lambda_sensitivity(opt, views, confidence)
        
        final_results["tau_sensitivity"] = tau_df
        final_results["lambda_sensitivity"] = lmb_df
        
        # Plot sub-components implicitly via visualizations
        viz.plot_tau_sensitivity(tau_df)
        viz.plot_lambda_sensitivity(lmb_df)
        
        # -------------------------------------------------------------
        # Phase 4: Extreme 2008 Stress Testing Simulation
        # -------------------------------------------------------------
        print("\n[4/6] Booting 2008 Financial Crisis Simulation Metrics...")
        stresser = HistoricalStressTester(tickers)
        stresser.run_training_phase(views, confidence)
        stresser.run_stress_test()
        
        final_results["stress_test"] = stresser.results
        
        # -------------------------------------------------------------
        # Phase 5: Generating Master Dashboard Reporting
        # -------------------------------------------------------------
        print("\n[5/6] Building Master Visualization Layout Panels...")
        viz.plot_final_research_dashboard(backtest_out, stresser.results)
        viz.create_visualizations(opt, baseline_metrics)  # Base optimization charts
        
        # -------------------------------------------------------------
        # Phase 6: Consolidating Final Output Matrix to CSV
        # -------------------------------------------------------------
        print("\n[6/6] Generating Unified Structuring & Reporting...")
        _export_performance_summary(final_results)
        _export_robustness_summary(final_results)
        
        print("\n" + "="*80)
        print("[OK] FULL ANALYTICAL RESEARCH WORKFLOW EXTRACTED SUCCESSFULLY.")
        print("  Outputs written identically to local /results array.")
        print("="*80)

    except Exception as e:
        print("\nCRITICAL FAILURE DURING WORKFLOW EXECTION:")
        print(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
