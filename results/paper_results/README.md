# Paper Results

This directory contains the machine-readable tables used in the previous paper release. They are retained for traceability and are **not validated outputs of the corrected pipeline**.

The full pipeline writes new outputs to `results/generated/` without overwriting these historical files:

- `tri_market_summary.csv` — strategies and benchmarks, with average rebalancing turnover and initial deployment cost reported separately.
- `dataset_manifest.csv` — requested/effective dates and observation counts for the main and crisis samples.
- `factor_regression_us.csv` — US factor-regression results.
- `crisis_summary.csv` — reproducibly generated crisis drawdown, volatility-spike and recovery metrics.
- `tau_sensitivity.csv` — fixed-tau sensitivity using the same US main-sample OOS window.
- `RUN_MANIFEST.json` — return, cost, prior, date-window, metric conventions, and local price-snapshot hashes.

The raw price data are not distributed in Git. The pipeline was run locally on 2026-10-13 after reacquiring provider data, but the generated strategy and crisis results differ materially from the historical paper tables. Keep these files unchanged for traceability. Do not copy generated values into the manuscript until the optimizer/turnover discrepancy, crisis recovery definition, and benchmark conventions are reconciled. See `docs/RESULTS_RECONCILIATION.md`. The configured main-sample end date is exclusive: `2025-01-01` means the final possible calendar date is `2024-12-31`.
