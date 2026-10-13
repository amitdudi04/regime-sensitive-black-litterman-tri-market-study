# Regime-Sensitive Black-Litterman Portfolio Allocation

Empirical comparison of Black-Litterman and classical mean-variance portfolio allocation across the United States, China and India.

**Amit Kumar Dudi**

## Overview

This project examines whether Black-Litterman equilibrium anchoring can improve portfolio stability when expected returns are estimated with noise. The study compares Black-Litterman with historical-mean Markowitz allocation using rolling out-of-sample tests, transaction costs, crisis analysis and allocation-stability measures.

The analysis uses three ETF baskets:

| Market | ETFs |
|---|---|
| United States | SPY, QQQ, IWM, XLF, XLK |
| China | ASHR, KWEB, MCHI, FXI |
| India | INDA, EPI, SMIN, INDY |

The main backtest uses a **252-trading-day estimation window** and a **63-trading-day holding period**.

## Research questions

The project focuses on four questions:

- Does Black-Litterman reduce the instability of optimized portfolio weights?
- Does lower weight instability translate into lower turnover and transaction-cost drag?
- How do the two allocation methods behave during major crisis periods?
- Are differences in portfolio returns associated with systematic factor exposures or market regimes?

## Methodology

For each market, the pipeline:

1. downloads daily ETF prices;
2. aligns assets on common observed trading dates;
3. computes simple daily returns;
4. estimates covariance with Ledoit-Wolf shrinkage;
5. estimates historical expected returns for Markowitz;
6. forms Black-Litterman posterior expected returns;
7. applies the same long-only, fully-invested optimizer to both models;
8. holds the resulting weights for 63 trading days;
9. records out-of-sample returns, turnover, transaction costs and weight changes.

The Black-Litterman prior is based on

[
Pi = lambda Sigma w_{eq}
]

with absolute views defined through an identity view matrix. The public implementation uses an **equal-weight equilibrium prior by default**. Historical ETF capitalization/AUM weights are not distributed with this repository, but alternative equilibrium weights can be supplied directly to the backtest.

The view vector is

[
Q = Pi + 0.10(mu_{hist}-Pi)
]

and (	au) is conditioned using recent realized volatility.

## Allocation Stability Index

Allocation Stability Index (ASI) is the average L1 change in target weights between consecutive rebalances:

[
ASI_t = sum_i |w_{i,t}-w_{i,t-1}|
]

Lower ASI indicates a more stable target allocation. Turnover is calculated separately from drift-adjusted pre-trade weights.

## Empirical result status

The figures in `results/paper_results/` and the tables below are a **historical snapshot from the previous paper release**. Code review identified omitted initial deployment costs, missing reproducible crisis/tau generators, and an unresolved mismatch between the published numbers and the current implementation. The corrected pipeline has now been run locally, but its results differ materially from the historical tables. Keep the historical files for traceability; do not replace the manuscript's figures until the model/turnover discrepancy and benchmark definitions are reconciled.

The raw price history is not distributed in Git. A corrected pipeline run was completed locally on 2026-10-13 after reacquiring provider data. Its outputs are in the ignored `results/generated/` directory and include the actual observation windows and metric conventions. **Those outputs differ materially from the historical paper snapshot below, so the discrepancy must be resolved before any current values are cited as paper results.** The generated values are not committed as canonical research outputs. The main requested sample is `2010-01-01` through `2024-12-31`: `requested_end: 2025-01-01` is an exclusive end date. Crisis analysis uses a separate historical price sample beginning at the configured `crisis_data_start` so that the 2008 US crisis is not silently presented as part of the main 2010–2024 sample.

## Previous paper-release performance snapshot

These historical values use annualized arithmetic returns and a zero-risk-free-rate Sharpe convention. The reported turnover column describes average rebalancing turnover and excludes the initial cash-to-portfolio deployment; the corrected pipeline reports that deployment and its cost separately.

| Market | Model | Annualized arithmetic return | Volatility | Sharpe (0% RF) | Avg. rebalance turnover | ASI | Max drawdown |
|---|---|---:|---:|---:|---:|---:|---:|
| US | Black-Litterman | 12.99% | 20.00% | 0.650 | 0.20% | 0.001632 | -38.04% |
| US | Markowitz | 13.24% | 21.57% | 0.614 | 1.58% | 0.015365 | -33.95% |
| US | S&P 500 benchmark | 13.19% | 19.83% | 0.665 | — | — | -37.87% |
| China | Black-Litterman | 1.20% | 28.45% | 0.042 | 0.08% | 0.000391 | -68.07% |
| China | Markowitz | 2.64% | 30.19% | 0.088 | 1.12% | 0.010772 | -68.58% |
| China | CSI 300 benchmark | 1.20% | 28.74% | 0.042 | — | — | -68.66% |
| India | Black-Litterman | 7.60% | 21.34% | 0.356 | 0.07% | 0.000322 | -53.67% |
| India | Markowitz | 9.76% | 22.18% | 0.440 | 0.82% | 0.007822 | -50.07% |
| India | BSE Sensex benchmark | 7.54% | 21.33% | 0.353 | — | — | -53.78% |

