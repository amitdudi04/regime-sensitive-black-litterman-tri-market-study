"""Formal statistical tests for performance comparison.

Includes Jobson-Korkie Sharpe difference test (basic implementation),
bootstrap Sharpe difference, turnover t-test, and ASI calculation.
"""
import numpy as np
import pandas as pd
from scipy import stats


def asi_from_weights(weight_history: pd.DataFrame) -> float:
    """Allocation Stability Index (ASI) = mean L1 norm of weight differences."""
    if len(weight_history) <= 1:
        return 0.0
    diffs = weight_history.diff().abs().dropna()
    l1 = diffs.sum(axis=1)
    return float(l1.mean())


def turnover_series_from_weights(weight_history: pd.DataFrame) -> pd.Series:
    """Compute turnover per rebalance as L1 distance between consecutive weight vectors."""
    return weight_history.diff().abs().sum(axis=1).dropna()


def bootstrap_sharpe_diff(strategy_returns_a: pd.Series, strategy_returns_b: pd.Series, n_bootstrap: int = 1000, seed: int = 42):
    """Bootstrap the difference in Sharpe ratios between two return series.

    Returns: (observed_diff, p_value, bootstrap_diffs)
    """
    rng = np.random.default_rng(seed)
    obs_sharpe_a = (strategy_returns_a.mean() / strategy_returns_a.std()) * np.sqrt(252)
    obs_sharpe_b = (strategy_returns_b.mean() / strategy_returns_b.std()) * np.sqrt(252)
    obs_diff = obs_sharpe_a - obs_sharpe_b

    # Align indices
    combined = pd.concat([strategy_returns_a, strategy_returns_b], axis=1).dropna()
    a = combined.iloc[:,0].values
    b = combined.iloc[:,1].values
    n = len(a)

    boot_diffs = np.zeros(n_bootstrap)
    block_size = max(20, min(63, n // 10))  # standard block size approx 1 month or 20 days
    
    for i in range(n_bootstrap):
        # Circular Block Bootstrap
        start_indices = rng.integers(0, n, size=int(np.ceil(n / block_size)))
        idx = np.concatenate([np.arange(s, s + block_size) % n for s in start_indices])[:n]
        
        sa = a[idx]
        sb = b[idx]
        sa_sh = (sa.mean() / sa.std()) * np.sqrt(252) if sa.std() != 0 else 0.0
        sb_sh = (sb.mean() / sb.std()) * np.sqrt(252) if sb.std() != 0 else 0.0
        boot_diffs[i] = sa_sh - sb_sh

    # Center the bootstrap distribution under the null hypothesis
    boot_diffs_centered = boot_diffs - np.mean(boot_diffs)
    
    # two-sided p-value against the centered distribution
    p_value = np.mean(np.abs(boot_diffs_centered) >= np.abs(obs_diff))
    return obs_diff, p_value, boot_diffs


def jobson_korkie_test(returns_a: pd.Series, returns_b: pd.Series, rf: float = 0.0):
    """Basic Jobson-Korkie test (uncorrected) for Sharpe ratio difference.

    Note: This implements the original test statistics. For small samples,
    consider bootstrap alternative.
    """
    # Align
    df = pd.concat([returns_a, returns_b], axis=1).dropna()
    a = df.iloc[:,0] - rf/252
    b = df.iloc[:,1] - rf/252

    n = len(a)
    # Annualize inputs to match the Sharpe diff scaling
    ra = a.mean() * 252; rb = b.mean() * 252
    sa = a.std(ddof=1) * np.sqrt(252); sb = b.std(ddof=1) * np.sqrt(252)
    sa2 = a.var(ddof=1) * 252; sb2 = b.var(ddof=1) * 252
    rho = np.corrcoef(a, b)[0,1]

    sa_hat = ra / sa
    sb_hat = rb / sb
    denom = np.sqrt((1/n) * ( (1/sa2) * ( (1/4)*(ra**2)/sa2 ) + (1/sb2) * ( (1/4)*(rb**2)/sb2 ) - (rho/(sa*sb))*(ra*rb) ))
    if denom == 0 or np.isnan(denom):
        return {'stat': np.nan, 'p_value': np.nan}
    stat = (sa_hat - sb_hat) / denom
    p_value = 2 * (1 - stats.norm.cdf(np.abs(stat)))
    return {'stat': stat, 'p_value': p_value}


def turnover_ttest(turnover_a: np.ndarray, turnover_b: np.ndarray):
    """Two-sample t-test for difference in mean turnover."""
    return stats.ttest_ind(turnover_a, turnover_b, equal_var=False)
