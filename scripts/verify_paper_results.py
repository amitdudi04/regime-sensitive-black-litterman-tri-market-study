"""Audit generated numerical tables against immutable historical paper-reference CSVs.

This is a comparison tool, not a calibration or paper-reproduction claim.
Missing outputs, absent keys, or mismatched values never count as verified.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "results" / "paper_results"
GENERATED_DIR = ROOT / "results" / "generated"

TABLES = {
    "tri_market": {
        "paper": "tri_market_summary.csv",
        "generated": "tri_market_summary.csv",
        "keys": ("Market", "Model"),
        "fields": {
            "Annualized Return": "Annualized Return",
            "Annualized Volatility": "Annualized Volatility",
            "Sharpe Ratio": "Sharpe Ratio",
            "Turnover": "Average Rebalance Turnover",
            "ASI": "ASI",
            "Max Drawdown": "Max Drawdown",
        },
    },
    "crisis": {
        "paper": "crisis_summary.csv",
        "generated": "crisis_summary.csv",
        "keys": ("Crisis", "Market", "Model"),
        "fields": {
            "Max Drawdown": "Max Drawdown",
            "Volatility Spike": "Volatility Spike",
            "Recovery Trading Days": "Recovery Trading Days",
        },
    },
    "tau": {
        "paper": "tau_sensitivity.csv",
        "generated": "tau_sensitivity.csv",
        "keys": ("Tau",),
        "fields": {"Reported Black-Litterman Sharpe": "Sharpe Ratio"},
    },
}


def _normalize_key(item: object) -> str:
    if pd.isna(item):
        return ""
    text = str(item).casefold().replace("_", " ").replace("-", " ")
    return " ".join(text.split())


def compare_tables(
    paper_dir: Path = PAPER_DIR,
    generated_dir: Path = GENERATED_DIR,
    *,
    tolerance: float = 0.00005,
) -> pd.DataFrame:
    """Produce one row per reported numeric cell and block absent evidence."""
    if tolerance < 0 or not np.isfinite(tolerance):
        raise ValueError("tolerance must be finite and nonnegative")
    rows: list[dict[str, object]] = []
    for table, spec in TABLES.items():
        paper_path = paper_dir / spec["paper"]
        generated_path = generated_dir / spec["generated"]
        if not paper_path.is_file():
            raise FileNotFoundError(f"Historical paper reference not found: {paper_path}")
        paper = pd.read_csv(paper_path)
        generated = pd.read_csv(generated_path) if generated_path.is_file() else None
        keys = tuple(spec["keys"])
        for key in keys:
            if key not in paper:
                raise ValueError(f"{paper_path}: missing required key {key}")
        if generated is not None:
            if any(key not in generated for key in keys):
                raise ValueError(f"{generated_path}: missing required key columns")
            normalized_keys = generated.loc[:, keys].apply(lambda col: col.map(_normalize_key))
            if normalized_keys.duplicated().any():
                raise ValueError(f"{generated_path}: ambiguous duplicate comparison keys")
            generated = generated.assign(_comparison_key=list(map(tuple, normalized_keys.to_numpy())))
            generated = generated.set_index("_comparison_key", drop=False)

        for _, original in paper.iterrows():
            key = tuple(_normalize_key(original[field]) for field in keys)
            current = None
            if generated is not None and key in generated.index:
                current = generated.loc[[key]].iloc[0]
            for paper_field, generated_field in spec["fields"].items():
                value = pd.to_numeric(original.get(paper_field), errors="coerce")
                if pd.isna(value):
                    continue  # Benchmarks intentionally have no turnover/ASI.
                observed = (
                    pd.to_numeric(current.get(generated_field), errors="coerce")
                    if current is not None
                    else np.nan
                )
                delta = float(observed - value) if pd.notna(observed) else np.nan
                status = (
                    "MATCH"
                    if pd.notna(observed) and abs(delta) <= tolerance
                    else ("MISMATCH" if pd.notna(observed) else "MISSING")
                )
                rows.append({
                    "table": table,
                    "key": " | ".join(str(original[field]) for field in keys),
                    "metric": paper_field,
                    "paper_value": float(value),
                    "generated_value": float(observed) if pd.notna(observed) else np.nan,
                    "difference": delta,
                    "status": status,
                })
    return pd.DataFrame(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-dir", type=Path, default=PAPER_DIR)
    parser.add_argument("--generated-dir", type=Path, default=GENERATED_DIR)
    parser.add_argument("--tolerance", type=float, default=0.00005)
    parser.add_argument("--strict", action="store_true", help="exit nonzero unless all values match")
    args = parser.parse_args()
    report = compare_tables(args.paper_dir, args.generated_dir, tolerance=args.tolerance)
    args.generated_dir.mkdir(parents=True, exist_ok=True)
    report.to_csv(args.generated_dir / "paper_reconciliation.csv", index=False)
    counts = {str(k): int(v) for k, v in report["status"].value_counts().items()}
    complete = bool(len(report) and (report["status"] == "MATCH").all())
    summary = {
        "paper_computation_reproduced": False,
        "all_compared_cells_match": complete,
        "comparison_count": len(report),
        "status_counts": counts,
        "tolerance_absolute": args.tolerance,
        "warning": "A numeric match alone does not validate inputs, methodology, or original paper provenance.",
    }
    (args.generated_dir / "paper_reconciliation.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 1 if args.strict and not complete else 0


if __name__ == "__main__":
    raise SystemExit(main())
