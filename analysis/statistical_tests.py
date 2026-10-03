import numpy as np
import pandas as pd
from scipy import stats


def _annualized_sharpe(values, periods_per_year=252):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) < 2:
        return np.nan
    sigma = values.std(ddof=1)
    if sigma == 0:
        return np.nan
    return values.mean() / sigma * np.sqrt(periods_per_year)


def circular_block_bootstrap_sharpe_difference(
    returns_a,
    returns_b,
    block_size=20,
    iterations=2000,
    seed=42,
):
    """
    Paired circular-block bootstrap for the difference in annualized Sharpe ratios.

    The two strategy return series are resampled with the same block indices so their
    contemporaneous dependence is preserved.
    """
    df = pd.concat(
        [pd.Series(returns_a, name="a"), pd.Series(returns_b, name="b")],
        axis=1,
    ).dropna()

    if len(df) < max(10, block_size):
        raise ValueError("Insufficient aligned observations for block bootstrap")

    a = df["a"].to_numpy(dtype=float)
    b = df["b"].to_numpy(dtype=float)
    n = len(df)
    rng = np.random.default_rng(seed)

    observed = _annualized_sharpe(a) - _annualized_sharpe(b)
    diffs = np.empty(iterations, dtype=float)

    blocks_needed = int(np.ceil(n / block_size))
    for i in range(iterations):
        starts = rng.integers(0, n, size=blocks_needed)
        idx = np.concatenate([
            (np.arange(start, start + block_size) % n) for start in starts
        ])[:n]
        diffs[i] = _annualized_sharpe(a[idx]) - _annualized_sharpe(b[idx])

    # Center the empirical distribution to represent the null of zero difference.
    centered = diffs - np.nanmean(diffs)
    p_value = float(np.nanmean(np.abs(centered) >= abs(observed)))

    return {
        "observed_sharpe_difference": float(observed),
        "p_value": p_value,
        "block_size": int(block_size),
        "iterations": int(iterations),
        "seed": int(seed),
        "bootstrap_differences": diffs,
    }


def circular_block_bootstrap(returns_array, block_size, iterations=1000, seed=42):
    """Backward-compatible circular bootstrap of the sample mean."""
    values = np.asarray(returns_array, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) < block_size:
        raise ValueError("block_size cannot exceed the number of valid observations")

    n = len(values)
    rng = np.random.default_rng(seed)
    out = np.empty(iterations, dtype=float)
    blocks_needed = int(np.ceil(n / block_size))

    for i in range(iterations):
        starts = rng.integers(0, n, size=blocks_needed)
        idx = np.concatenate([
            (np.arange(start, start + block_size) % n) for start in starts
        ])[:n]
        out[i] = values[idx].mean()
    return out


def execute_t_test_divergence(distribution_a, distribution_b):
    """Welch two-sample t-test for descriptive robustness checks."""
    t_stat, p_val = stats.ttest_ind(
        np.asarray(distribution_a, dtype=float),
        np.asarray(distribution_b, dtype=float),
        equal_var=False,
        nan_policy="omit",
    )
    return float(t_stat), float(p_val)


def jobson_korkie_test(returns_a, returns_b, rf=0.0):
    """
    Basic Jobson-Korkie-style Sharpe-ratio difference test for correlated returns.

    This implementation is retained for comparability with the paper. Because the
    original Jobson-Korkie statistic is sensitive to non-normality and finite samples,
    the paired circular-block bootstrap should be treated as the primary robustness
    check in empirical reporting.
    """
    df = pd.concat(
        [pd.Series(returns_a, name="a"), pd.Series(returns_b, name="b")],
        axis=1,
    ).dropna()
    if len(df) < 3:
        raise ValueError("At least three aligned return observations are required")

    a = df["a"].to_numpy(dtype=float) - float(rf) / 252.0
    b = df["b"].to_numpy(dtype=float) - float(rf) / 252.0
    n = len(a)

    mean_a, mean_b = a.mean(), b.mean()
    var_a, var_b = a.var(ddof=1), b.var(ddof=1)
    cov_ab = np.cov(a, b, ddof=1)[0, 1]

    if var_a <= 0 or var_b <= 0:
        return {"stat": np.nan, "p_value": np.nan, "n": n}

    sharpe_a = mean_a / np.sqrt(var_a)
    sharpe_b = mean_b / np.sqrt(var_b)

    # Delta-method variance of the difference in Sharpe ratios.
    # This is reported as a basic JK-style diagnostic, not as the sole inference.
    rho = cov_ab / np.sqrt(var_a * var_b)
    variance = (
        2.0 * (1.0 - rho)
        + 0.5 * (
            sharpe_a**2
            + sharpe_b**2
            - 2.0 * rho**2 * sharpe_a * sharpe_b
        )
    ) / n

    if variance <= 0 or not np.isfinite(variance):
        return {"stat": np.nan, "p_value": np.nan, "n": n}

    stat = (sharpe_a - sharpe_b) / np.sqrt(variance)
    p_value = 2.0 * (1.0 - stats.norm.cdf(abs(stat)))
    return {
        "stat": float(stat),
        "p_value": float(p_value),
        "n": int(n),
        "sharpe_a_daily": float(sharpe_a),
        "sharpe_b_daily": float(sharpe_b),
    }