The defensible conclusion from the historical snapshot is narrower than universal performance superiority: Black-Litterman had much lower reported target-weight instability and average rebalancing turnover, but it did **not** dominate returns or risk-adjusted performance across all markets. In the historical US table, the S&P 500 benchmark Sharpe (0.665) exceeds Black-Litterman (0.650); Markowitz has higher reported Sharpe in China and India. The corrected local run produces materially different values, so these conclusions must be re-evaluated after the discrepancy described in `docs/RESULTS_RECONCILIATION.md` is resolved.

The corrected pipeline uses adjusted-close ETF proxies—SPY for the US, ASHR for China and INDA for India—so the benchmark return series follows the same adjusted-close convention as the portfolio assets. Each benchmark ETF is also a constituent of its optimized basket, so these are passive investable-ETF comparisons rather than independent index series. The historical paper used index-style benchmarks (and its China index symbol is currently unavailable from the configured provider); historical benchmark values therefore are not directly comparable to the newly generated ETF-proxy values. The output records each metric's exact start date, end date and observation count.

## Reproducible crisis analysis

The pipeline now writes `results/generated/crisis_summary.csv`. It freezes the last target weights strictly before each crisis, evaluates every available out-of-sample trading day in the crisis window, defines initial crisis wealth as 1.0, calculates the volatility-spike ratio against up to the preceding 252 trading days, and records the actual baseline observation count. Because some ETF baskets have short listing histories, the baseline may be shorter than 252 days (the China 2015 window has only 139 available pre-crisis observations in the current run). Recovery is defined as the first return to crisis-start wealth after the trough while keeping the pre-crisis target weights frozen through the recovery date, as specified in the paper. The generated recovery durations must still be checked against the historical table because the current portfolio weights and drawdown/volatility results differ materially.

The historical paper table reported the following values. The corrected generator now follows the paper's frozen-weight-through-recovery definition, but its generated durations still differ because the current portfolio weights and data sample have not been reconciled to the historical release:

| Crisis | BL recovery | Markowitz recovery |
|---|---:|---:|
| 2008 US Global Financial Crisis | 1093 trading days | 1056 trading days |
| 2015 China equity crash | 458 trading days | 459 trading days |
| 2020 India COVID shock | 176 trading days | 176 trading days |

## Reproducible tau sensitivity

The pipeline now writes `results/generated/tau_sensitivity.csv` by rerunning the US Black-Litterman backtest at each configured fixed `tau`, setting `tau_low_vol = tau_high_vol` for each run. Every row records the same main-sample universe, out-of-sample start/end, observation count, net-return series, and zero-risk-free Sharpe convention. This replaces the previous manually reported values that lacked comparable run metadata.

## Factor and regime analysis

For the US portfolio, the project estimates MKT, SMB, HML and MOM exposures using Kenneth French daily factors with Newey-West/HAC standard errors.

A separate two-state Markov-switching model is used for ex-post high- and low-volatility analysis. The allocation rule itself uses only information available at the rebalance date.

## Repository structure

```text
core/           market-data and return utilities
models/         Black-Litterman model and portfolio optimizer
backtesting/    rolling out-of-sample backtest and crisis helpers
analysis/       factor, regime, ownership and statistical analysis
pipelines/      end-to-end tri-market research pipeline
results/
  paper_results/  historical tables from the previous paper release
scripts/        figure generation
tests/          numerical and chronology tests
docs/           methodology and pipeline documentation
```

## Running the project

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the tri-market study:

```bash
python -m pipelines.run_tri_market_pipeline
```

The run creates local output files under `results/generated/`, including strategy/benchmark metrics, date manifests, factor regressions, crisis-summary metrics, fixed-tau sensitivity, and `RUN_MANIFEST.json`. The exact adjusted-close price matrices are stored in `results/generated/price_data/` with SHA-256 hashes and source metadata; this directory is excluded from version control. With `prefer_local_price_snapshot: true`, identical requests reuse a verified local snapshot. Set it to `false` or delete the snapshot directory to refresh Yahoo Finance data. These local snapshots make a run repeatable on the same machine without publishing raw price data in Git.

To generate charts from the latest local run:

```bash
python scripts/generate_research_figures.py
```

## Testing

The repository includes tests for:

- Black-Litterman prior and posterior calculations;
- long-only and fully-invested optimizer constraints;
- rolling out-of-sample chronology;
- future-data/no-look-ahead checks;
- transaction-cost handling;
- missing-price handling;
- pre-crisis weight freezing and daily crisis-window metric calculation;
- fixed-tau sensitivity using a shared out-of-sample window;
- initial deployment transaction costs;
- robust data-download fallback that never silently shrinks the requested ETF universe.

Run the test suite with:

```bash
python -m unittest discover -s tests -v
```

## Limitations

The study uses low-dimensional ETF baskets rather than full stock universes. Transaction costs are modeled as proportional trading frictions and do not include nonlinear market impact. Crisis windows are selected from known historical events. The public code defaults to equal-weight equilibrium weights unless a separate historical capitalization/AUM series is supplied.

The purpose of the project is to compare the behavior of the two allocation frameworks across different market environments, not to assume that either model should dominate every performance measure.
