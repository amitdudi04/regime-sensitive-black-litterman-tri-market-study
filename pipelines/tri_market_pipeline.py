import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from analysis.crisis_analysis import build_crisis_summary
from analysis.factor_regression import run_factor_regression
from analysis.supplementary_diagnostics import run_supplementary_diagnostics
from analysis.tau_sensitivity import run_tau_sensitivity
from backtesting.paper_backtest import BacktestConfig, run_paper_backtest
from core.data_loader import download_market_data
from core.return_calculations import compute_simple_returns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results" / "generated"
CONFIG_PATH = PROJECT_ROOT / "config" / "project_config.yaml"

MARKETS = {
    "US": {
        "tickers": ["SPY", "QQQ", "IWM", "XLF", "XLK"],
        "benchmark": "SPY",
        "benchmark_label": "S&P 500 ETF proxy (SPY adjusted-close total return; portfolio constituent)",
    },
    "China": {
        "tickers": ["ASHR", "KWEB", "MCHI", "FXI"],
        "benchmark": "ASHR",
        "benchmark_label": "CSI 300 ETF proxy (ASHR; also in the portfolio universe)",
    },
    "India": {
        "tickers": ["INDA", "EPI", "SMIN", "INDY"],
        "benchmark": "INDA",
        "benchmark_label": "Broad India ETF proxy (INDA adjusted-close total return; portfolio constituent)",
    },
}


