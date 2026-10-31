"""Quantitative sanity check for the historical manuscript's reference tables.

This checks numerical implications of *reported* arithmetic returns, turnover
and Sharpe. It does not alter the manuscript or infer missing raw data.

The turnover cost calculation is conditional: 63-session rebalancing and turnover
as an L1 fraction of portfolio NAV at each rebalance. If the manuscript used a
different turnover frequency or unit, that definition must be supplied to
reconcile the published claim.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def audit(
    paper_file: Path,
    generated_file: Path | None = None,
    *,
    cost_rate: float = 0.001,
    trading_days: int = 252,
    rebalance_sessions: int = 63,
    figure_sessions: int = 3500,
) -> tuple[pd.DataFrame, dict]:
    paper = pd.read_csv(paper_file)
    required = [
        "Market", "Model", "Annualized Return", "Annualized Volatility",
        "Sharpe Ratio", "Turnover", "ASI", "Max Drawdown",
    ]
    if any(col not in paper for col in required):
        raise ValueError("Historical performance reference is missing required fields")
    if paper.duplicated(["Market", "Model"]).any():
        raise ValueError("Ambiguous duplicate historical performance rows")
    if cost_rate < 0 or trading_days <= 0 or rebalance_sessions <= 0 or figure_sessions <= 0:
        raise ValueError("Invalid cost or rebalancing assumptions")
    comparison = None
    if generated_file is not None and generated_file.is_file():
        comparison = pd.read_csv(generated_file)
        comparison = comparison[comparison["Model"].isin(["Black-Litterman", "Markowitz"])]
        comparison = comparison.set_index(["Market", "Model"])
    details = []
    for _, row in paper.iterrows():
        if row["Model"] == "Benchmark":
            continue
        annual_return = float(row["Annualized Return"])
        annual_vol = float(row["Annualized Volatility"])
        displayed_sharpe = float(row["Sharpe Ratio"])
        calculated_sharpe = annual_return / annual_vol
        turnover = float(row["Turnover"])
        annual_cost_bps = turnover * cost_rate * trading_days / rebalance_sessions * 10000
        # Jensen (concavity of log): for daily simple returns r_t > -1,
        # prod(1+r_t) <= (1 + mean(r_t)) ** n.
        bound = (1 + annual_return / trading_days) ** figure_sessions
        rec = {
            "Market": row["Market"], "Model": row["Model"],
            "Paper Annualized Return": annual_return,
            "Paper Sharpe": displayed_sharpe,
            "Sharpe Implied by Paper Return and Volatility": calculated_sharpe,
            "Paper Turnover L1": turnover,
            "Conditional Annual Cost (bps)": annual_cost_bps,
            "3500-session Jensen Upper Bound on Terminal Wealth": bound,
            "Jensen Bound Assumes": "paper annual return = arithmetic mean daily simple return x 252",
            "Paper Return Convention Proven": False,
        }
        if comparison is not None and (row["Market"], row["Model"]) in comparison.index:
            observed = comparison.loc[(row["Market"], row["Model"])]
            for field in ("Annualized Return", "Annualized Volatility", "Sharpe Ratio",
                          "Max Drawdown", "ASI"):
                rec["Current " + field] = float(observed[field])
                rec["Current minus Paper " + field] = float(observed[field] - row[field])
            rec["Current Average Rebalance Turnover"] = float(
                observed["Average Rebalance Turnover"]
            )
            rec["Current minus Paper Turnover"] = float(
                observed["Average Rebalance Turnover"] - turnover
            )
        details.append(rec)
    df = pd.DataFrame(details)
    us = df[df["Market"].eq("US")].set_index("Model")
    annual_delta_bps = float(
        us.loc["Markowitz", "Conditional Annual Cost (bps)"]
        - us.loc["Black-Litterman", "Conditional Annual Cost (bps)"]
    )
    status = {
        "paper_results_edited": False,
        "historical_reproduction": "NOT_ESTABLISHED",
        "scope": "paper Table 2 arithmetic implications, not original sample reconstruction",
        "cost_per_unit_l1_turnover_bps": cost_rate * 10000,
        "assumed_rebalances_per_year": trading_days / rebalance_sessions,
        "paper_us_markowitz_conditional_annual_cost_bps": float(
            us.loc["Markowitz", "Conditional Annual Cost (bps)"]
        ),
        "paper_us_bl_conditional_annual_cost_bps": float(
            us.loc["Black-Litterman", "Conditional Annual Cost (bps)"]
        ),
        "paper_us_markowitz_minus_bl_annual_cost_bps": annual_delta_bps,
        "paper_15_to_30bps_cost_drag_is_supported_by_displayed_turnover": False,
        "paper_figure1_sharpes_us_china_india": {"US": 1.208, "China": 0.669, "India": 1.075},
        "paper_table2_bl_sharpes_us_china_india": {
            market: float(paper[(paper["Market"] == market)
                                & (paper["Model"] == "Black-Litterman")]["Sharpe Ratio"].iloc[0])
            for market in ("US", "China", "India")
        },
        "figure1_terminal_wealth_eyeballed": True,
        "figure1_cumulative_wealth_vs_table2": (
            "Figure 1's rough final wealth multiples greatly exceed the Jensen "
            "upper bounds under the stated annual-arithmetic-simple-return interpretation. "
            "Resolve source/normalization/return convention before using the figure."
        ),
        "warning": (
            "The original paper does not retain enough input metadata to establish the "
            "turnover periodicity, gross/net definitions or plotted wealth normalization. "
            "These are conditional inconsistencies, not fabricated corrected paper data."
        ),
    }
    return df, status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-file", type=Path,
                        default=ROOT / "results/paper_results/tri_market_summary.csv")
    parser.add_argument("--generated-dir", type=Path,
                        default=ROOT / "results/generated")
    args = parser.parse_args()
    details, summary = audit(
        args.paper_file,
        args.generated_dir / "tri_market_summary.csv",
    )
    args.generated_dir.mkdir(exist_ok=True, parents=True)
    details.to_csv(args.generated_dir / "paper_arithmetic_audit.csv", index=False)
    (args.generated_dir / "paper_arithmetic_audit.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
