from pathlib import Path
import json

import numpy as np
import pandas as pd
import yaml

from analysis.factor_regression import run_factor_regression
from backtesting.paper_backtest import BacktestConfig, run_paper_backtest
from core.data_loader import download_market_data
from core.return_calculations import compute_simple_returns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results" / "recomputed"
CONFIG_PATH = PROJECT_ROOT / "config" / "project_config.yaml"

MARKETS = {
    "US": {
        "tickers": ["SPY", "QQQ", "IWM", "XLF", "XLK"],
        "benchmark": "^GSPC",
    },
    "China": {
        "tickers": ["ASHR", "KWEB", "MCHI", "FXI"],
        "benchmark": "000300.SS",
    },
    "India": {
        "tickers": ["INDA", "EPI", "SMIN", "INDY"],
        "benchmark": "^BSESN",
    },
}


def _load_project_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
        cfg = yaml.safe_load(handle)
    return cfg


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
    }


def _asi(weights):
    if weights is None or len(weights) < 2:
        return np.nan
    return float(weights.diff().abs().sum(axis=1).dropna().mean())


def _benchmark_returns(ticker, start, end, target_index):
    prices = download_market_data([ticker], start, end)
    returns = compute_simple_returns(prices).iloc[:, 0]
    return returns.reindex(target_index).dropna()


def run_paper_v1_study():
    project_cfg = _load_project_config()
    requested_start = str(project_cfg["requested_start"])
    requested_end = str(project_cfg["requested_end"])

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

    for market, spec in MARKETS.items():
        prices = download_market_data(spec["tickers"], requested_start, requested_end)
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
        packet["convergence"].to_csv(market_dir / "optimizer_convergence.csv")

        for model, col in [
            ("Black-Litterman", "black_litterman_net"),
            ("Markowitz", "markowitz_net"),
        ]:
            metrics = _performance(daily[col])
            weight_key = "black_litterman" if model == "Black-Litterman" else "markowitz"
            weights = packet["weights"][weight_key]
            average_turnover = float(
                packet["turnover"][model].iloc[1:].mean()
                if len(packet["turnover"]) > 1
                else 0.0
            )
            summary_rows.append(
                {
                    "Market": market,
                    "Model": model,
                    **metrics,
                    "Average Turnover": average_turnover,
                    "ASI": _asi(weights),
                }
            )

            # Kenneth French daily factors used here are US factors. Applying
            # them silently to China/India would not be a defensible local-factor
            # specification, so the canonical runner limits this regression to US.
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

        benchmark = _benchmark_returns(
            spec["benchmark"], requested_start, requested_end, daily.index
        )
        if not benchmark.empty:
            benchmark_metrics = _performance(benchmark)
            summary_rows.append(
                {
                    "Market": market,
                    "Model": f"Benchmark ({spec['benchmark']})",
                    **benchmark_metrics,
                    "Average Turnover": np.nan,
                    "ASI": np.nan,
                }
            )

        manifest_rows.append(
            {
                "Market": market,
                "Tickers": ",".join(spec["tickers"]),
                "Requested Start": requested_start,
                "Requested End": requested_end,
                "Effective Price Start": prices.index.min().date().isoformat(),
                "Effective Price End": prices.index.max().date().isoformat(),
                "Price Observations": int(len(prices)),
                "OOS Start": daily.index.min().date().isoformat(),
                "OOS End": daily.index.max().date().isoformat(),
                "OOS Observations": int(len(daily)),
                "Equilibrium Weight Method": packet["equilibrium_weight_method"],
            }
        )

    summary = pd.DataFrame(summary_rows)
    manifest = pd.DataFrame(manifest_rows)
    factors = pd.DataFrame(factor_rows)

    summary.to_csv(RESULTS_DIR / "tri_market_summary.csv", index=False)
    manifest.to_csv(RESULTS_DIR / "dataset_manifest.csv", index=False)
    factors.to_csv(RESULTS_DIR / "factor_regression_us.csv", index=False)

    run_manifest = {
        "status": "recomputed_not_yet_paper_certified",
        "requested_sample": [requested_start, requested_end],
        "window_size": cfg.window_size,
        "rebalance_frequency": cfg.rebalance_freq,
        "transaction_cost_rate": cfg.transaction_cost_rate,
        "view_method": "Q = Pi + 0.10 * (historical_mean - Pi)",
        "equilibrium_weight_default": project_cfg["equilibrium_weight_default"],
        "return_convention": "simple returns for portfolio P&L",
        "factor_scope": "US only; Kenneth French US daily factors",
        "note": (
            "The published paper states a market-capitalization prior. The current "
            "public repository does not contain defensible historical market-cap/AUM "
            "weights for the ETF baskets, so this reconciliation run uses an explicit "
            "equal-weight equilibrium proxy until such weights are supplied."
        ),
    }
    with open(RESULTS_DIR / "RUN_MANIFEST.json", "w", encoding="utf-8") as handle:
        json.dump(run_manifest, handle, indent=2)

    return {
        "summary": summary,
        "manifest": manifest,
        "factors": factors,
    }


if __name__ == "__main__":
    run_paper_v1_study()
