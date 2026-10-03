# Paper-v1 Reconciliation Status

## Purpose

This document records the audit status of the public repository against the
research paper *Regime-Sensitive Black-Litterman Portfolio Allocation: A
Cross-Market Empirical Analysis of Stability, Turnover, and Crisis Resilience*.

The objective is not to force the repository to reproduce paper numbers by
hard-coding them. The objective is to make every reported result traceable from
data -> code -> machine-generated output -> figure -> paper/README.

## Published-paper reference results

The research paper reports the following primary table:

| Market | Model | Return | Volatility | Sharpe | Turnover | ASI | Max drawdown |
|---|---|---:|---:|---:|---:|---:|---:|
| US | Black-Litterman | 12.99% | 20.00% | 0.650 | 0.20% | 0.001632 | -38.04% |
| US | Markowitz | 13.24% | 21.57% | 0.614 | 1.58% | 0.015365 | -33.95% |
| China | Black-Litterman | 1.20% | 28.45% | 0.042 | 0.08% | 0.000391 | -68.07% |
| China | Markowitz | 2.64% | 30.19% | 0.088 | 1.12% | 0.010772 | -68.58% |
| India | Black-Litterman | 7.60% | 21.34% | 0.356 | 0.07% | 0.000322 | -53.67% |
| India | Markowitz | 9.76% | 22.18% | 0.440 | 0.82% | 0.007822 | -50.07% |

These values are treated as published reference values, not as automatically
validated machine outputs.

## Why reconciliation was required

The previous repository contained a separate result family in
results/v1_final_results/tri_market_summary.csv (for example US BL Sharpe 1.208
rather than 0.650). The previous run_tri_market_pipeline.py also hard-coded
several of those values and downloaded only one representative ETF per market
despite the research design describing a 5/4/4 ETF universe.

Other issues identified during the audit included:

- current modules depending on code labelled legacy/;
- model-specific optimizer treatment that could confound the BL-vs-Markowitz comparison;
- market-cap language while code approximated capitalization using price x volume;
- a mixture of log-return and simple-return conventions;
- Newey-West/HAC inference described in documentation but not implemented in the factor-regression module;
- a mock Jobson-Korkie p-value in the root statistical-tests module;
- unit-test files containing only pass;
- publication-figure code generating random realistic-looking trajectories;
- silent synthetic-price fallback in a historical stress-testing module.

## Changes on the reconciliation branch

The branch audit/paper-v1-reconciliation now:

1. removes hard-coded tri-market performance exports from the canonical runner;
2. adds a paper-v1 walk-forward backtest with a common optimizer for BL and Markowitz;
3. uses simple returns for portfolio P&L and wealth compounding;
4. rejects missing market data rather than forward-filling prices;
5. adds Newey-West/HAC factor inference with exact-date alignment;
6. removes the mock statistical-test implementation;
7. replaces empty test stubs with real tests;
8. removes random/synthetic research-figure generation;
9. writes newly computed research results to results/recomputed/ so the published-paper reference tables are not silently overwritten;
10. explicitly labels the current equilibrium prior as an equal-weight proxy unless defensible historical ETF capitalization/AUM weights are supplied.

## Important unresolved point

The paper states that the Black-Litterman equilibrium prior is derived from
market-capitalization weights. The public repository does not contain a
defensible historical market-cap/AUM weight dataset for the ETF universe.
Therefore the reconciliation implementation does not pretend that average
price x volume is market capitalization. It uses an explicit equal-weight proxy
until a justified prior-weight series is provided.

This means the branch should not yet be merged as a claim that the published
12.99% / 0.650 result family has been independently reproduced. A clean rerun
with the intended data and prior specification is required first.

## Crisis results

The existing crisis-recovery table is internally consistent with the paper's
reported recovery durations:

- US 2008: 1093 days (BL), 1056 days (Markowitz)
- China 2015: 458 days (BL), 459 days (Markowitz)
- India 2020: 176 days for both

These results should remain visible, including the fact that Black-Litterman
does not dominate every crisis metric.

## Reporting rule going forward

No result should be copied manually into the README or paper.

The source hierarchy should be:

market data -> canonical pipeline -> CSV -> figures/tables -> README/paper

If a recomputed result differs from the paper, the discrepancy must be
documented and the paper or methodology revised rather than forcing the code to
match the old value.
