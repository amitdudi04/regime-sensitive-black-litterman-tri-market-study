from dataclasses import dataclass

import numpy as np
import pandas as pd

from core.covariance_estimators import estimate_covariance
from models.black_litterman_model import (
    compute_black_litterman_posterior,
    compute_implied_equilibrium_returns,
)
from models.optimizer import (
    compute_black_litterman_weights,
    compute_mean_variance_weights,
)


@dataclass
class BacktestConfig:
    window_size: int = 252
    rebalance_freq: int = 63
    risk_aversion: float = 3.0
    tau_low_vol: float = 0.05
    tau_high_vol: float = 0.01
    transaction_cost_rate: float = 0.001
    view_blend: float = 0.10
    view_uncertainty_scale: float = 10.0
    min_weight: float = 0.0
    max_weight: float = 1.0


def _regime_tau(train_returns: pd.DataFrame, cfg: BacktestConfig) -> float:
    """Ex-ante volatility rule; uses training data only."""
    rolling = train_returns.rolling(60).std().dropna()
    if rolling.empty:
        return cfg.tau_low_vol
    last_vol = float(rolling.iloc[-1].mean() * np.sqrt(252))
    median_vol = float(rolling.mean(axis=1).median() * np.sqrt(252))
    return cfg.tau_high_vol if last_vol > median_vol else cfg.tau_low_vol


def _drifted_weights(previous_weights, previous_asset_returns):
    if previous_weights is None or previous_asset_returns is None:
        return None
    growth = (1.0 + previous_asset_returns).prod(axis=0)
    drifted = previous_weights * growth
    total = float(drifted.sum())
    if total <= 0 or not np.isfinite(total):
        raise RuntimeError("Cannot compute drift-adjusted pre-trade weights")
    return drifted / total


def _l1_turnover(target, pre_trade):
    if pre_trade is None:
        # Initial portfolio deployment is not counted as rebalancing turnover.
        return 0.0
    return float((target - pre_trade).abs().sum())


