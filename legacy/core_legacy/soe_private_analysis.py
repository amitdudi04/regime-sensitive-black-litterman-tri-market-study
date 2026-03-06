"""SOE vs Private portfolio analysis for China ownership structural study.

Implements pipelines to run regime-sensitive Black-Litterman portfolios for
SOE, Private, and Combined universes. Computes performance, stability, crisis
metrics, hypothesis tests, visual hooks and export readiness.
"""
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from scipy import stats

from legacy.core_legacy.ownership_classification import SOE_TICKERS, PRIVATE_TICKERS
from legacy.core_legacy.optimizer import BlackLittermanOptimizer
from legacy.core_legacy.regime_detection import rolling_60d_volatility, is_high_vol_regime
from legacy.core_legacy.statistical_tests import asi_from_weights, bootstrap_sharpe_diff, turnover_ttest
from legacy.core_legacy.visualization import plot_cumulative_returns, plot_rolling_sharpe, plot_allocation_drift_heatmap, plot_tau_timeline
from legacy.core_legacy.export_utils import export_csv_summary, export_excel_workbook, dataframe_to_latex
from legacy.core_legacy.backtester import PortfolioBacktester


def _compute_herfindahl(weights: np.ndarray) -> float:
    return float(np.sum(weights**2))


def _max_drawdown(series: pd.Series) -> float:
    cum = (1 + series).cumprod()
    running_max = cum.cummax()
    drawdown = (cum - running_max) / running_max
    return float(drawdown.min())


def _cvar(series: pd.Series, alpha: float = 0.95) -> float:
    if series.empty:
        return np.nan
    var = series.quantile(1-alpha)
    tail = series[series <= var]
    return float(tail.mean())


def _recovery_days(series: pd.Series) -> Optional[int]:
    # Days from trough to recovery to previous peak
    cum = (1 + series).cumprod()
    peak = cum.cummax()
    draw = (cum - peak) / peak
    trough_idx = draw.idxmin()
    trough_value = draw.min()
    # find first date after trough where cum >= previous peak value at trough
    prev_peak_value = peak.loc[:trough_idx].iloc[-1]
    after = cum.loc[trough_idx:]
    recovered = after[after >= prev_peak_value]
    if recovered.empty:
        return None
    days = (recovered.index[0] - trough_idx).days
    return int(days)


def _run_pipeline(tickers: List[str], prices: pd.DataFrame, start_date: str, end_date: str,
                  window: int = 252, rebalance_freq: int = 63, tc_rate: float = 0.001,
                  tau_high: float = 0.01, tau_low: float = 0.05) -> Dict[str, Any]:
    """Run rolling OOS pipeline for a given universe and return structured results.

    Uses the central `PortfolioBacktester` to ensure consistent weight history,
    drift-adjusted turnover and exports.
    """
    price_slice = prices.reindex(columns=tickers).dropna(how='all')
    returns = price_slice.pct_change().dropna()

    optimizer = BlackLittermanOptimizer(tickers, start_date, end_date, covariance_method='ledoit')
    optimizer.prices = price_slice
    optimizer.returns = returns
    optimizer.cov_matrix = optimizer._compute_covariance(returns)

    backtester = PortfolioBacktester(optimizer, window_size=window, rebalance_freq=rebalance_freq, transaction_cost_rate=tc_rate)
    bt_res = backtester.run_backtest(views_dict={})

    # Extract BL-specific outputs (we run a BL-centric backtest)
    net_returns = bt_res['black_litterman']['net']
    gross_returns = bt_res['black_litterman']['gross']
    weights_df = bt_res.get('weight_history', {}).get('black_litterman', pd.DataFrame())
    turnover_series = bt_res.get('turnover_series', {}).get('black_litterman', pd.Series(dtype=float))
    tau_timeline = bt_res.get('tau_timeline', pd.Series(dtype=float))

    # Metrics
    ann_net_ret = float(net_returns.mean() * 252)
    ann_vol = float(net_returns.std() * np.sqrt(252))
    sharpe = (ann_net_ret - optimizer.risk_free_rate) / ann_vol if ann_vol > 0 else np.nan
    max_dd = _max_drawdown(net_returns)
    cvar95 = _cvar(net_returns, alpha=0.95)
    avg_turnover = float(turnover_series.mean()) if not turnover_series.empty else np.nan
    asi = asi_from_weights(weights_df) if not weights_df.empty else np.nan
    herf = float((weights_df**2).sum(axis=1).mean()) if not weights_df.empty else np.nan

    results = {
        'net_returns': net_returns.sort_index(),
        'gross_returns': gross_returns.sort_index(),
        'weights': weights_df,
        'turnover_series': turnover_series,
        'tau_timeline': tau_timeline,
        'metrics': {
            'annualized_net_return': ann_net_ret,
            'annualized_volatility': ann_vol,
            'sharpe': sharpe,
            'information_ratio': np.nan,
            'max_drawdown': max_dd,
            'cvar95': cvar95,
            'average_turnover': avg_turnover,
            'asi': asi,
            'herfindahl': herf
        }
    }

    return results


