"""Focused Phase 2 comparisons using frozen Phase 1 inputs; never downloads data.

Run: python -m pipelines.phase2_experiments
Results: results/generated/phase2/ (separate from all Phase 1 evidence).
"""
from dataclasses import asdict, fields, replace
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import uuid

import numpy as np
import pandas as pd

from analysis.statistical_tests import circular_block_bootstrap_sharpe_difference
from backtesting.allocation_stability_index import compute_asi
from backtesting.paper_backtest import (BacktestConfig, run_paper_backtest,
    _buy_and_hold_daily_returns, _drifted_weights, _l1_turnover)
from core.return_calculations import compute_simple_returns
from core.validation import validate_panel, normalized_weights
from pipelines.tri_market_pipeline import MARKETS, _load_project_config, _performance, _total_costs

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/generated/phase2"
PHASE1_SHA = "598fe0d3c0a7cd7ebaf5709ae62b7c6735b92a0d"
COST_BPS = (0, 5, 10, 20)
CAPS = (1.0, 0.4)
BOOTSTRAP = {"block_size": 20, "iterations": 2000, "seed": 42}
TABLES = ("phase2_strategy_summary.csv", "phase2_concentration_sensitivity.csv",
          "phase2_transaction_cost_sensitivity.csv", "phase2_statistical_comparisons.csv")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_frozen_prices(market, spec, config):
    path = ROOT / f"results/generated/price_data/{market.lower()}_adjusted_close.csv"
    meta_path = path.with_suffix(".json")
    reference = ROOT / f"docs/phase1/{market.lower()}_adjusted_close.json"
    if not all(p.is_file() for p in (path, meta_path, reference)):
        raise FileNotFoundError(f"FROZEN_PHASE1_INPUT_UNAVAILABLE: {market}; no download substitution permitted")
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    original = json.loads(reference.read_text(encoding="utf-8"))
    if digest(path) != metadata["sha256"] or metadata["sha256"] != original["sha256"]:
        raise ValueError(f"Frozen Phase 1 checksum mismatch for {market}")
    if (metadata["price_field"] != "Adj Close (auto_adjust=False)"
            or metadata["tickers"] != spec["tickers"]
            or metadata["requested_end_exclusive"] != config["requested_end"]):
        raise ValueError(f"Frozen input definition mismatch for {market}")
    prices = pd.read_csv(path, index_col="Date", parse_dates=True)
    prices.index.name = None
    validate_panel(prices, kind="prices")
    if list(prices.columns) != spec["tickers"]:
        raise ValueError("Frozen asset order changed")
    return prices.loc[prices.index >= pd.Timestamp(config["requested_start"])], metadata


def equal_weight_path(returns, config):
    returns = validate_panel(returns)
    if len(returns) <= config.window_size:
        raise ValueError("Insufficient training history for common OOS start")
    target = pd.Series(1 / returns.shape[1], index=returns.columns)
    weights, trades, daily = [], [], []
    previous = None
    for start in range(config.window_size, len(returns), config.rebalance_freq):
        block = returns.iloc[start:start + config.rebalance_freq]
        pretrade = _drifted_weights(target, previous) if previous is not None else None
        trades.append((block.index[0], _l1_turnover(target, pretrade)))
        weights.append((block.index[0], target.to_numpy().copy()))
        daily.append(_buy_and_hold_daily_returns(block, target))
        previous = block
    return {"gross": pd.concat(daily),
            "weights": pd.DataFrame([w for _, w in weights], index=[d for d, _ in weights], columns=returns.columns),
            "turnover": pd.Series(dict(trades), dtype=float)}


def model_paths(returns, config):
    """Exactly two optimizer backtests per market; never rerun for cost-only changes."""
    paths = {}
    for cap in CAPS:
        if cap * returns.shape[1] < 1:
            raise ValueError("Predefined maximum-weight scenario is infeasible")
        matched = replace(config, max_weight=cap, transaction_cost_rate=0.0)
        packet = run_paper_backtest(returns, matched)
        for model, prefix in (("Black-Litterman", "black_litterman"), ("Markowitz", "markowitz")):
            paths[(model, cap)] = {"gross": packet["daily_returns"][prefix + "_gross"],
                                   "weights": packet["weights"][prefix],
                                   "turnover": packet["turnover"][model]}
    paths[("Equal-weight", 1.0)] = equal_weight_path(returns, config)
    expected = returns.index[config.window_size:]
    for path in paths.values():
        if not path["gross"].index.equals(expected):
            raise ValueError("Strategy OOS dates do not match")
    return paths


