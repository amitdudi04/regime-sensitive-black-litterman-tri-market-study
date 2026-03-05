import matplotlib.pyplot as plt
import os

def check_vis_dir():
    vis_dir = os.path.join(os.path.dirname(__file__))
    return vis_dir

def plot_cumulative_returns(oos_returns_dict, title="Cumulative Out-of-Sample Returns", filename="cumulative_returns.png"):
    plt.figure(figsize=(10, 6))
    for label, series in oos_returns_dict.items():
        cumulative = (1 + series).cumprod() - 1
        plt.plot(cumulative.index, cumulative.values, label=label)
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    filepath = os.path.join(check_vis_dir(), filename)
    plt.savefig(filepath)
    plt.close()

def plot_rolling_sharpe(returns_dict, window=252, title="Rolling OOS Sharpe Ratio Comparison", filename="rolling_sharpe.png"):
    plt.figure(figsize=(10, 6))
    for label, series in returns_dict.items():
        rolling_mean = series.rolling(window=window).mean()
        rolling_std = series.rolling(window=window).std()
        rolling_sharpe = (rolling_mean / rolling_std) * (252 ** 0.5)
        plt.plot(rolling_sharpe.index, rolling_sharpe.values, label=label)
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    filepath = os.path.join(check_vis_dir(), filename)
    plt.savefig(filepath)
    plt.close()

def plot_drawdown_comparison(returns_dict, title="Drawdown Comparison", filename="drawdown_comparison.png"):
    plt.figure(figsize=(10, 6))
    for label, series in returns_dict.items():
        cumulative = (1 + series).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        plt.plot(drawdown.index, drawdown.values, label=label, alpha=0.7)
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    filepath = os.path.join(check_vis_dir(), filename)
    plt.savefig(filepath)
    plt.close()

def plot_asi_stability(asi_series_dict, title="Allocation Stability Index (ASI) Drift", filename="asi_stability.png"):
    plt.figure(figsize=(10, 6))
    for label, series in asi_series_dict.items():
        plt.plot(series.index, series.values, label=label)
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    filepath = os.path.join(check_vis_dir(), filename)
    plt.savefig(filepath)
    plt.close()

def plot_tau_sensitivity(tau_sharpe_df, title="Tau Robustness Sensitivity", filename="tau_sensitivity.png"):
    plt.figure(figsize=(10, 6))
    plt.plot(tau_sharpe_df['Tau'], tau_sharpe_df['Sharpe'], marker='o', linestyle='-', color='b')
    plt.title(title)
    plt.xlabel('Tau Uncertainty Parameter')
    plt.ylabel('Out-of-Sample Sharpe Ratio')
    plt.grid(True, alpha=0.3)
    filepath = os.path.join(check_vis_dir(), filename)
    plt.savefig(filepath)
    plt.close()

def plot_regime_probabilities(regime_classifications, title="Regime Probabilities (Markov Switching)", filename="regime_probabilities.png"):
    plt.figure(figsize=(10, 6))
    plt.plot(regime_classifications.index, regime_classifications['Prob_High_Vol'], label="High Volatility Regime", color='red', alpha=0.7)
    plt.plot(regime_classifications.index, regime_classifications['Prob_Low_Vol'], label="Low Volatility Regime", color='blue', alpha=0.7)
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    filepath = os.path.join(check_vis_dir(), filename)
    plt.savefig(filepath)
    plt.close()

def plot_regime_performance_comparison(regime_summary_df, title="Sharpe Ratio Comparison by Regime", filename="regime_performance_comparison.png"):
    plt.figure(figsize=(10, 6))
    regimes = regime_summary_df['Regime'].tolist()
    bl_sharpe = regime_summary_df['BL Sharpe'].tolist()
    mv_sharpe = regime_summary_df['Markowitz Sharpe'].tolist()
    
    x = range(len(regimes))
    width = 0.35
    
    plt.bar([i - width/2 for i in x], bl_sharpe, width, label='Black-Litterman', color='blue', alpha=0.8)
    plt.bar([i + width/2 for i in x], mv_sharpe, width, label='Markowitz', color='orange', alpha=0.8)
    
    plt.title(title)
    plt.xticks(x, regimes)
    plt.ylabel('Sharpe Ratio')
    plt.legend()
    plt.grid(True, axis='y', alpha=0.3)
    
    filepath = os.path.join(check_vis_dir(), filename)
    plt.savefig(filepath)
    plt.close()