def run_china_soe_pipeline(prices: pd.DataFrame, start_date: str, end_date: str, **kwargs) -> Dict[str, Any]:
    return _run_pipeline(SOE_TICKERS, prices, start_date, end_date, **kwargs)


def run_china_private_pipeline(prices: pd.DataFrame, start_date: str, end_date: str, **kwargs) -> Dict[str, Any]:
    return _run_pipeline(PRIVATE_TICKERS, prices, start_date, end_date, **kwargs)


def run_combined_china_pipeline(prices: pd.DataFrame, start_date: str, end_date: str, **kwargs) -> Dict[str, Any]:
    combined = list(dict.fromkeys(SOE_TICKERS + PRIVATE_TICKERS))
    return _run_pipeline(combined, prices, start_date, end_date, **kwargs)


def _hypothesis_tests(soe_res: Dict[str, Any], private_res: Dict[str, Any]) -> Dict[str, float]:
    # H1: volatility (downsampled to non-overlapping 63-day periods to avoid spurious precision)
    vol_a = soe_res['net_returns'].rolling(window=63).std().dropna()[::63] * np.sqrt(252)
    vol_b = private_res['net_returns'].rolling(window=63).std().dropna()[::63] * np.sqrt(252)
    t_vol = stats.ttest_ind(vol_a.dropna(), vol_b.dropna(), equal_var=False)

    # H2: ASI
    # compute ASI series per rebalance (L1 differences)
    asi_a_series = soe_res['weights'].diff().abs().sum(axis=1).dropna()
    asi_b_series = private_res['weights'].diff().abs().sum(axis=1).dropna()
    t_asi = stats.ttest_ind(asi_a_series, asi_b_series, equal_var=False)

    # H3: volatility spike during crisis - compare crisis vol multipliers
    # Placeholder: compute ratio of crisis vol to pre-crisis vol
    def safe_float(v):
        return 0.0 if (v is None or np.isnan(v)) else float(v)
        
    tests = {
        'vol_t_stat': safe_float(t_vol.statistic),
        'vol_p_value': safe_float(t_vol.pvalue),
        'asi_t_stat': safe_float(t_asi.statistic),
        'asi_p_value': safe_float(t_asi.pvalue)
    }
    return tests


