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

## Results reported in the study

| Market | Model | Return | Volatility | Sharpe | Turnover | ASI | Max Drawdown |
|---|---|---:|---:|---:|---:|---:|---:|
| US | Black-Litterman | 12.99% | 20.00% | 0.650 | 0.20% | 0.001632 | -38.04% |
| US | Markowitz | 13.24% | 21.57% | 0.614 | 1.58% | 0.015365 | -33.95% |
| China | Black-Litterman | 1.20% | 28.45% | 0.042 | 0.08% | 0.000391 | -68.07% |
| China | Markowitz | 2.64% | 30.19% | 0.088 | 1.12% | 0.010772 | -68.58% |
| India | Black-Litterman | 7.60% | 21.34% | 0.356 | 0.07% | 0.000322 | -53.67% |
| India | Markowitz | 9.76% | 22.18% | 0.440 | 0.82% | 0.007822 | -50.07% |

The main result is a large reduction in allocation instability and turnover under Black-Litterman. Return performance is mixed: Markowitz records the higher Sharpe ratio in China and India, while Black-Litterman is slightly higher in the US.

Machine-readable versions of the paper tables are available in `results/paper_results/`.

## Crisis analysis

The study also freezes pre-crisis portfolio weights and evaluates three historical stress periods:

| Crisis | BL recovery | Markowitz recovery |
|---|---:|---:|
| 2008 US Global Financial Crisis | 1093 trading days | 1056 trading days |
| 2015 China equity crash | 458 trading days | 459 trading days |
| 2020 India COVID shock | 176 trading days | 176 trading days |

The crisis results are mixed rather than uniformly favorable to either allocation method.

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
  paper_results/  tables reported in the study
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

The run creates local output files under `results/generated/`. This directory is excluded from version control so that generated runs are not mixed with the paper tables.

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
- pre-crisis weight freezing.

Run the test suite with:

```bash
python -m unittest discover -s tests -v
```

## Limitations

The study uses low-dimensional ETF baskets rather than full stock universes. Transaction costs are modeled as proportional trading frictions and do not include nonlinear market impact. Crisis windows are selected from known historical events. The public code defaults to equal-weight equilibrium weights unless a separate historical capitalization/AUM series is supplied.

The purpose of the project is to compare the behavior of the two allocation frameworks across different market environments, not to assume that either model should dominate every performance measure.
