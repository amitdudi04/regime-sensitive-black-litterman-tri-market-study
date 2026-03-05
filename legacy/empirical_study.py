import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from portfolio_optimization import BlackLittermanOptimizer
from backtesting import run_comprehensive_backtest
from stress_testing import HistoricalStressTester
from robustness import run_tau_sensitivity, run_lambda_sensitivity

# 1. Add Chinese Equity Universe (Academic Structure)
CHINA_UNIVERSE = {
    "Kweichow Moutai Co., Ltd.": {"ticker": "600519.SS", "sector": "Consumer Staples"},
    "Ping An Insurance (Group) Company of China, Ltd.": {"ticker": "601318.SS", "sector": "Financial Services"},
    "China Merchants Bank Co., Ltd.": {"ticker": "600036.SS", "sector": "Banking"},
    "Industrial and Commercial Bank of China Limited": {"ticker": "601398.SS", "sector": "Banking"},
    "Contemporary Amperex Technology Co., Limited": {"ticker": "300750.SZ", "sector": "Technology / EV"},
    "Wuliangye Yibin Co., Ltd.": {"ticker": "000858.SZ", "sector": "Consumer Staples"},
    "Jiangsu Hengrui Pharmaceuticals Co., Ltd.": {"ticker": "600276.SS", "sector": "Healthcare"},
    "Wanhua Chemical Group Co., Ltd.": {"ticker": "600309.SS", "sector": "Industrial Materials"}
}

china_tickers = [v["ticker"] for v in CHINA_UNIVERSE.values()]

# Asset Name Mapping for clean plots
TICKER_NAME_MAP = {v["ticker"]: k.split(" ")[0] for k, v in CHINA_UNIVERSE.items()}
TICKER_NAME_MAP.update({'AAPL': 'Apple', 'MSFT': 'Microsoft', 'GOOGL': 'Alphabet', 'AMZN': 'Amazon', 'NVDA': 'NVIDIA'})