def run_crisis_structural_tests(prices: pd.DataFrame, train_start: str = '2012-01-01', train_end: str = '2014-12-31', test_start: str = '2015-01-01', test_end: str = '2016-12-31') -> Dict[str, Any]:
    """Run crisis-specific tests for SOE, Private and Combined universes.

    Freezes pre-crisis weights and applies them to the crisis window.
    """
    # Helper to compute frozen weights
    def _freeze_weights(tickers: List[str]) -> Dict[str, Any]:
        price_slice = prices.reindex(columns=tickers).dropna(how='all')
        train_slice = price_slice.loc[train_start:train_end]
        valid_tickers = train_slice.dropna(axis=1).columns.tolist()
        
        if not valid_tickers:
            return {
                'weights': np.array([]), 
                'crisis_metrics': {
                    'crisis_return': np.nan, 'max_drawdown': np.nan, 
                    'volatility_spike': np.nan, 'recovery_days': None, 'allocation_drift': np.nan
                }, 
                'crisis_returns': pd.Series(dtype=float)
            }
            
        train = train_slice[valid_tickers].pct_change().dropna()
        test = price_slice.loc[test_start:test_end][valid_tickers].pct_change().dropna()
        
        # Use PortfolioBacktester to compute final pre-crisis weight exactly
        optimizer = BlackLittermanOptimizer(valid_tickers, train_start, train_end, covariance_method='ledoit')
        optimizer.prices = train_slice[valid_tickers]
        optimizer.returns = train
        optimizer.cov_matrix = optimizer._compute_covariance(train)

        # Backtester configured to produce a single rebalance at the end of training
        from legacy.core_legacy.backtester import PortfolioBacktester
        bt = PortfolioBacktester(optimizer, window_size=len(train), rebalance_freq=len(train), transaction_cost_rate=0.0)
        bt_res = bt.run_backtest(views_dict={})

        # Extract the last rebalanced BL weight (exact pre-crisis frozen weight)
        weight_df = bt_res.get('weight_history', {}).get('black_litterman', pd.DataFrame())
        if not weight_df.empty:
            # last index corresponds to the freeze date
            weights = weight_df.iloc[-1].values
        else:
            # Fallback to direct BL solve if no weight history present
            tau = 0.01 if is_high_vol_regime(train) else 0.05
            bl_ret = optimizer.apply_black_litterman({}, tau=tau, cov_matrix=optimizer.cov_matrix)
            weights = optimizer.optimize_portfolio(bl_ret)

        # Apply frozen weights to crisis returns
        crisis_returns = test.dot(weights)
        crisis_metrics = {
            'crisis_return': float(crisis_returns.sum()),
            'max_drawdown': float(_max_drawdown(crisis_returns)),
            'volatility_spike': float((crisis_returns.std() * np.sqrt(252)) / (train.std().mean() * np.sqrt(252))) if not train.empty else np.nan,
            'recovery_days': _recovery_days(crisis_returns),
            'allocation_drift': np.nan  # requires dynamic re-estimation during crisis
        }
        return {'weights': weights, 'crisis_metrics': crisis_metrics, 'crisis_returns': crisis_returns}

    soe = _freeze_weights(SOE_TICKERS)
    private = _freeze_weights(PRIVATE_TICKERS)
    combined = _freeze_weights(list(dict.fromkeys(SOE_TICKERS + PRIVATE_TICKERS)))

    # Compare
    comparison = {
        'soe': soe,
        'private': private,
        'combined': combined
    }
    return comparison


def generate_structural_summary(soe_metrics: Dict[str, Any], private_metrics: Dict[str, Any], tests: Dict[str, Any]) -> str:
    parts = []
    try:
        if soe_metrics['annualized_volatility'] < private_metrics['annualized_volatility']:
            parts.append('State backing appears to dampen volatility.')
        if private_metrics['annualized_net_return'] > soe_metrics['annualized_net_return']:
            parts.append('Private firms provide higher growth but higher instability.')
        if soe_metrics.get('asi', np.nan) < private_metrics.get('asi', np.nan):
            parts.append('SOE allocations demonstrate greater structural stability.')
        # Add test p-values
        p_vol = tests.get('vol_p_value', np.nan)
        p_asi = tests.get('asi_p_value', np.nan)
        parts.append(f"Volatility difference p-value: {p_vol:.4f}")
        parts.append(f"ASI difference p-value: {p_asi:.4f}")
    except Exception:
        parts.append('Insufficient data to generate summary.')
    return '\n'.join(parts)


def export_study_tables(summary: Dict[str, Any], filepath_base: str):
    # summary is expected to contain 'soe','private','combined' with metrics dicts
    rows = []
    for k in ['soe','private','combined']:
        m = summary.get(k, {}).get('metrics', {})
        row = {'universe': k}
        row.update(m)
        rows.append(row)
    df = pd.DataFrame(rows)
    export_csv_summary({'china_ownership_summary': df}, filepath_base + '_china_ownership_summary')
    export_excel_workbook({'summary': df}, filepath_base + '.xlsx')
    return dataframe_to_latex(df, caption='China Ownership Study Summary', label='tab:china_ownership')
