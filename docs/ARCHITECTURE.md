# Research Architecture

The executable pipeline and its diagnostics use the same ETF price histories, but the historical crisis analysis is a separate experiment. See [the methodology](METHODOLOGY.md) for exact return and weight conventions.

```text
Yahoo Finance ETF prices (record retrieval metadata and SHA-256)
    |
    +--> Common-date alignment --> Simple daily returns
             |
             +--> 252-session rolling estimation / Ledoit–Wolf covariance
             |      +--> Markowitz: historical mean expected returns
             |      +--> Black–Litterman: equilibrium prior + dated/absolute views
             |                tau chosen using trailing observed volatility
             |      +--> Shared long-only optimizer
             |      +--> 63-session buy-and-hold intervals (weights drift)
             |      +--> Initial and rebalance costs --> Net portfolio returns
             |
             +--> Performance, target-weight ASI, drift-adjusted turnover
             +--> US Kenneth French factor regression (HAC)
             +--> Ex-post Markov regime classification + paired Sharpe bootstrap
             +--> Separate 2008/2015/2020 crisis and fixed-tau diagnostics
             |
             +--> results/generated/ and dataset/run manifests
                         |
                         +--> scripts/verify_paper_results.py
                         |       Paper mismatch / incomparable benchmark report
                         +--> scripts/validate_generated_outputs.py
                                 Numerical-format and finance-invariant validation
```

## Main modules

| Location | Purpose |
|---|---|
| `core/` | Market-data download, adjusted-price handling, daily returns and shrinkage covariance |
| `models/` | Black–Litterman posterior and long-only portfolio optimization |
| `backtesting/paper_backtest.py` | Walk-forward training, dated equilibrium prior selection, buy-and-hold P&L and trading costs |
| `analysis/crisis_analysis.py` | Paper-style weighted-log diagnostic **separate from** frozen-holdings buy-and-hold crisis paths |
| `analysis/tau_sensitivity.py` | US fixed-tau scenario backtests |
| `analysis/factor_regression.py` | US daily factor regression, HAC inference and factor-data provenance |
| `analysis/regime_detection.py`, `analysis/supplementary_diagnostics.py` | Descriptive ex-post states and paired block-bootstrap Sharpe comparisons |
| `analysis/ownership_research.py` | Optional dated SOE/private stock-level analysis; original evidence not supplied |
| `pipelines/tri_market_pipeline.py` | Orchestration and output manifests |
| `scripts/verify_paper_results.py` | Explicit numerical comparisons against historical paper CSVs |
| `scripts/validate_generated_outputs.py` | Check generated table schemas and internal finance arithmetic |
| `.github/workflows/` | Synthetic tests and public-data empirical checks |

## Output provenance

`results/paper_results/` contains historical **transcriptions of the manuscript's tables**, not verified outputs of the revised pipeline. `results/generated/` contains regenerated outputs and is excluded from version control. Raw provider data snapshots are also excluded: their recorded hashes identify a particular run but do not guarantee later fresh downloads yield the same data.

For the verified October 30 snapshot and its still-unresolved differences from the manuscript, see [corrected-pipeline results](EMPIRICAL_AUDIT_2026-10-30.md).