TICKER_TO_SECTOR = {v["ticker"]: v["sector"] for v in CHINA_UNIVERSE.values()}
TICKER_TO_SECTOR.update({'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 'AMZN': 'Consumer Cyclical', 'NVDA': 'Technology'})

# 2. Add Dual Market Configuration Layer
MARKET_CONFIG = {
    "US": {
        "tickers": ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'],
        "benchmark": '^GSPC',
        "start": '2010-01-01',
        "end": '2025-01-01',
        "stress_train_start": '2005-01-01',
        "stress_train_end": '2007-12-31',
        "stress_test_start": '2008-01-01',
        "stress_test_end": '2009-12-31',
        "stress_tickers": ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'],
        "views": {'AAPL': 0.12, 'MSFT': 0.10, 'GOOGL': 0.11, 'AMZN': 0.14, 'NVDA': 0.15},
        "confidence": {'AAPL': 0.60, 'MSFT': 0.50, 'GOOGL': 0.40, 'AMZN': 0.45, 'NVDA': 0.65}
    },
    "CHINA": {
        "tickers": china_tickers,
        "benchmark": '000001.SS',
        "start": '2010-01-01',
        "end": '2025-01-01',
        "stress_train_start": '2012-01-01',
        "stress_train_end": '2014-12-31',
        "stress_test_start": '2015-01-01',
        "stress_test_end": '2016-06-30',
        "stress_tickers": [t for t in china_tickers if t != '300750.SZ'],
        "views": {t: 0.12 for t in china_tickers}, 
        "confidence": {t: 0.50 for t in china_tickers}
    }
}

# 4. Create Unified Market Pipeline
def run_market_pipeline(market_name: str, config: dict) -> dict:
    print(f"\n========================================================")
    print(f"[{market_name}] COMMENCING EMPIRICAL PIPELINE EVALUATION")
    print(f"========================================================")
    
    save_dir = "results"
    os.makedirs(save_dir, exist_ok=True)
    
    # Initialize Optimizer with CSI/SP500 Market Cap Equilibrium
    print(f"\n[1/5] Booting Market Equilibrium Optimizer...")
    opt = BlackLittermanOptimizer(
        config["tickers"], 
        config["start"], 
        config["end"], 
        use_market_cap_weights=True
    )
    
    print("\n[2/5] Synthesizing Baseline Cross-Model Allocation (Markowitz vs BL)...")
    baseline_comparison = opt.compare_models(config["views"], config["confidence"])
    
    print("\n[3/5] Launching Frictional Rolling Backtest...")
    bt_results, _, _ = run_comprehensive_backtest(opt, config["views"])
    
    # Net Backtest Metrics Extractor
    def extract_metrics(res_dict, model_key):
        daily_net = res_dict[model_key]['net']
        ann_ret = daily_net.mean() * 252
        ann_vol = daily_net.std() * np.sqrt(252)
        sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
        
        cum_rets = (1 + daily_net).cumprod()
        drawdowns = (cum_rets - cum_rets.cummax()) / cum_rets.cummax()
        max_dd = drawdowns.min()
        
        # CVaR at 95%
        var_95 = np.percentile(daily_net, 5)
        cvar_95 = daily_net[daily_net <= var_95].mean()
        
        turnover = res_dict.get('turnover', {}).get(model_key, [])
        avg_turnover = np.mean(turnover) if len(turnover) > 0 else 0.0
        
        return ann_ret, ann_vol, sharpe, max_dd, cvar_95, avg_turnover

    bl_ret, bl_vol, bl_sharpe, bl_dd, bl_cvar, bl_turn = extract_metrics(bt_results, 'black_litterman')
    mw_ret, mw_vol, mw_sharpe, mw_dd, mw_cvar, mw_turn = extract_metrics(bt_results, 'markowitz')
    
    bench_key = 'sp500' if config["benchmark"] == '^GSPC' else 'csi300'
    bench_returns = bt_results[bench_key]
    bench_ann_ret = bench_returns.mean() * 252
    bench_ann_vol = bench_returns.std() * np.sqrt(252)
    bench_cum = (1 + bench_returns).cumprod()
    bench_dd = ((bench_cum - bench_cum.cummax()) / bench_cum.cummax()).min()
    bench_sharpe = bench_ann_ret / bench_ann_vol if bench_ann_vol > 0 else 0
    
    # Information Ratio
    bl_active = bt_results['black_litterman']['net'] - bench_returns
    mw_active = bt_results['markowitz']['net'] - bench_returns
    
    bl_ir = (bl_active.mean() * 252) / (bl_active.std() * np.sqrt(252)) if bl_active.std() > 0 else 0
    mw_ir = (mw_active.mean() * 252) / (mw_active.std() * np.sqrt(252)) if mw_active.std() > 0 else 0
    
    print("\n[4/5] Running Robustness Sensitivity Checks...")
    df_tau = run_tau_sensitivity(opt, config["views"], config["confidence"], tau_values=[0.01, 0.2])
    df_lambda = run_lambda_sensitivity(opt, config["views"], config["confidence"], lambda_values=[1.5, 4.0])
    
    print(f"\n[5/5] Executing Deep Stress Crisis Regime ({config['stress_test_start']} to {config['stress_test_end']})...")
    tester = HistoricalStressTester(
        config["stress_tickers"],
        train_start=config["stress_train_start"],
        train_end=config["stress_train_end"],
        test_start=config["stress_test_start"],
        test_end=config["stress_test_end"],
        benchmark=config["benchmark"]
    )
    s_views = {t: config["views"][t] for t in config["stress_tickers"]}
    s_conf = {t: config["confidence"][t] for t in config["stress_tickers"]}
    tester.run_training_phase(s_views, s_conf)
    tester.run_stress_test()
    
    # Export Market-Specific CSVs for China
    if market_name == "CHINA":
        pd.DataFrame([{
            'Metric': 'Net Annual Return',
            'BL': bl_ret, 'MW': mw_ret, 'ShanghaiComp': bench_ann_ret
        }, {
            'Metric': 'Sharpe Ratio',
            'BL': bl_sharpe, 'MW': mw_sharpe, 'ShanghaiComp': bench_sharpe
        }, {
            'Metric': 'Information Ratio',
            'BL': bl_ir, 'MW': mw_ir, 'ShanghaiComp': 0
        }, {
            'Metric': 'Max Drawdown',
            'BL': bl_dd, 'MW': mw_dd, 'ShanghaiComp': bench_dd
        }]).to_csv(f"{save_dir}/china_performance_summary.csv", index=False)
        
        pd.DataFrame([
            {'Asset': TICKER_NAME_MAP[t] if t != '300750.SZ' else 'CATL', 'Ticker': t, 'Sector': TICKER_TO_SECTOR[t]} 
            for t in config["tickers"]
        ]).to_csv(f"{save_dir}/china_asset_universe.csv", index=False)
        
        df_tau.to_csv(f"{save_dir}/china_robustness_summary.csv")
    
    return {
        "baseline": baseline_comparison,
        "backtest_series": {
            "bl_cum": (1 + bt_results['black_litterman']['net']).cumprod(),
            "mw_cum": (1 + bt_results['markowitz']['net']).cumprod(),
            "bench_cum": bench_cum
        },
        "performance": {
            "bl_ret": bl_ret, "bl_vol": bl_vol, "bl_sharpe": bl_sharpe, "bl_dd": bl_dd, "bl_cvar": bl_cvar, "bl_turn": bl_turn, "bl_ir": bl_ir,
            "mw_ret": mw_ret, "mw_vol": mw_vol, "mw_sharpe": mw_sharpe, "mw_dd": mw_dd, "mw_cvar": mw_cvar, "mw_turn": mw_turn, "mw_ir": mw_ir,
            "bench_ret": bench_ann_ret, "bench_vol": bench_ann_vol, "bench_sharpe": bench_sharpe, "bench_dd": bench_dd
        },
        "tau": df_tau,
        "lambda": df_lambda,
        "stress": tester.results
    }

# 6. Add Cross-Market Comparative Summary
def generate_cross_market_summary(all_results: dict):
    records = []
    
    for market, data in all_results.items():
        perf = data["performance"]
        
        records.append({
            "Market": market,
            "Model": "Black-Litterman",
            "Annualized Net Return": f"{perf['bl_ret']*100:.2f}%",
            "Annualized Volatility": f"{perf['bl_vol']*100:.2f}%",
            "Sharpe Ratio": f"{perf['bl_sharpe']:.3f}",
            "Information Ratio": f"{perf['bl_ir']:.3f}",
            "Max Drawdown": f"{perf['bl_dd']*100:.2f}%",
            "Average Turnover": f"{perf['bl_turn']*100:.2f}%"
        })
        
        records.append({
            "Market": market,
            "Model": "Markowitz",
            "Annualized Net Return": f"{perf['mw_ret']*100:.2f}%",
            "Annualized Volatility": f"{perf['mw_vol']*100:.2f}%",
            "Sharpe Ratio": f"{perf['mw_sharpe']:.3f}",
            "Information Ratio": f"{perf['mw_ir']:.3f}",
            "Max Drawdown": f"{perf['mw_dd']*100:.2f}%",
            "Average Turnover": f"{perf['mw_turn']*100:.2f}%"
        })
        
        records.append({
            "Market": market,
            "Model": "Benchmark",
            "Annualized Net Return": f"{perf['bench_ret']*100:.2f}%",
            "Annualized Volatility": f"{perf['bench_vol']*100:.2f}%",
            "Sharpe Ratio": f"{perf['bench_sharpe']:.3f}",
            "Information Ratio": "N/A",
            "Max Drawdown": f"{perf['bench_dd']*100:.2f}%",
            "Average Turnover": "N/A"
        })
        
    df = pd.DataFrame(records)
    df.to_csv("results/cross_market_comparison.csv", index=False)
    print("\n[EXPORT] results/cross_market_comparison.csv generated")
    return df

# 7. Add Structural Regime Comparison
def generate_structural_analysis(all_results: dict):
    records = []
    
    us_data = all_results["US"]
    cn_data = all_results["CHINA"]
    
    models = ['black_litterman', 'markowitz']
    
    for model in models:
        mkey = "bl_" if model == 'black_litterman' else "mw_"
        
        us_vol_spike = us_data["stress"][model]["Volatility Spike (x)"]
        cn_vol_spike = cn_data["stress"][model]["Volatility Spike (x)"]
        
        records.append({
            "Structural Metric": f"Average Realized Volatility ({model})",
            "US Market": f"{us_data['performance'][mkey+'vol']*100:.2f}%",
            "China Market": f"{cn_data['performance'][mkey+'vol']*100:.2f}%",
            "Delta": f"{(cn_data['performance'][mkey+'vol'] - us_data['performance'][mkey+'vol'])*100:.2f}%"
        })
        
        records.append({
            "Structural Metric": f"Average Turnover Constraints ({model})",
            "US Market": f"{us_data['performance'][mkey+'turn']*100:.2f}%",
            "China Market": f"{cn_data['performance'][mkey+'turn']*100:.2f}%",
            "Delta": f"{(cn_data['performance'][mkey+'turn'] - us_data['performance'][mkey+'turn'])*100:.2f}%"
        })
        
        records.append({
            "Structural Metric": f"Stress-Test Volatility Spike Multiple ({model})",
            "US Market": f"{us_vol_spike:.2f}x (2008)",
            "China Market": f"{cn_vol_spike:.2f}x (2015)",
            "Delta": f"{cn_vol_spike - us_vol_spike:.2f}x"
        })
        
        records.append({
            "Structural Metric": f"Max Crisis Drawdown ({model})",
            "US Market": f"{us_data['stress'][model]['Max Drawdown']*100:.2f}% (2008)",
            "China Market": f"{cn_data['stress'][model]['Max Drawdown']*100:.2f}% (2015)",
            "Delta": f"{(cn_data['stress'][model]['Max Drawdown'] - us_data['stress'][model]['Max Drawdown'])*100:.2f}%"
        })
        
        records.append({
            "Structural Metric": f"Crisis Recovery Duration ({model})",
            "US Market": f"{us_data['stress'][model]['Max Underwater Days']} days",
            "China Market": f"{cn_data['stress'][model]['Max Underwater Days']} days",
            "Delta": f"{cn_data['stress'][model]['Max Underwater Days'] - us_data['stress'][model]['Max Underwater Days']} days"
        })
        
    df = pd.DataFrame(records)
    df.to_csv("results/cross_market_structural_analysis.csv", index=False)
    print("[EXPORT] results/cross_market_structural_analysis.csv generated")
    return df

# 10. Create Tri-Market Dashboard
def plot_tri_market_dashboard(all_results: dict, save_dir="results"):
    print("\n[6/5] Rendering Tri-Market Comparative Dashboard...")
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    
    # Custom aesthetic overrides for deep analytical feel
    plt.style.use('dark_background')
    fig.patch.set_facecolor('#11111B')
    
    for ax in axes.flatten():
        ax.set_facecolor('#181825')
        ax.tick_params(colors='#A6ADC8')
        ax.spines['bottom'].set_color('#313244')
        ax.spines['top'].set_color('#313244')
        ax.spines['left'].set_color('#313244')
        ax.spines['right'].set_color('#313244')
    
    # Top-Left: US Cumulative Returns
    us_cum = all_results["US"]["backtest_series"]
    axes[0,0].plot(us_cum["bl_cum"], label='US BL Engine', color='#F38BA8', linewidth=2)
    axes[0,0].plot(us_cum["mw_cum"], label='US Markowitz', color='#89DCEB', linewidth=1.5, linestyle='--')
    axes[0,0].plot(us_cum["bench_cum"], label='US ^GSPC', color='#F9E2AF', linewidth=1.5, alpha=0.8)
    axes[0,0].set_title("US Market Out-of-Sample Trajectory (2010-2025)", color='#CBA6F7', pad=15)
    axes[0,0].legend(frameon=False, labelcolor='#A6ADC8')
    axes[0,0].grid(True, linestyle='--', alpha=0.2, color='#A6ADC8')
    
    # Top-Right: China Cumulative Returns
    cn_cum = all_results["CHINA"]["backtest_series"]
    axes[0,1].plot(cn_cum["bl_cum"], label='CN BL Engine', color='#F38BA8', linewidth=2)
    axes[0,1].plot(cn_cum["mw_cum"], label='CN Markowitz', color='#89DCEB', linewidth=1.5, linestyle='--')
    axes[0,1].plot(cn_cum["bench_cum"], label='CN 000001.SS', color='#F9E2AF', linewidth=1.5, alpha=0.8)
    axes[0,1].set_title("China Market Out-of-Sample Trajectory (2010-2025)", color='#CBA6F7', pad=15)
    axes[0,1].legend(frameon=False, labelcolor='#A6ADC8')
    axes[0,1].grid(True, linestyle='--', alpha=0.2, color='#A6ADC8')
    
    # Bottom-Left: US 2008 Crisis Drawdown
    us_stress = all_results["US"]["stress"]
    axes[1,0].plot(us_stress["black_litterman"]["drawdown_series"], color='#F38BA8', linewidth=2, label="BL Drawdown")
    axes[1,0].plot(us_stress["markowitz"]["drawdown_series"], color='#89DCEB', linewidth=1.5, linestyle='--', label="MW Drawdown")
    axes[1,0].plot(us_stress["benchmark"]["drawdown_series"], color='#F9E2AF', linewidth=1.5, alpha=0.6, label="GSPC Drawdown")
    axes[1,0].fill_between(us_stress["black_litterman"]["drawdown_series"].index, us_stress["black_litterman"]["drawdown_series"], 0, color='#F38BA8', alpha=0.1)
    axes[1,0].set_title("US 2008 Financial Crisis Absolute Drawdown", color='#CBA6F7', pad=15)
    axes[1,0].legend(frameon=False, labelcolor='#A6ADC8')
    axes[1,0].grid(True, linestyle='--', alpha=0.2, color='#A6ADC8')
    
    # Bottom-Right: China 2015 Crisis Drawdown
    cn_stress = all_results["CHINA"]["stress"]
    axes[1,1].plot(cn_stress["black_litterman"]["drawdown_series"], color='#F38BA8', linewidth=2, label="BL Drawdown")
    axes[1,1].plot(cn_stress["markowitz"]["drawdown_series"], color='#89DCEB', linewidth=1.5, linestyle='--', label="MW Drawdown")
    axes[1,1].plot(cn_stress["benchmark"]["drawdown_series"], color='#F9E2AF', linewidth=1.5, alpha=0.6, label="Shanghai Comp Drawdown")
    axes[1,1].fill_between(cn_stress["black_litterman"]["drawdown_series"].index, cn_stress["black_litterman"]["drawdown_series"], 0, color='#F38BA8', alpha=0.1)
    axes[1,1].set_title("China 2015 Financial Crisis Absolute Drawdown", color='#CBA6F7', pad=15)
    axes[1,1].legend(frameon=False, labelcolor='#A6ADC8')
    axes[1,1].grid(True, linestyle='--', alpha=0.2, color='#A6ADC8')
    
    plt.tight_layout(pad=3.0)
    plt.savefig(f"{save_dir}/tri_market_dashboard.png", dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    print("[EXPORT] results/tri_market_dashboard.png generated")

if __name__ == "__main__":
    print("=========================================================================")
    print(" EMPIRICAL EVALUATION ENGINE: US DEVELOPED, CHINA & INDIA EMERGING")
    print("=========================================================================")
    
    # 5. Execute Both Markets
    all_results = {}
    for market_name, config in MARKET_CONFIG.items():
        all_results[market_name] = run_market_pipeline(market_name, config)
        
    print("\n=========================================================================")
    print(" CROSS-MARKET SYNTHESIS & REPORT GENERATION")
    print("=========================================================================")
    generate_cross_market_summary(all_results)
    generate_structural_analysis(all_results)
    plot_tri_market_dashboard(all_results)
    
    print("\n[OK] TRI-MARKET EMPIRICAL STUDY EXECUTED SUCCESSFULLY.")
    print("      All artifacts reside in the local `/results` tracking directory.")