def _load_project_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _load_or_download_prices(market, tickers, start, end, *, prefer_local_snapshot=True):
    """Load a verified local adjusted-price snapshot or fetch and persist a new one."""
    snapshot_dir = RESULTS_DIR / "price_data"
    snapshot_path = snapshot_dir / f"{market.lower()}_adjusted_close.csv"
    metadata_path = snapshot_dir / f"{market.lower()}_adjusted_close.json"

    if prefer_local_snapshot and snapshot_path.is_file() and metadata_path.is_file():
        with open(metadata_path, "r", encoding="utf-8") as handle:
            metadata = json.load(handle)
        same_request = (
            metadata.get("requested_start") == str(start)
            and metadata.get("requested_end_exclusive") == str(end)
            and metadata.get("tickers") == list(tickers)
        )
        if same_request:
            actual_hash = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
            if actual_hash != metadata.get("sha256"):
                raise ValueError(
                    f"Local price snapshot checksum mismatch for {market}; "
                    "remove the snapshot or reacquire the source data"
                )
            prices = pd.read_csv(snapshot_path, index_col="Date", parse_dates=True)
            if list(prices.columns) != list(tickers) or prices.empty or prices.isna().any().any():
                raise ValueError(f"Local price snapshot has an invalid schema for {market}")
            prices.index = pd.DatetimeIndex(prices.index)
            prices.index.name = None
            return prices.sort_index(), metadata

    prices = download_market_data(tickers, start, end)
    if prices.empty or list(prices.columns) != list(tickers) or prices.isna().any().any():
        raise ValueError(f"Downloaded adjusted-close price matrix is incomplete for {market}")

    snapshot_dir.mkdir(parents=True, exist_ok=True)
    prices.to_csv(snapshot_path, index_label="Date", float_format="%.12g")
    digest = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
    metadata = {
        "market": market,
        "source": "Yahoo Finance via yfinance",
        "price_field": "Adj Close, falling back to Close only if adjusted close is unavailable",
        "requested_start": str(start),
        "requested_end_exclusive": str(end),
        "tickers": list(tickers),
        "effective_start": prices.index.min().date().isoformat(),
        "effective_end": prices.index.max().date().isoformat(),
        "observations": int(len(prices)),
        "sha256": digest,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(metadata_path, "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)
    # Use the serialized snapshot for this run too, so the first run and subsequent
    # cache-backed runs calculate from exactly the same stored numeric values.
    stored_prices = pd.read_csv(snapshot_path, index_col="Date", parse_dates=True)
    stored_prices.index = pd.DatetimeIndex(stored_prices.index)
    stored_prices.index.name = None
    return stored_prices.sort_index(), metadata


def _performance(series):
    series = pd.Series(series).dropna()
    ann_return = float(series.mean() * 252.0)
    ann_vol = float(series.std(ddof=1) * np.sqrt(252.0))
    sharpe = ann_return / ann_vol if ann_vol > 0 else np.nan

    wealth = (1.0 + series).cumprod()
    drawdown = wealth / wealth.cummax() - 1.0

    return {
        "Annualized Return": ann_return,
        "Annualized Volatility": ann_vol,
        "Sharpe Ratio": sharpe,
        "Max Drawdown": float(drawdown.min()),
        "Metric Sample Start": series.index.min().date().isoformat(),
        "Metric Sample End": series.index.max().date().isoformat(),
        "Metric Observations": int(len(series)),
    }


def _asi(weights):
    if weights is None or len(weights) < 2:
        return np.nan
    return float(weights.diff().abs().sum(axis=1, min_count=1).dropna().mean())


def _benchmark_returns(ticker, start, end, target_index):
    """Return a benchmark series when its provider data are available.

    Benchmark failure is recorded in the run manifest instead of crashing after
    strategy outputs have already been written. An empty series is never presented
    as a benchmark result.
    """
    try:
        prices = download_market_data([ticker], start, end)
        if prices.empty or prices.shape[1] == 0:
            return pd.Series(dtype=float, name=str(ticker))
        returns_frame = compute_simple_returns(prices)
        if returns_frame.empty or returns_frame.shape[1] == 0:
            return pd.Series(dtype=float, name=str(ticker))
        returns = returns_frame.iloc[:, 0].rename(str(ticker))
        return returns.reindex(target_index).dropna()
    except (RuntimeError, ValueError, KeyError, IndexError):
        return pd.Series(dtype=float, name=str(ticker))


def _aligned_benchmark_series(market_returns, ticker, start, end, target_index):
    """Use an adjusted-close portfolio constituent when possible; otherwise fetch a benchmark."""
    if ticker in market_returns.columns:
        result = market_returns[ticker].reindex(target_index).dropna()
        result.name = str(ticker)
        return result
    return _benchmark_returns(ticker, start, end, target_index)


def run_tri_market_study():
    project_cfg = _load_project_config()
    requested_start = str(project_cfg["requested_start"])
    requested_end = str(project_cfg["requested_end"])
    crisis_data_start = str(project_cfg.get("crisis_data_start", "2005-01-01"))
    prefer_local_price_snapshot = bool(project_cfg.get("prefer_local_price_snapshot", True))
    tau_values = project_cfg.get("tau_sensitivity_values", [0.01, 0.05, 0.10, 0.15, 0.20])

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    cfg = BacktestConfig(
        window_size=int(project_cfg["window_size"]),
        rebalance_freq=int(project_cfg["rebalance_frequency"]),
        risk_aversion=float(project_cfg["risk_aversion"]),
        tau_low_vol=float(project_cfg["tau_low_vol"]),
        tau_high_vol=float(project_cfg["tau_high_vol"]),
        transaction_cost_rate=float(project_cfg["transaction_cost_rate"]),
        view_blend=float(project_cfg["view_blend"]),
        view_uncertainty_scale=float(project_cfg["view_uncertainty_scale"]),
        min_weight=float(project_cfg["min_weight"]),
        max_weight=float(project_cfg["max_weight"]),
    )

    summary_rows = []
    manifest_rows = []
    factor_rows = []
    crisis_summary_rows = []
    regime_rows = []
    bootstrap_rows = []
    tau_sensitivity = pd.DataFrame()
    price_snapshot_metadata = {}

    for market, spec in MARKETS.items():
        # Fetch once and preserve the exact adjusted-close input matrix locally.
        # Subsequent runs reuse the snapshot unless the request/configuration changes.
        crisis_prices, snapshot_metadata = _load_or_download_prices(
            market,
            spec["tickers"],
            crisis_data_start,
            requested_end,
            prefer_local_snapshot=prefer_local_price_snapshot,
        )
        price_snapshot_metadata[market] = snapshot_metadata
        prices = crisis_prices.loc[
            crisis_prices.index >= pd.Timestamp(requested_start)
        ].copy()
        if prices.empty:
            raise ValueError(f"No main-sample prices are available for market {market}")
        returns = compute_simple_returns(prices)

        packet = run_paper_backtest(returns, cfg)
        daily = packet["daily_returns"]

        market_dir = RESULTS_DIR / market.lower()
        market_dir.mkdir(parents=True, exist_ok=True)

        daily.to_csv(market_dir / "daily_oos_returns.csv")
        packet["weights"]["black_litterman"].to_csv(
            market_dir / "weights_black_litterman.csv"
        )
        packet["weights"]["markowitz"].to_csv(
            market_dir / "weights_markowitz.csv"
        )
        packet["turnover"].to_csv(market_dir / "turnover.csv")
        packet["tau"].to_csv(market_dir / "tau_timeline.csv")
        packet["equilibrium_prior_history"].to_csv(
            market_dir / "equilibrium_prior_history.csv"
        )
        packet["convergence"].to_csv(market_dir / "optimizer_convergence.csv")

        if market == "US":
            tau_sensitivity = run_tau_sensitivity(
                returns,
                cfg,
                tau_values,
                market=market,
            )
            tau_sensitivity.to_csv(RESULTS_DIR / "tau_sensitivity.csv", index=False)

        for model, col in [
            ("Black-Litterman", "black_litterman_net"),
            ("Markowitz", "markowitz_net"),
        ]:
            metrics = _performance(daily[col])
            weight_key = (
                "black_litterman" if model == "Black-Litterman" else "markowitz"
            )
            weights = packet["weights"][weight_key]
            average_rebalance_turnover = float(
                packet["turnover"][model].iloc[1:].mean()
                if len(packet["turnover"]) > 1
                else np.nan
            )
            initial_deployment_turnover = float(packet["turnover"][model].iloc[0])
            initial_deployment_cost_bps = (
                initial_deployment_turnover * cfg.transaction_cost_rate * 10000.0
            )

            summary_rows.append(
                {
                    "Market": market,
                    "Model": model,
                    **metrics,
                    "Average Rebalance Turnover": average_rebalance_turnover,
                    "Initial Deployment Turnover": initial_deployment_turnover,
                    "Initial Deployment Cost (bps)": initial_deployment_cost_bps,
                    "ASI": _asi(weights),
                }
            )

            # The Kenneth French data used here are US factors, so this regression
            # is limited to the US portfolio.
            if market == "US":
                try:
                    factor = run_factor_regression(daily[col], model)
                    factor["Market"] = market
                    factor_rows.append(factor)
                except Exception as exc:
                    factor_rows.append(
                        {
                            "Market": market,
                            "Model": model,
                            "Factor_Regression_Error": str(exc),
                        }
                    )

        benchmark = _aligned_benchmark_series(
            returns,
            spec["benchmark"],
            requested_start,
            requested_end,
            daily.index,
        )
        if not benchmark.empty:
            summary_rows.append(
                {
                    "Market": market,
                    "Model": f"Benchmark: {spec.get('benchmark_label', spec['benchmark'])}",
                    **_performance(benchmark),
                    "Average Rebalance Turnover": np.nan,
                    "Initial Deployment Turnover": np.nan,
                    "Initial Deployment Cost (bps)": np.nan,
                    "ASI": np.nan,
                }
            )

        # Ex-post regime and paired bootstrap outputs use exactly aligned main-OOS
        # benchmark and net strategy dates. They are NEW diagnostics, not paper results.
        supplemental_regime, state_dates, supplemental_bootstrap = run_supplementary_diagnostics(
            market,
            benchmark,
            daily["black_litterman_net"],
            daily["markowitz_net"],
        )
        regime_rows.extend(supplemental_regime.to_dict(orient="records"))
        bootstrap_rows.extend(supplemental_bootstrap.to_dict(orient="records"))
        state_dates.to_csv(market_dir / "regime_probabilities_expost.csv")

        # Crisis results use a separate historical sample so the 2008 US event is
        # not silently mixed into the main 2010–2024 out-of-sample window.
        crisis_returns = compute_simple_returns(crisis_prices)
        crisis_packet = run_paper_backtest(crisis_returns, cfg)
        crisis_asset_returns = crisis_returns.reindex(
            crisis_packet["daily_returns"].index
        )
        crisis_weights = crisis_packet["weights"]
        crisis_summary = build_crisis_summary(
            market,
            crisis_asset_returns,
            crisis_weights,
        )
        crisis_summary_rows.extend(crisis_summary.to_dict(orient="records"))

        manifest_rows.append(
            {
                "Market": market,
                "Tickers": ",".join(spec["tickers"]),
                "Requested Start": requested_start,
                "Requested End (Exclusive)": requested_end,
                "Effective Price Start": prices.index.min().date().isoformat(),
                "Effective Price End": prices.index.max().date().isoformat(),
                "Price Observations": int(len(prices)),
                "OOS Start": daily.index.min().date().isoformat(),
                "OOS End": daily.index.max().date().isoformat(),
                "OOS Observations": int(len(daily)),
                "Initial Deployment Turnover": float(
                    packet["turnover"]["Black-Litterman"].iloc[0]
                ),
                "Initial Deployment Cost (bps)": float(
                    packet["turnover"]["Black-Litterman"].iloc[0]
                    * cfg.transaction_cost_rate
                    * 10000.0
                ),
                "Crisis Requested Start": crisis_data_start,
                "Crisis Effective Price Start": crisis_prices.index.min().date().isoformat(),
                "Crisis Effective Price End": crisis_prices.index.max().date().isoformat(),
                "Crisis OOS Start": crisis_packet["daily_returns"].index.min().date().isoformat(),
                "Crisis OOS End": crisis_packet["daily_returns"].index.max().date().isoformat(),
                "Crisis OOS Observations": int(len(crisis_packet["daily_returns"])),
                "Benchmark Ticker": spec["benchmark"],
                "Benchmark Label": spec.get("benchmark_label", spec["benchmark"]),
                "Benchmark Available": bool(not benchmark.empty),
                "Benchmark Observations": int(len(benchmark)),
                "Benchmark Effective Start": (
                    benchmark.index.min().date().isoformat() if not benchmark.empty else None
                ),
                "Benchmark Effective End": (
                    benchmark.index.max().date().isoformat() if not benchmark.empty else None
                ),
                "Equilibrium Weight Method": packet["equilibrium_weight_method"],
                "Price Snapshot Path": f"results/generated/price_data/{market.lower()}_adjusted_close.csv",
                "Price Snapshot SHA256": snapshot_metadata["sha256"],
                "Price Data Source": snapshot_metadata["source"],
                "Price Snapshot Timestamp UTC": snapshot_metadata["downloaded_at_utc"],
            }
        )

    summary = pd.DataFrame(summary_rows)
    manifest = pd.DataFrame(manifest_rows)
    factors = pd.DataFrame(factor_rows)

    crisis_summary = pd.DataFrame(crisis_summary_rows)
    if tau_sensitivity.empty:
        raise RuntimeError("US tau-sensitivity output was not generated")

    summary.to_csv(RESULTS_DIR / "tri_market_summary.csv", index=False)
    manifest.to_csv(RESULTS_DIR / "dataset_manifest.csv", index=False)
    factors.to_csv(RESULTS_DIR / "factor_regression_us.csv", index=False)
    crisis_summary.to_csv(RESULTS_DIR / "crisis_summary.csv", index=False)
    tau_sensitivity.to_csv(RESULTS_DIR / "tau_sensitivity.csv", index=False)
    pd.DataFrame(regime_rows).to_csv(RESULTS_DIR / "regime_performance_expost.csv", index=False)
    pd.DataFrame(bootstrap_rows).to_csv(RESULTS_DIR / "bootstrap_sharpe_differences.csv", index=False)

    run_manifest = {
        "requested_sample_start": requested_start,
        "requested_sample_end_exclusive": requested_end,
        "crisis_sample_start_requested": crisis_data_start,
        "price_snapshot_policy": (
            "prefer local verified snapshot; set prefer_local_price_snapshot=false or remove "
            "results/generated/price_data to refresh provider data"
        ),
        "price_snapshots": {
            market: {
                "path": f"results/generated/price_data/{market.lower()}_adjusted_close.csv",
                "sha256": metadata["sha256"],
                "source": metadata["source"],
                "downloaded_at_utc": metadata["downloaded_at_utc"],
                "effective_start": metadata["effective_start"],
                "effective_end": metadata["effective_end"],
                "observations": metadata["observations"],
            }
            for market, metadata in price_snapshot_metadata.items()
        },
        "window_size": cfg.window_size,
        "rebalance_frequency": cfg.rebalance_freq,
        "transaction_cost_rate": cfg.transaction_cost_rate,
        "initial_deployment_policy": (
            "portfolio starts from cash; charge L1 purchased weight on first OOS day"
        ),
        "turnover_convention": (
            "L1 traded-weight sum; rebalance turnover is drift-adjusted target change; "
            "initial cash deployment is reported separately"
        ),
        "return_convention": (
            "adjusted-close simple total returns; arithmetic annualization; Sharpe assumes zero RF"
        ),
        "benchmark_return_convention": (
            "adjusted-close ETF proxy total returns; benchmark ETFs are constituents of each "
            "optimized universe, so comparisons are passive ETF proxies rather than independent indices"
        ),
        "view_method": "Q = Pi + 0.10 * (historical_mean - Pi)",
        "equilibrium_weight_default": project_cfg["equilibrium_weight_default"],
        "benchmark_definitions": {
            market: {
                "ticker": spec["benchmark"],
                "label": spec.get("benchmark_label", spec["benchmark"]),
            }
            for market, spec in MARKETS.items()
        },
        "tau_sensitivity_values": [float(value) for value in tau_values],
        "tau_sensitivity_sample": "same main-sample US returns, fixed tau, net portfolio returns",
        "crisis_metric_conventions": {
            "frozen_weights": "last target weights strictly before crisis start",
            "crisis_return_convention": "weighted daily log returns derived from adjusted-close simple asset returns",
            "max_drawdown": "crisis-window wealth path normalized to V(t0)=1.0",
            "volatility_spike": "crisis-window daily portfolio log-return volatility divided by up to prior 252 trading days; actual baseline count is recorded",
            "recovery_target": "wealth returns to 1.0, the value at the start of the crisis",
            "recovery_duration": "trading-index positions from crisis trough to first recovery",
            "recovery_path": "pre-crisis target weights remain frozen from crisis start through recovery",
        },
        "factor_scope": "US only; Kenneth French US daily factors",
        "supplementary_evidence": {
            "regime": "Markov 2-state smoothed probabilities ex-post, not a trading signal",
            "bootstrap": "paired circular block bootstrap of net Sharpe difference, separate from paper statistics",
            "ownership": "not computed: lacks dated SOE/private classifications and source-level constituents",
            "original_paper_reproduced": False,
        }
    }
    with open(RESULTS_DIR / "RUN_MANIFEST.json", "w", encoding="utf-8") as handle:
        json.dump(run_manifest, handle, indent=2)

    return {
        "summary": summary,
        "manifest": manifest,
        "factors": factors,
        "crisis_summary": crisis_summary,
        "tau_sensitivity": tau_sensitivity,
        "regime_performance_expost": pd.DataFrame(regime_rows),
        "bootstrap_sharpe_differences": pd.DataFrame(bootstrap_rows),
    }


if __name__ == "__main__":
    run_tri_market_study()