def apply_costs(gross, turnover, bps):
    if not np.isfinite(bps) or bps < 0 or not gross.index.is_unique or not turnover.index.is_unique:
        raise ValueError("Invalid cost rate or duplicate trade/return dates")
    if not turnover.index.isin(gross.index).all() or not np.isfinite(turnover).all() or (turnover < 0).any():
        raise ValueError("Invalid trading decisions")
    fractions = turnover * bps / 10000
    if (fractions >= 1).any():
        raise ValueError("Cost exhausts portfolio wealth")
    net = gross.copy()
    net.loc[turnover.index] = (1 + gross.loc[turnover.index]) * (1 - fractions) - 1
    return net


def concentration_metrics(weights, returns):
    """40% is a rebalance-target bound; holdings may drift above it between trades."""
    weights = normalized_weights(weights)
    live = []
    for i, (date, target) in enumerate(weights.iterrows()):
        end = weights.index[i + 1] if i + 1 < len(weights) else None
        block = returns.loc[(returns.index >= date) & ((returns.index < end) if end is not None else True)]
        holdings = (1 + block).cumprod().mul(target, axis=1)
        live.append(holdings.div(holdings.sum(axis=1), axis=0))
    live = pd.concat(live)
    return {"Maximum Target Weight": float(weights.max().max()),
            "Mean Target HHI": float(weights.pow(2).sum(axis=1).mean()),
            "Maximum End-of-Day Weight": float(live.max().max()),
            "Mean End-of-Day HHI": float(live.pow(2).sum(axis=1).mean())}


def summary_row(market, model, cap, path, returns, bps, concentration=None):
    gross, trades, weights = path["gross"], path["turnover"], path["weights"]
    net = apply_costs(gross, trades, bps)
    return {"Market": market, "Model": model, "Target Weight Cap": cap, "Cost (bps per L1)": bps,
            **_performance(net), "Gross Annualized Return": float(gross.mean() * 252),
            "Net Terminal Wealth": float((1 + net).prod()), "ASI": compute_asi(weights),
            "Average Rebalance Turnover": float(trades.iloc[1:].mean()),
            "Initial Deployment Turnover": float(trades.iloc[0]),
            "Initial Deployment Cost (bps)": float(trades.iloc[0] * bps),
            "Sum Cost Fractions": float(trades.sum() * bps / 10000),
            "Total Costs Per Initial NAV": _total_costs(net, trades, bps / 10000),
            **(concentration if concentration is not None else concentration_metrics(weights, returns))}


def statistical_row(market, cap, comparator, a, b, *, bootstrap=BOOTSTRAP):
    if not a.index.equals(b.index) or a.isna().any() or b.isna().any():
        raise ValueError("Paired bootstrap must use identical complete OOS dates")
    result = circular_block_bootstrap_sharpe_difference(a, b, **bootstrap)
    return {"Market": market, "Target Weight Cap": cap, "Cost (bps per L1)": 10,
            "Strategy A": "Black-Litterman", "Strategy B": comparator,
            "Sharpe Difference A minus B": result["observed_sharpe_difference"],
            "95% CI Lower": result["percentile_ci_95"][0], "95% CI Upper": result["percentile_ci_95"][1],
            "Two-sided P-value": result["p_value"], "P below 0.05 Unadjusted": result["p_value"] < .05,
            "Paired Observations": len(a), "OOS Start": a.index[0].date().isoformat(),
            "OOS End": a.index[-1].date().isoformat(), **bootstrap,
            "Null Centering": result["null_centering"],
            "Comparator Cap": cap if comparator == "Markowitz" else "1/N targets; feasible under 40%"}


