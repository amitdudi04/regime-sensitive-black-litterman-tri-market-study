"""Fail-closed schema and finance-invariant audit of generated research outputs.

This checks internal calculation/format consistency, not agreement with the paper.
"""
from pathlib import Path
import argparse
import json
import re

import numpy as np
import pandas as pd


def validate_outputs(root: Path) -> dict[str, object]:
    needed = [
        "tri_market_summary.csv", "crisis_summary.csv",
        "tau_sensitivity.csv", "dataset_manifest.csv",
        "factor_regression_us.csv", "regime_performance_expost.csv",
        "bootstrap_sharpe_differences.csv", "paper_reconciliation.csv",
        "paper_reconciliation.json", "RUN_MANIFEST.json",
    ]
    absent = [name for name in needed if not (root / name).is_file()]
    if absent:
        raise ValueError(f"Required diagnostic outputs missing: {absent}")
    summary = pd.read_csv(root / "tri_market_summary.csv")
    manifest = pd.read_csv(root / "dataset_manifest.csv")
    regime = pd.read_csv(root / "regime_performance_expost.csv")
    boot = pd.read_csv(root / "bootstrap_sharpe_differences.csv")
    crisis = pd.read_csv(root / "crisis_summary.csv")
    tau = pd.read_csv(root / "tau_sensitivity.csv")
    factor = pd.read_csv(root / "factor_regression_us.csv")
    expected_markets = {"US", "China", "India"}
    strategies = summary[summary["Model"].isin(["Black-Litterman", "Markowitz"])]
    if set(strategies["Market"]) != expected_markets or len(strategies) != 6:
        raise ValueError("Expected one BL and one Markowitz result per market")
    if strategies.duplicated(["Market", "Model"]).any():
        raise ValueError("Duplicated strategy summary rows")
    if not np.isfinite(strategies[["Annualized Return", "Annualized Volatility",
                                   "Sharpe Ratio", "Max Drawdown", "ASI",
                                   "Average Rebalance Turnover"]].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite strategy metric")
    if (strategies["Annualized Volatility"] <= 0).any():
        raise ValueError("Invalid annualized volatility")
    computed_sharpe = strategies["Annualized Return"] / strategies["Annualized Volatility"]
    if not np.allclose(computed_sharpe, strategies["Sharpe Ratio"], atol=1e-7, rtol=1e-7):
        raise ValueError("Sharpe does not reconcile to reported zero-RF return and volatility")
    if ((strategies["Max Drawdown"] > 0) | (strategies["Max Drawdown"] < -1)).any():
        raise ValueError("Invalid drawdown magnitude")
    for col in ("ASI", "Average Rebalance Turnover"):
        if ((strategies[col] < 0) | (strategies[col] > 2.000001)).any():
            raise ValueError(f"{col} is outside feasible L1 weight distance")
    if (strategies["Initial Deployment Turnover"].round(8) != 1).any():
        raise ValueError("Expected full one-way initial investment from cash")
    if set(manifest["Market"]) != expected_markets:
        raise ValueError("Dataset manifest missing a market")
    for market in expected_markets:
        sample = strategies[strategies["Market"].eq(market)]
        if sample["Metric Sample Start"].nunique() != 1 or sample["Metric Sample End"].nunique() != 1:
            raise ValueError(f"BL and Markowitz have different OOS windows for {market}")
        if sample["Metric Observations"].nunique() != 1:
            raise ValueError(f"BL and Markowitz have different OOS counts for {market}")
        states = regime[regime["Market"].eq(market)]
        if len(states) != 2 or set(states["Regime"]) != {"Low_Vol", "High_Vol"}:
            raise ValueError(f"Missing or duplicated regime cells for {market}")
        if int(states["Observations"].sum()) != int(sample["Metric Observations"].iloc[0]):
            raise ValueError(f"Regime partition differs from OOS sample for {market}")
        bootstrap = boot[boot["Market"].eq(market)]
        if len(bootstrap) != 1 or int(bootstrap["Paired Observations"].iloc[0]) != int(sample["Metric Observations"].iloc[0]):
            raise ValueError(f"Bootstrap sample differs from OOS sample for {market}")
        p = float(bootstrap["Null Centered Two-sided P-value"].iloc[0])
        if not 0 <= p <= 1:
            raise ValueError(f"Invalid bootstrap p-value for {market}")
        path = root / market.lower() / "equilibrium_prior_history.csv"
        if not path.is_file() or pd.read_csv(path).empty:
            raise ValueError(f"No effective prior history for {market}")
    if set(crisis["Market"]) != expected_markets or len(crisis) != 6:
        raise ValueError("Crisis result must have two strategies for each market")
    for col in ("Max Drawdown", "Buy-Hold Max Drawdown"):
        if crisis[col].isna().any() or ((crisis[col] < -1) | (crisis[col] > 0)).any():
            raise ValueError(f"Invalid crisis {col}")
    if len(tau) != 5 or set(tau["Market"]) != {"US"} or tau["Tau"].duplicated().any():
        raise ValueError("Fixed tau output has missing or duplicate values")
    if not (tau["OOS Observations"] == int(strategies[strategies["Market"].eq("US")]["Metric Observations"].iloc[0])).all():
        raise ValueError("Tau sensitivity uses a different OOS count")
    if len(factor) != 2 or set(factor["Model"]) != {"Black-Litterman", "Markowitz"}:
        raise ValueError("US factor regression must have exactly two strategy rows")
    if "Factor Aligned SHA256" not in factor or not factor["Factor Aligned SHA256"].astype(str).map(
        lambda x: bool(re.fullmatch(r"[0-9a-f]{64}", x))
    ).all():
        raise ValueError("Missing aligned Kenneth French factor-data fingerprint")
    paper_status = json.loads((root / "paper_reconciliation.json").read_text(encoding="utf-8"))
    if paper_status.get("paper_computation_reproduced") is not False:
        raise ValueError("Paper reproduction must never be inferred from this validation")
    return {
        "internal_consistency": "PASS",
        "paper_reproduction": "NOT_ESTABLISHED",
        "markets": sorted(expected_markets),
        "strategy_rows": len(strategies),
        "crisis_rows": len(crisis),
        "tau_rows": len(tau),
        "regime_rows": len(regime),
        "bootstrap_rows": len(boot),
        "paper_comparison_cells": paper_status["comparison_count"],
        "paper_comparison_status": paper_status["status_counts"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-dir", type=Path,
                        default=Path(__file__).resolve().parents[1] / "results" / "generated")
    args = parser.parse_args()
    report = validate_outputs(args.generated_dir)
    print(json.dumps(report, indent=2))
    (args.generated_dir / "OUTPUT_VALIDATION.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
