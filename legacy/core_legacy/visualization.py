"""Visualization utilities for the China Structural Study.

Provides a set of plotting helpers that integrate with the dashboard.
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def plot_cumulative_returns(series_dict: dict, title: str = 'Cumulative Returns'):
    plt.figure(figsize=(10,6))
    for label, series in series_dict.items():
        (1+series.fillna(0)).cumprod().plot(label=label)
    plt.legend()
    plt.title(title)
    plt.grid(True)
    return plt.gcf()


def plot_rolling_sharpe(series_dict: dict, window: int = 63, title: str = 'Rolling Sharpe'):
    plt.figure(figsize=(10,4))
    for label, series in series_dict.items():
        rolling_sh = (series.rolling(window).mean() / series.rolling(window).std()) * np.sqrt(252)
        rolling_sh.plot(label=label)
    plt.legend()
    plt.title(title)
    plt.grid(True)
    return plt.gcf()


def plot_allocation_drift_heatmap(weight_history: pd.DataFrame, title: str = 'Allocation Drift Heatmap'):
    plt.figure(figsize=(12,6))
    import seaborn as sns
    sns.heatmap(weight_history.T, cmap='viridis', cbar_kws={'label': 'weight'})
    plt.title(title)
    return plt.gcf()


def plot_tau_timeline(dates: pd.DatetimeIndex, taus: pd.Series, title: str = 'Tau Regime Timeline'):
    plt.figure(figsize=(12,2))
    plt.plot(dates, taus, drawstyle='steps-post')
    plt.title(title)
    plt.yticks(sorted(taus.unique()))
    plt.grid(True)
    return plt.gcf()
