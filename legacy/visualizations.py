"""
Visualization Module for Black-Litterman Portfolio Optimization
================================================================

Generates comprehensive visualizations including efficient frontier,
portfolio comparisons, cumulative returns, and risk analysis plots.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')


class PortfolioVisualizer:
    """Generate professional visualizations for portfolio optimization."""
    
    def __init__(self, optimizer, results):
        """
        Initialize visualizer.
        
        Parameters:
        -----------
        optimizer : BlackLittermanOptimizer
            The optimizer object with data and calculations
        results : dict
            Results from compare_models()
        """
        self.optimizer = optimizer
        self.results = results
        self.style = 'seaborn-v0_8-darkgrid'
        plt.style.use(self.style)
        sns.set_palette("husl")
    
    def plot_efficient_frontier(self, n_portfolios=500, figsize=(12, 8), save_dir="results"):
        """
        Plot the efficient frontier comparing Markowitz and Black-Litterman.
        
        Parameters:
        -----------
        n_portfolios : int
            Number of random portfolios to generate for comparison
        figsize : tuple
            Figure size (width, height)
        """
        # Generate random portfolios for context
        np.random.seed(42)
        returns_list = []
        volatility_list = []
        sharpe_list = []
        
        for _ in range(n_portfolios):
            weights = np.random.random(len(self.optimizer.ticker_list))
            weights /= np.sum(weights)
            
            # Use BL returns for random portfolios
            portfolio_return = np.sum(weights * self.optimizer.bl_returns)
            portfolio_vol = np.sqrt(weights @ self.optimizer.cov_matrix @ weights)
            sharpe = (portfolio_return - self.optimizer.risk_free_rate) / portfolio_vol
            
            returns_list.append(portfolio_return)
            volatility_list.append(portfolio_vol)
            sharpe_list.append(sharpe)
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot random portfolios
        scatter = ax.scatter(volatility_list, returns_list, c=sharpe_list, 
                            cmap='viridis', alpha=0.5, s=30, label='Random Portfolios')
        
        # Plot optimized portfolios
        markowitz = self.results['markowitz']
        bl = self.results['black_litterman']
        equal = self.results['equal_weight']
        
        markowitz_vol = np.sqrt(markowitz['weights'] @ self.optimizer.cov_matrix @ 
                               markowitz['weights'])
        bl_vol = np.sqrt(bl['weights'] @ self.optimizer.cov_matrix @ bl['weights'])
        equal_vol = np.sqrt(equal['weights'] @ self.optimizer.cov_matrix @ equal['weights'])
        
        markowitz_ret = markowitz['metrics']['Expected Return']
        bl_ret = bl['metrics']['Expected Return']
        equal_ret = equal['metrics']['Expected Return']
        
        # Plot optimal portfolios
        ax.scatter(markowitz_vol, markowitz_ret, s=300, marker='*', 
                  color='red', edgecolors='darkred', linewidth=2, 
                  label='Markowitz Maximum Sharpe', zorder=5)
        
        ax.scatter(bl_vol, bl_ret, s=300, marker='*', 
                  color='green', edgecolors='darkgreen', linewidth=2,
                  label='Black-Litterman Maximum Sharpe', zorder=5)
        
        ax.scatter(equal_vol, equal_ret, s=300, marker='s', 
                  color='blue', edgecolors='darkblue', linewidth=2,
                  label='Equal-Weight Benchmark', zorder=5)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Sharpe Ratio', fontsize=11, fontweight='bold')
        
        # Labels and formatting
        ax.set_xlabel('Volatility (Annual)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Expected Return (Annual)', fontsize=12, fontweight='bold')
        ax.set_title('Efficient Frontier: Markowitz vs Black-Litterman Model', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=10, framealpha=0.95)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{save_dir}/efficient_frontier.png', dpi=300, bbox_inches='tight')
        print(f"[OK] Saved: {save_dir}/efficient_frontier.png")
        
    
    def plot_weight_comparison(self, figsize=(14, 6), save_dir="results"):
        """Plot portfolio weights comparison across models."""
        
        models_data = {
            'Markowitz': self.results['markowitz']['weights'],
            'Black-Litterman': self.results['black_litterman']['weights'],
            'Equal-Weight': self.results['equal_weight']['weights']
        }
        
        fig, axes = plt.subplots(1, 3, figsize=figsize, sharey=True)
        colors = sns.color_palette("Set2", len(self.optimizer.ticker_list))
        
        for idx, (model_name, weights) in enumerate(models_data.items()):
            ax = axes[idx]
            
            # Create bar chart
            bars = ax.bar(self.optimizer.ticker_list, weights, color=colors, 
                         edgecolor='black', linewidth=1.5)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1%}', ha='center', va='bottom', fontsize=9)
            
            ax.set_title(model_name, fontsize=12, fontweight='bold')
            ax.set_ylabel('Weight' if idx == 0 else '', fontsize=11, fontweight='bold')
            ax.set_ylim(0, max(weights) * 1.15)
            ax.grid(axis='y', alpha=0.3)
        
        fig.suptitle('Portfolio Weights Comparison', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(f'{save_dir}/weight_comparison.png', dpi=300, bbox_inches='tight')
        print(f"[OK] Saved: {save_dir}/weight_comparison.png")
        
    
    def plot_cumulative_returns(self, figsize=(12, 7), save_dir="results"):
        """Plot cumulative returns for optimized portfolios."""
        
        # Calculate cumulative returns
        daily_returns = self.optimizer.returns
        
        # Markowitz portfolio
        markowitz_weights = self.results['markowitz']['weights']
        markowitz_daily_ret = (daily_returns @ markowitz_weights).values
        markowitz_cumulative = (1 + markowitz_daily_ret).cumprod()
        
        # Black-Litterman portfolio
        bl_weights = self.results['black_litterman']['weights']
        bl_daily_ret = (daily_returns @ bl_weights).values
        bl_cumulative = (1 + bl_daily_ret).cumprod()
        
        # Equal-weight portfolio
        equal_weights = self.results['equal_weight']['weights']
        equal_daily_ret = (daily_returns @ equal_weights).values
        equal_cumulative = (1 + equal_daily_ret).cumprod()
        
        # Create plot
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.plot(daily_returns.index, markowitz_cumulative, linewidth=2, 
               label='Markowitz', alpha=0.8, color='red')
        ax.plot(daily_returns.index, bl_cumulative, linewidth=2.5, 
               label='Black-Litterman', alpha=0.8, color='green')
        ax.plot(daily_returns.index, equal_cumulative, linewidth=2, 
               label='Equal-Weight', alpha=0.8, color='blue')
        
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Cumulative Return', fontsize=12, fontweight='bold')
        ax.set_title('Portfolio Cumulative Returns (Out-of-Sample)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=11, framealpha=0.95)
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y-1)))
        
        plt.tight_layout()
        plt.savefig(f'{save_dir}/cumulative_returns.png', dpi=300, bbox_inches='tight')
        print(f"[OK] Saved: {save_dir}/cumulative_returns.png")
        
    
    def plot_drawdown(self, figsize=(12, 7), save_dir="results"):
        """Plot maximum drawdown analysis."""
        
        daily_returns = self.optimizer.returns
        
        # Calculate drawdowns for each portfolio
        portfolios = {
            'Markowitz': self.results['markowitz']['weights'],
            'Black-Litterman': self.results['black_litterman']['weights'],
            'Equal-Weight': self.results['equal_weight']['weights']
        }
        
        fig, ax = plt.subplots(figsize=figsize)
        colors = ['red', 'green', 'blue']
        
        for (name, weights), color in zip(portfolios.items(), colors):
            # Calculate cumulative returns
            portfolio_ret = (daily_returns @ weights).values
            cumulative = (1 + portfolio_ret).cumprod()
            
            # Calculate running maximum and drawdown
            running_max = np.maximum.accumulate(cumulative)
            drawdown = (cumulative - running_max) / running_max
            
            ax.fill_between(daily_returns.index, drawdown, 0, alpha=0.3, 
                           color=color, label=name)
        
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Drawdown', fontsize=12, fontweight='bold')
        ax.set_title('Portfolio Drawdown Over Time', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=11, framealpha=0.95)
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
        
        plt.tight_layout()
        plt.savefig(f'{save_dir}/drawdown.png', dpi=300, bbox_inches='tight')
        print(f"[OK] Saved: {save_dir}/drawdown.png")
        
    
    def plot_risk_metrics_comparison(self, figsize=(14, 8), save_dir="results"):
        """Plot comprehensive risk metrics comparison."""
        
        metrics_to_plot = ['Expected Return', 'Volatility', 'Sharpe Ratio', 'Max Drawdown']
        
        # Prepare data
        data_dict = {}
        for model_name, model_data in self.results.items():
            data_dict[model_name.replace('_', ' ').title()] = model_data['metrics']
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()
        
        colors = sns.color_palette("Set2", len(data_dict))
        
        for idx, metric in enumerate(metrics_to_plot):
            ax = axes[idx]
            
            values = [data_dict[model][metric] for model in data_dict.keys()]
            bars = ax.bar(data_dict.keys(), values, color=colors, 
                         edgecolor='black', linewidth=1.5)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                if metric in ['Expected Return', 'Volatility', 'Max Drawdown']:
                    label = f'{height:.2%}'
                else:
                    label = f'{height:.3f}'
                
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       label, ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            ax.set_title(metric, fontsize=12, fontweight='bold')
            ax.set_ylabel('Value', fontsize=10, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            ax.set_ylim(0, max(values) * 1.2 if metric != 'Max Drawdown' else None)
        
        fig.suptitle('Risk Metrics Comparison', fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig(f'{save_dir}/risk_metrics.png', dpi=300, bbox_inches='tight')
        print(f"[OK] Saved: {save_dir}/risk_metrics.png")
        
    
    def plot_correlation_heatmap(self, figsize=(10, 8), save_dir="results"):
        """Plot correlation matrix heatmap."""
        
        fig, ax = plt.subplots(figsize=figsize)
        
        corr_matrix = self.optimizer.returns.corr()
        
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                   center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                   ax=ax, vmin=-1, vmax=1)
        
        ax.set_title('Asset Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(f'{save_dir}/correlation_matrix.png', dpi=300, bbox_inches='tight')
        print(f"[OK] Saved: {save_dir}/correlation_matrix.png")
        
    
    def generate_all_visualizations(self):
        """Generate all visualizations."""
        
        print("\n" + "="*60)
        print("GENERATING VISUALIZATIONS")
        print("="*60)
        
        self.plot_correlation_heatmap()
        self.plot_efficient_frontier()
        self.plot_weight_comparison()
        self.plot_cumulative_returns()
        self.plot_drawdown()
        self.plot_risk_metrics_comparison()
        
        print("\n[OK] All base visualizations generated successfully!")


def create_visualizations(optimizer, results):
    """Convenience function to create all visualizations."""
    visualizer = PortfolioVisualizer(optimizer, results)
    visualizer.generate_all_visualizations()

# ---------------------------------------------------------
# Robustness & Dashboard Visualizations
# ---------------------------------------------------------

def plot_tau_sensitivity(df, save_dir="results"):
    """Plot the 3-panel Matplotlib graphic for Tau Sensitivity."""
    import os
    fig = plt.figure(figsize=(15, 12))
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # Subplot 1: Tau vs Sharpe Ratio
    plt.subplot(3, 1, 1)
    plt.plot(df.index, df['Sharpe Ratio'], marker='o', color='green', linewidth=2)
    plt.title('Tau (τ) vs Sharpe Ratio', fontsize=14, fontweight='bold')
    plt.ylabel('Sharpe Ratio', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Subplot 2: Tau vs Volatility vs Expected Return
    plt.subplot(3, 1, 2)
    ax1 = plt.gca()
    ax2 = ax1.twinx()
    
    line1 = ax1.plot(df.index, df['Volatility'] * 100, marker='s', color='orange', label='Volatility')
    line2 = ax2.plot(df.index, df['Expected Return'] * 100, marker='^', color='blue', label='Expected Return')
    
    ax1.set_ylabel('Volatility (%)', fontsize=12, color='orange')
    ax2.set_ylabel('Expected Return (%)', fontsize=12, color='blue')
    plt.title('Tau (τ) vs Expected Return & Volatility', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')
    
    # Subplot 3: Portfolio Weight Drift Mapping
    plt.subplot(3, 1, 3)
    weight_cols = [c for c in df.columns if c.startswith('Weight_')]
    weights_data = df[weight_cols]
    labels = [c.replace('Weight_', '') for c in weight_cols]
    
    plt.stackplot(df.index, weights_data.T * 100, labels=labels, alpha=0.8)
    plt.title('Portfolio Weight Distribution vs Tau (τ)', fontsize=14, fontweight='bold')
    plt.xlabel('Tau (τ)', fontsize=12)
    plt.ylabel('Allocation (%)', fontsize=12)
    plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, 'tau_sensitivity.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_lambda_sensitivity(df, save_dir="results"):
    """Plot the 2-panel Matplotlib graphic for Lambda Sensitivity."""
    import os
    fig = plt.figure(figsize=(15, 10))
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # Subplot 1: Lambda vs Sharpe Ratio
    plt.subplot(2, 1, 1)
    plt.plot(df.index, df['Sharpe Ratio'], marker='o', color='purple', linewidth=2)
    plt.title('Risk Aversion (λ) vs Sharpe Ratio', fontsize=14, fontweight='bold')
    plt.ylabel('Sharpe Ratio', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(df.index)
    
    # Subplot 2: Lambda vs Expected Return
    plt.subplot(2, 1, 2)
    plt.plot(df.index, df['Expected Return'] * 100, marker='^', color='teal', linewidth=2)
    plt.title('Risk Aversion (λ) vs Expected Return', fontsize=14, fontweight='bold')
    plt.xlabel('Risk Aversion Coef (λ)', fontsize=12)
    plt.ylabel('Expected Return (%)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(df.index)
    
    plt.tight_layout()
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, 'lambda_sensitivity.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_stress_test(tester_results, save_dir="results"):
    """Generate 2-panel rendering tracking cumulative falls and drawdown vectors."""
    import os
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [2, 1]}, sharex=True)
    plt.style.use('seaborn-v0_8-darkgrid')
    
    colors = {
        'black_litterman': '#1E88E5',
        'markowitz': '#E53935',
        'equal_weight': '#8E24AA',
        'benchmark': '#43A047'
    }
    
    display_names = {
        'black_litterman': 'Black-Litterman Allocation',
        'markowitz': 'Markowitz Mean-Variance',
        'equal_weight': 'Equal Weight Portfolio',
        'benchmark': 'S&P 500 (^GSPC)'
    }
    
    for name, metrics in tester_results.items():
        cum_rets = metrics['cumulative_series']
        val_series = cum_rets * 100
        
        ls = '-' if name != 'benchmark' else '--'
        lw = 2.5 if name == 'black_litterman' else 1.5
        alpha = 1.0 if name == 'black_litterman' else 0.8
        
        ax1.plot(val_series.index, val_series, label=display_names[name], 
                 color=colors[name], linestyle=ls, linewidth=lw, alpha=alpha)
        
    ax1.set_title('2008 Financial Crisis Simulation: Cumulative Trajectories', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Portfolio Value (Baseline %)', fontsize=12)
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    for name, metrics in tester_results.items():
        dd_series = metrics['drawdown_series'] * 100
        
        ls = '-' if name != 'benchmark' else '--'
        lw = 2.0 if name == 'black_litterman' else 1.0
        alpha = 0.9 if name == 'black_litterman' else 0.5
        
        if name == 'black_litterman':
            ax2.fill_between(dd_series.index, dd_series, 0, color=colors[name], alpha=0.2)
            
        ax2.plot(dd_series.index, dd_series, color=colors[name], linestyle=ls, linewidth=lw, alpha=alpha)
        
    ax2.set_title('Geometric Drawdown Depths (%)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Drawdown (%)', fontsize=12)
    ax2.set_xlabel('Date', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, 'stress_test_2008.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_final_research_dashboard(backtest_results, stress_results, save_dir="results"):
    """
    Generate the Master Output Dashboard containing:
    - Cumulative Return Comparison
    - Gross vs Net BL Performance
    - Benchmark comparison
    - Stress Test Depth
    """
    import os
    fig = plt.figure(figsize=(20, 14))
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # 1. Cumulative Out of Sample Returns
    ax1 = plt.subplot(2, 2, 1)
    bl_net = backtest_results['black_litterman']['net']
    mw_net = backtest_results['markowitz']['net']
    sp500 = backtest_results['sp500']
    
    ax1.plot(bl_net.index, (1 + bl_net).cumprod() * 100, label='Black-Litterman (Net)', color='#1E88E5', lw=2)
    ax1.plot(mw_net.index, (1 + mw_net).cumprod() * 100, label='Markowitz (Net)', color='#E53935', lw=1.5)
    ax1.plot(sp500.index, (1 + sp500).cumprod() * 100, label='S&P 500', color='#43A047', ls='--', lw=1.5)
    ax1.set_title('Out-of-Sample Cumulative Returns', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Portfolio Value (%)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Gross vs Net Returns
    ax2 = plt.subplot(2, 2, 2)
    bl_gross = backtest_results['black_litterman']['gross']
    ax2.plot(bl_gross.index, (1 + bl_gross).cumprod() * 100, label='BL Gross', color='#8E24AA', lw=2)
    ax2.plot(bl_net.index, (1 + bl_net).cumprod() * 100, label='BL Net (After Costs)', color='#1E88E5', lw=2)
    ax2.fill_between(bl_net.index, (1 + bl_gross).cumprod() * 100, (1 + bl_net).cumprod() * 100, color='red', alpha=0.1, label='Friction Drag')
    ax2.set_title('Impact of Transaction Costs & Slippage', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Portfolio Value (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Rolling Drawdowns (Backtest)
    ax3 = plt.subplot(2, 2, 3)
    bl_cum = (1 + bl_net).cumprod()
    sp_cum = (1 + sp500).cumprod()
    bl_dd = (bl_cum - bl_cum.cummax()) / bl_cum.cummax() * 100
    sp_dd = (sp_cum - sp_cum.cummax()) / sp_cum.cummax() * 100
    ax3.plot(bl_dd.index, bl_dd, label='BL Drawdown', color='#1E88E5')
    ax3.plot(sp_dd.index, sp_dd, label='S&P 500 Drawdown', color='#43A047', ls='--')
    ax3.fill_between(bl_dd.index, bl_dd, 0, alpha=0.2, color='#1E88E5')
    ax3.set_title('Rolling Drawdown Trajectory', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Drawdown (%)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Stress Test 2008 Plunge
    ax4 = plt.subplot(2, 2, 4)
    bl_08_dd = stress_results['black_litterman']['drawdown_series'] * 100
    sp_08_dd = stress_results['benchmark']['drawdown_series'] * 100
    ax4.plot(bl_08_dd.index, bl_08_dd, label='BL 2008 Fall', color='#1E88E5', lw=2)
    ax4.plot(sp_08_dd.index, sp_08_dd, label='S&P 500 2008 Fall', color='#43A047', ls='--', lw=2)
    ax4.fill_between(bl_08_dd.index, bl_08_dd, 0, alpha=0.2, color='#1E88E5')
    ax4.set_title('2008 Global Financial Crisis Stress Test', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Drawdown Depth (%)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, 'final_research_dashboard.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_benchmark_comparison(backtest_results, save_dir="results"):
    """Plot cumulative returns of models against benchmarks and save plot."""
    import os
    os.makedirs(save_dir, exist_ok=True)
    
    plt.figure(figsize=(12, 7))
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # Calculate cumulative returns
    models = {
        'MW (Net)': backtest_results['markowitz']['net'],
        'MW (Gross)': backtest_results['markowitz']['gross'],
        'BL (Net)': backtest_results['black_litterman']['net'],
        'BL (Gross)': backtest_results['black_litterman']['gross'],
        'Equal-Weight (Net)': backtest_results['equal_weight']['net'],
        'S&P 500 (^GSPC)': backtest_results['sp500'],
        'CSI 300 (000300.SS)': backtest_results['csi300']
    }
    
    colors = {
        'MW (Net)': '#ff7f0e',
        'MW (Gross)': '#ffbb78',
        'BL (Net)': '#1f77b4',
        'BL (Gross)': '#aec7e8',
        'Equal-Weight (Net)': '#2ca02c',
        'S&P 500 (^GSPC)': '#d62728',
        'CSI 300 (000300.SS)': '#9467bd'
    }
    
    for name, returns in models.items():
        cum_rets = (1 + returns).cumprod() - 1
        ls = '--' if 'Gross' in name else '-'
        alpha = 0.5 if 'Gross' in name else 1.0
        plt.plot(cum_rets.index, cum_rets * 100, label=name, color=colors[name], 
                 linewidth=2.0, linestyle=ls, alpha=alpha)
        
    plt.title('Out-of-Sample Cumulative Returns vs Benchmarks (Gross/Net)', fontsize=14, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Cumulative Return (%)', fontsize=12)
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    save_path = os.path.join(save_dir, 'benchmark_comparison.png')
    plt.savefig(save_path, dpi=300)
    plt.close()

def plot_turnover_history(backtest_results, save_dir="results"):
    """Plot turnover rates at each rebalance period over time."""
    import os
    os.makedirs(save_dir, exist_ok=True)
    
    plt.figure(figsize=(12, 5))
    plt.style.use('seaborn-v0_8-darkgrid')
    
    models = {
        'Markowitz': backtest_results['turnover']['markowitz'],
        'Black-Litterman': backtest_results['turnover']['black_litterman'],
        'Equal-Weight': backtest_results['turnover']['equal_weight'],
    }
    
    colors = {
        'Markowitz': '#ff7f0e',
        'Black-Litterman': '#1f77b4',
        'Equal-Weight': '#2ca02c',
    }
    
    for name, turnover in models.items():
        if not turnover.empty:
            plt.bar(turnover.index, turnover * 100, label=name, color=colors[name], 
                    alpha=0.6, width=15)
        
    plt.title('Portfolio Asset Turnover at Rolling Rebalances', fontsize=14, fontweight='bold')
    plt.xlabel('Rebalance Date', fontsize=12)
    plt.ylabel('Turnover Weight Transacted (%)', fontsize=12)
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    save_path = os.path.join(save_dir, 'turnover_history.png')
    plt.savefig(save_path, dpi=300)
    plt.close()
