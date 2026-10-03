"""
Canonical cross-market execution entry point.

This runner deliberately contains no hard-coded empirical performance numbers.
Every exported metric is derived from the backtest result returned by
pipelines.dual_market.evaluate_dual_market.

During the paper-reconciliation phase outputs are written to results/recomputed/
rather than overwriting the published-paper reference tables.
"""
from pathlib import Path
import json

import pandas as pd

from pipelines.dual_market import evaluate_dual_market


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "results" / "recomputed"


def _write_factor_results(raw_results):
    rows = []
    for market, result in raw_results.items():
        factor_block = result.get("factor_regression", {})
        for key, model_name in [("bl", "Black-Litterman"), ("mw", "Markowitz")]:
            row = factor_block.get(key)
            if row:
                record = dict(row)
                record["Market"] = market
                record["Model"] = model_name
                rows.append(record)
    if rows:
        pd.DataFrame(rows).to_csv(OUT_DIR / "factor_regression_by_market.csv", index=False)


def _write_statistical_tests(statistical_tests):
    rows = []
    for market, values in statistical_tests.items():
        rows.append({
            "Market": market,
            "Circular_Block_Bootstrap_P": values.get("bootstrap_p"),
            "Jobson_Korkie_P": values.get("jobson_korkie_p"),
        })
    if rows:
        pd.DataFrame(rows).to_csv(OUT_DIR / "statistical_tests.csv", index=False)


def run():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    packet = evaluate_dual_market()
    summary = packet["summary_df"].copy()
    structural = packet["structural_df"].copy()

    summary.to_csv(OUT_DIR / "tri_market_summary.csv", index=False)
    structural.to_csv(OUT_DIR / "structural_summary.csv", index=False)
    _write_factor_results(packet["raw_results"])
    _write_statistical_tests(packet.get("statistical_tests", {}))

    manifest = {
        "status": "recomputed_not_yet_paper_certified",
        "source": "pipelines.dual_market.evaluate_dual_market",
        "hard_coded_performance_values": False,
        "note": (
            "These outputs must be reconciled against the published-paper tables "
            "before promotion to results/v1_final_results."
        ),
    }
    with open(OUT_DIR / "RUN_MANIFEST.json", "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)

    print(f"Recomputed outputs written to: {OUT_DIR}")


if __name__ == "__main__":
    run()