def run_paper_backtest(
    returns_df: pd.DataFrame,
    config: BacktestConfig | None = None,
    equilibrium_weights: pd.Series | None = None,
):
    """
    Chronological 252/63 walk-forward comparison of Markowitz and Black-Litterman.

    Both models use the same covariance estimator, optimizer, constraints and
    risk-aversion coefficient. Their primary difference is the expected-return
    vector: historical means for Markowitz versus an equilibrium-anchored
    Black-Litterman posterior.

    The BL view vector uses the documented mild historical-return tilt:
        Q = Pi + view_blend * (historical_mean - Pi)

    P is the identity matrix and Omega is diagonal with the same units as the
    annualized covariance matrix. No future observation enters a training window.
    """
    cfg = config or BacktestConfig()
    returns_df = returns_df.dropna(how="any").sort_index()

    if len(returns_df) <= cfg.window_size:
        raise ValueError("Not enough observations for the requested rolling window")

    assets = list(returns_df.columns)
    n_assets = len(assets)

    if equilibrium_weights is None:
        equilibrium_weights = pd.Series(
            np.repeat(1.0 / n_assets, n_assets), index=assets, dtype=float
        )
        equilibrium_weight_method = "equal_weight_proxy"
    else:
        equilibrium_weights = pd.Series(equilibrium_weights, index=assets, dtype=float)
        equilibrium_weights = equilibrium_weights / equilibrium_weights.sum()
        equilibrium_weight_method = "user_supplied"

    daily = {
        "black_litterman_gross": [],
        "black_litterman_net": [],
        "markowitz_gross": [],
        "markowitz_net": [],
    }
    daily_index = []

    weight_records = {"black_litterman": [], "markowitz": []}
    turnover_records = []
    tau_records = []
    convergence_records = []

    prev_weights = {"black_litterman": None, "markowitz": None}
    prev_asset_returns = None

    for start in range(cfg.window_size, len(returns_df), cfg.rebalance_freq):
        stop = min(start + cfg.rebalance_freq, len(returns_df))
        train = returns_df.iloc[start - cfg.window_size : start]
        test = returns_df.iloc[start:stop]
        if test.empty:
            break

        cov = estimate_covariance(train)
        historical_mean = train.mean() * 252.0

        tau = _regime_tau(train, cfg)
        pi = compute_implied_equilibrium_returns(
            cov, equilibrium_weights.values, cfg.risk_aversion
        )

        p = np.eye(n_assets)
        q = pi.values + cfg.view_blend * (historical_mean.values - pi.values)

        # Omega has return-variance units and is intentionally independent of tau,
        # so tau sensitivity is empirically identifiable.
        omega_diag = np.maximum(
            np.diag(cov.to_numpy()) * cfg.view_uncertainty_scale,
            1e-12,
        )
        omega = np.diag(omega_diag)

        posterior = compute_black_litterman_posterior(
            pi, cov, P=p, Q=q, Omega=omega, tau=tau
        )

        mv_weights = compute_mean_variance_weights(
            historical_mean,
            cov,
            risk_aversion=cfg.risk_aversion,
            min_weight=cfg.min_weight,
            max_weight=cfg.max_weight,
        )
        bl_weights = compute_black_litterman_weights(
            posterior,
            cov,
            lambda_risk_aversion=cfg.risk_aversion,
            min_weight=cfg.min_weight,
            max_weight=cfg.max_weight,
        )

        pre_trade_mv = _drifted_weights(prev_weights["markowitz"], prev_asset_returns)
        pre_trade_bl = _drifted_weights(prev_weights["black_litterman"], prev_asset_returns)

        mv_turnover = _l1_turnover(mv_weights, pre_trade_mv)
        bl_turnover = _l1_turnover(bl_weights, pre_trade_bl)

        mv_gross = test.dot(mv_weights)
        bl_gross = test.dot(bl_weights)
        mv_net = mv_gross.copy()
        bl_net = bl_gross.copy()

        # Charge proportional rebalancing friction once, on the first day after trade.
        if len(test):
            mv_net.iloc[0] -= mv_turnover * cfg.transaction_cost_rate
            bl_net.iloc[0] -= bl_turnover * cfg.transaction_cost_rate

        daily["markowitz_gross"].extend(mv_gross.tolist())
        daily["markowitz_net"].extend(mv_net.tolist())
        daily["black_litterman_gross"].extend(bl_gross.tolist())
        daily["black_litterman_net"].extend(bl_net.tolist())
        daily_index.extend(test.index.tolist())

        rebalance_date = test.index[0]
        weight_records["markowitz"].append((rebalance_date, mv_weights.copy()))
        weight_records["black_litterman"].append((rebalance_date, bl_weights.copy()))
        turnover_records.append(
            {
                "Date": rebalance_date,
                "Black-Litterman": bl_turnover,
                "Markowitz": mv_turnover,
            }
        )
        tau_records.append({"Date": rebalance_date, "Tau": tau})
        convergence_records.append(
            {
                "Date": rebalance_date,
                "Black-Litterman": "success",
                "Markowitz": "success",
            }
        )

        prev_weights["markowitz"] = mv_weights
        prev_weights["black_litterman"] = bl_weights
        prev_asset_returns = test.copy()

    daily_df = pd.DataFrame(daily, index=pd.DatetimeIndex(daily_index)).sort_index()

    weights = {}
    for model, rows in weight_records.items():
        if rows:
            weights[model] = pd.DataFrame(
                [series.values for _, series in rows],
                index=pd.DatetimeIndex([date for date, _ in rows]),
                columns=assets,
            )
        else:
            weights[model] = pd.DataFrame(columns=assets)

    turnover = pd.DataFrame(turnover_records).set_index("Date")
    tau_timeline = pd.DataFrame(tau_records).set_index("Date")
    convergence = pd.DataFrame(convergence_records).set_index("Date")

    return {
        "daily_returns": daily_df,
        "weights": weights,
        "turnover": turnover,
        "tau": tau_timeline,
        "convergence": convergence,
        "equilibrium_weights": equilibrium_weights,
        "equilibrium_weight_method": equilibrium_weight_method,
        "config": cfg,
    }