def run_phase2(output_dir=OUT):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    marker = output_dir / "PHASE2_RUN_MANIFEST.json"
    if marker.exists():
        raise FileExistsError("Preserve the existing Phase 2 run; choose a new output directory")
    if any(output_dir.glob("*.csv")):
        raise FileExistsError("Incomplete/existing Phase 2 outputs must not be silently overwritten")
    project = _load_project_config()
    phase1 = json.loads((ROOT / "docs/phase1/RUN_MANIFEST.json").read_text(encoding="utf-8"))
    if project != phase1["configuration"]:
        raise ValueError("Phase 1 configuration changed; no silent experiment redesign permitted")
    names = {f.name: f.name for f in fields(BacktestConfig)}
    names["rebalance_freq"] = "rebalance_frequency"
    cfg = BacktestConfig(**{name: project[key] for name, key in names.items()})
    baseline, capped, cost_rows, stats, daily_rows, weight_rows, input_metadata = [], [], [], [], [], [], {}
    for market, spec in MARKETS.items():
        prices, meta = load_frozen_prices(market, spec, project)
        input_metadata[market] = meta
        returns = compute_simple_returns(prices)
        paths = model_paths(returns, cfg)
        for (model, cap), path in paths.items():
            # Target decisions and gross accounting are independent of the cost rate.
            concentration = concentration_metrics(path["weights"], returns)
            for bps in COST_BPS:
                row = summary_row(market, model, cap, path, returns, bps, concentration)
                cost_rows.append(row)
                if bps == 10:
                    if cap == 1: baseline.append(row)
                    if model != "Equal-weight": capped.append(row)
            daily = pd.DataFrame({"Gross Return": path["gross"],
                **{f"Net Return {bps}bps": apply_costs(path["gross"], path["turnover"], bps) for bps in COST_BPS}})
            daily.index.name = "Date"
            daily = daily.reset_index().assign(Market=market, Model=model, **{"Target Weight Cap":cap})
            daily_rows.append(daily)
            for date, targets in path["weights"].iterrows():
                weight_rows.append({"Date": date, "Market": market, "Model": model, "Target Weight Cap": cap,
                    "L1 Turnover": float(path["turnover"].loc[date]),
                    "Target Weights JSON": json.dumps(targets.to_dict(), sort_keys=True)})
        ew = apply_costs(paths[("Equal-weight",1.)]["gross"], paths[("Equal-weight",1.)]["turnover"],10)
        for cap in CAPS:
            bl = apply_costs(paths[("Black-Litterman",cap)]["gross"],paths[("Black-Litterman",cap)]["turnover"],10)
            mv = apply_costs(paths[("Markowitz",cap)]["gross"],paths[("Markowitz",cap)]["turnover"],10)
            stats.extend([statistical_row(market,cap,"Markowitz",bl,mv), statistical_row(market,cap,"Equal-weight",bl,ew)])
    for name, records in zip(TABLES,(baseline,capped,cost_rows,stats)):
        pd.DataFrame(records).to_csv(output_dir/name,index=False)
    pd.concat(daily_rows,ignore_index=True).to_csv(output_dir/"phase2_daily_returns.csv",index=False)
    pd.DataFrame(weight_rows).to_csv(output_dir/"phase2_trading_decisions.csv",index=False)
    manifest = {"run_id":str(uuid.uuid4()), "completed_at_utc":datetime.now(timezone.utc).isoformat(),
        "phase1_base_commit":PHASE1_SHA,
        "phase2_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        "git_dirty":bool(subprocess.check_output(["git","status","--porcelain"],cwd=ROOT,text=True).strip()),
        "source_sha256": {str(p.relative_to(ROOT)).replace('\\','/'): digest(p) for p in
            [Path(__file__), ROOT/"scripts/validate_phase2_outputs.py", ROOT/"config/project_config.yaml",ROOT/"requirements-phase1-lock.txt"]},
        "configuration":asdict(cfg), "cost_bps":COST_BPS, "target_weight_caps":CAPS,
        "bootstrap":BOOTSTRAP, "statistical_cost_bps":10,
        "frozen_phase1_inputs":input_metadata, "new_market_downloads":False,
        "definitions":{"returns":"simple daily; annual arithmetic mean x252; sample volatility x sqrt252; Sharpe RF=0",
            "turnover":"Phase 1 L1 target minus drifted pretrade weights; initial deployment 1 separately",
            "costs":"(1+r_net)=(1+r_gross)*(1-L1_turnover*bps/10000) at scheduled trades",
            "cost_expenditure":"sum pretrade net NAV x fee fraction, in units of initial NAV; distinct from terminal wealth loss",
            "equal_weight":"reset to 1/N every 63 sessions; no interim trades; OOS begins after 252 sessions",
            "cap":"rebalance target bound, not continuously enforced holding cap; matched BL/MV",
            "HHI":"sum squared weights; mean targets across rebalances and mean holdings across end-of-day observations",
            "inference":"Phase 1 approximate empirical-mean-centered paired circular bootstrap; percentile 95% intervals; no multiplicity adjustment"},
        "environment":{"python":platform.python_version(),"os":platform.platform(),
            "packages":{d.metadata['Name']:d.version for d in importlib.metadata.distributions()}},
        "output_sha256":{p.name:digest(p) for p in output_dir.glob("*.csv")}}
    marker.write_text(json.dumps(manifest,indent=2)+'\n',encoding="utf-8")
    from scripts.validate_phase2_outputs import validate_phase2
    validation = validate_phase2(output_dir)
    (output_dir/"PHASE2_OUTPUT_VALIDATION.json").write_text(json.dumps(validation,indent=2)+'\n',encoding="utf-8")
    print(pd.DataFrame(baseline).to_string(index=False))
    print(json.dumps(validation,indent=2))
    return manifest


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,default=OUT)
    run_phase2(parser.parse_args().output_dir)
