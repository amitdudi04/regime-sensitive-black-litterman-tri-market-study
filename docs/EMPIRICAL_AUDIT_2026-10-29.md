# Verified GitHub Actions Empirical Audit — 29 October 2026

**Status: pipeline execution and automated comparison complete; manuscript numerical reproduction FAILED.**

- Workflow: [Empirical reproduction audit, run 40936030819](https://github.com/amitdudi04/regime-sensitive-black-litterman-tri-market-study/actions/runs/40936030819).
- Audited code snapshot: `b9867048b9c042d8f2123812592d1fb26f2b9a28`. Later source-documentation updates do not retroactively change this run.
- Source: Yahoo Finance adjusted-close ETF series via yfinance; data retrieved during the workflow on 2026-10-29.
- Data provenance: SHA-256 checksums and retrieval timestamps are in the `dataset_manifest.csv` and `RUN_MANIFEST.json` workflow artifacts. Raw provider input data are **not** archived publicly.
- Validation: the 29-test unit suite and complete tri-market/crisis/tau pipeline succeeded. A successful pipeline is **not** numerical paper replication.
- Paper comparison: **71 numeric reference cells** checked across the historical tri-market, crisis and tau CSVs; **0 match, 59 differ, 12 lack an equivalent generated row** (the historical benchmark rows differ in definition).
- Missing beyond that check: paper factor-regression Table 5, SOE/private Table 6, regime Table 7, and the historical bootstrap inference cannot be certified from the retained paper-run data. See `REVIEWER_CORRECTIONS.md`.

## 1. Newly generated main-sample outcomes

All returns and volatilities are annualized using arithmetic daily simple-return conventions, with a zero risk-free rate for the displayed Sharpe. Costs include initial deployment; trading weights drift naturally between 63-session rebalances.

| Market | Model | Return | Volatility | Sharpe | Maximum drawdown | Mean rebalance turnover (L1) | Mean ASI (L1) |
|---|---|---:|---:|---:|---:|---:|---:|
| US | BL | 15.4148% | 19.1023% | 0.806964 | -35.0693% | 2.8735% | 0.009409 |
| US | Markowitz | 15.8896% | 21.3454% | 0.744401 | -31.1532% | 80.2864% | 0.805057 |
| China | BL | 5.8193% | 28.7549% | 0.202377 | -64.2506% | 3.5751% | 0.001479 |
| China | Markowitz | 4.5275% | 30.2822% | 0.149512 | -65.2639% | 70.7290% | 0.712408 |
| India | BL | 10.8720% | 21.5867% | 0.503642 | -49.7382% | 1.7249% | 0.002346 |
| India | Markowitz | 13.2072% | 22.6253% | 0.583734 | -47.5870% | 58.3410% | 0.585258 |

These outcomes are **2026-10-29 corrected-pipeline diagnostics, not the paper's March 2026 results**.

The source-data effective OOS windows were US **2011-01-04 through 2024-12-31** (3,521 observations), China **2014-11-07 through 2024-12-31** (2,553), and India **2013-02-13 through 2024-12-31** (2,991).

The current default prior remains equal-weight. The branch supports a dated ex-ante AUM/capitalization prior, but the paper's original historical AUM series has not been recovered.

## 2. Crisis-window diagnostics

The paper-style *weighted log return* and the economically consistent *no-interim-trading buy-and-hold* wealth paths are kept as **distinct** columns. They are not interchangeable.

| Crisis | Model | Paper-style diagnostic MDD | Buy-and-hold MDD | Buy-and-hold recovery days |
|---|---|---:|---:|---:|
| 2008 US GFC | BL | -53.4674% | -52.1204% | 277 |
| 2008 US GFC | Markowitz | -46.9902% | -46.9902% | 273 |
| 2015 China crash | BL | -37.4376% | -36.9642% | 376 |
| 2015 China crash | Markowitz | -49.7631% | -49.7631% | 1,202 |
| 2020 India COVID | BL | -42.5712% | -42.5592% | 160 |
| 2020 India COVID | Markowitz | -41.6819% | -41.7125% | 161 |

Neither current convention reproduces the paper's historical crisis outcomes. Recovery is not forced to match a particular historical row.

## 3. Reconciliation and provenance

The workflow artifact contains `tri_market_summary.csv`, `crisis_summary.csv`, `tau_sensitivity.csv`, `factor_regression_us.csv`, `dataset_manifest.csv`, `RUN_MANIFEST.json`, `paper_reconciliation.csv`, `paper_reconciliation.json`, and dated-prior history files for all three markets.

**Historical paper figures remain immutable** in `results/paper_results/`. The audit branch must remain unmerged pending reconciliation. The current numerical records support a separate updated empirical study, not a retroactive proof that the original paper computations are reproducible.

### Remaining publication-level blockers

1. Exact historically dated equilibrium AUM/capitalization weights and original paper-run price snapshots remain unavailable.
2. The original paper figure labels, factor coefficients, regime and ownership test inputs, and significance calculations have not been reproduced.
3. Sample and benchmark conventions differ; comparing unlike outputs is not a mathematical defect that can be fixed by rounding.
4. Corrected methodology changes portfolio performance materially; a revised manuscript and newly validated figures/tables are required if these results replace the published claims.

**Reviewer decision: Software/diagnostic audit PASSED; exact published-paper replication NOT ESTABLISHED; publication reconciliation remains open.**
