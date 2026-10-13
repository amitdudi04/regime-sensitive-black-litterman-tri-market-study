# Published Paper Results

This directory preserves the machine-readable result tables from the previous paper release. These values are the reference for the results reported in the supplied March 2026 manuscript, *Black-Litterman vs. Markowitz: Stability, Turnover, and Crisis Dynamics Across Global Markets*.

## Files

- tri_market_summary.csv - Table 2: tri-market performance results.
- crisis_summary.csv - Table 4: crisis drawdown, volatility-spike and recovery-duration results.
- tau_sensitivity.csv - Table 8: fixed-tau Sharpe sensitivity values.

The values in these historical CSVs agree with the corresponding manuscript tables at displayed precision. This is a transcription check only; it does not prove that the current public implementation reproduces the original calculations.

Other manuscript findings (factor exposure in Table 5, SOE/private results in Table 6, regime results in Table 7, and statistical validation in Section 13) do not have matching historical CSV files in this directory. The current factor diagnostic differs from Table 5, and matching SOE/private, regime and bootstrap result artifacts were not saved by the current run. These findings are documented as paper-reported, not independently reproduced, in the results reconciliation.

## Important distinction

The historical tables are intentionally retained unchanged. The current local diagnostic run writes to results/generated/ and produces materially different performance, crisis and tau-sensitivity values. Do not copy generated values over these reference files or present them as paper results until the methodology and numerical differences are reconciled.

The unresolved differences include the equilibrium prior (market-capitalization-implied in the manuscript versus equal-weight by default in the current implementation), simple versus continuously compounded return conventions, benchmark definitions, turnover/ASI calculations, effective market sample dates and crisis outputs. See [the results reconciliation](../../docs/RESULTS_RECONCILIATION.md) for the comparison and status of each issue.

No model code or numerical output is changed by this note.
