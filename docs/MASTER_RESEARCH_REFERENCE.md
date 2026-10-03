# Master Research Reference — Audit-Aligned Version

## 1. Research objective

The project evaluates whether Black-Litterman equilibrium anchoring can reduce
the allocation instability associated with historical-mean Markowitz
optimization without assuming that Black-Litterman must outperform on every
return metric.

The study compares the methods across US, Chinese and Indian ETF baskets and
examines allocation stability, turnover, implementation cost, crisis behavior,
factor exposure, ownership structure and volatility regimes.

## 2. Hypotheses

- **H1 — Risk-adjusted performance:** Black-Litterman may improve risk-adjusted
  performance under estimation uncertainty.
- **H2 — Allocation stability:** Black-Litterman should reduce target-weight
  instability relative to historical-mean Markowitz allocation.
- **H3 — Implementation friction:** lower allocation drift and turnover should
  reduce proportional transaction-cost drag.
- **H4 — SOE stability:** Chinese state-owned exposure may provide greater
  downside resilience than private-sector exposure.

H4 is an ex-ante hypothesis. The paper's reported evidence does not support it
at conventional significance levels.

## 3. Dataset

The intended baskets are:

- US: SPY, QQQ, IWM, XLF, XLK
- China: ASHR, KWEB, MCHI, FXI
- India: INDA, EPI, SMIN, INDY

The requested interval is 2010-2025. Effective market-specific dates depend on
common observed ETF histories and must be exported by the data pipeline.

## 4. Estimation design

The canonical study uses a 252-trading-day rolling estimation window and a
63-trading-day holding/rebalance interval.

Ledoit-Wolf covariance shrinkage is applied inside each training window.

Both Markowitz and Black-Litterman portfolios are long-only and fully invested
and use the same optimizer and risk model. The intended difference is the
expected-return construction.

## 5. Black-Litterman model

Equilibrium returns are expressed as:

Pi = lambda * Sigma * w_eq

The posterior combines Pi with P, Q, Omega and tau.

The reconciliation code uses identity P and the documented mild historical
view Q = Pi + 0.10*(historical_mean - Pi).

The paper describes a capitalization-weighted prior. The public repository does
not presently contain a defensible historical ETF market-cap/AUM series, so the
audit branch uses an explicit equal-weight proxy unless such data are supplied.

## 6. Published-paper performance reference

The working paper reports:

| Market | BL Sharpe | Markowitz Sharpe | BL Turnover | Markowitz Turnover | BL ASI | Markowitz ASI |
|---|---:|---:|---:|---:|---:|---:|
| US | 0.650 | 0.614 | 0.20% | 1.58% | 0.001632 | 0.015365 |
| China | 0.042 | 0.088 | 0.08% | 1.12% | 0.000391 | 0.010772 |
| India | 0.356 | 0.440 | 0.07% | 0.82% | 0.000322 | 0.007822 |

The evidence therefore supports a stability interpretation more strongly than a
claim of universal return superiority. In the paper reference table, Markowitz
has higher Sharpe in China and India, and the US benchmark Sharpe is also
slightly above BL.

## 7. Allocation Stability Index

ASI is mean L1 target-weight drift:

ASI_t = sum_i |w_i,t - w_i,t-1|

It is useful because it isolates changes in the optimizer's desired allocation.
It is distinct from trading turnover, which should account for portfolio drift
before each rebalance.

The paper reference results show lower BL ASI in all three evaluated markets.
That finding should be stated as sample-specific evidence, not universal
mathematical dominance.

## 8. Crisis results

Paper reference recovery durations:

- US 2008: BL 1093, Markowitz 1056 trading days
- China 2015: BL 458, Markowitz 459
- India 2020: both 176

The appropriate conclusion is that systematic crisis exposure can dominate
portfolio-construction differences. BL does not dominate every crisis statistic.

## 9. Factor interpretation

The project examines MKT, SMB, HML and MOM exposures. The corrected code uses
HAC/Newey-West inference.

If Markowitz has a significant momentum loading, the defensible statement is
that its performance is **consistent with greater momentum exposure**. The
regression does not by itself prove that momentum caused all of its
emerging-market outperformance.

## 10. Ownership result

The paper reference p-value of about 0.572 does not support statistically
significant SOE-vs-private risk-adjusted performance differences. The result is
best described as **H4 not supported**, rather than proof of no ownership effect.

## 11. Regime analysis

Markov switching separates high- and low-volatility states for conditional
evaluation. An ex-ante rolling-volatility rule separately conditions tau in the
allocation code.

Unless Markov filtered probabilities are directly used in the portfolio rule,
the project should not say that the Markov model itself drives the allocation.

## 12. Tau sensitivity

The paper reports a narrow Sharpe range as tau varies. The audit found that the
public repository's later tau table did not reproduce the same values. Tau
sensitivity therefore remains a reconciliation item and must be regenerated
from the final BL parameterization before being promoted as canonical output.

## 13. Research interpretation

The strongest supported research contribution is not that Black-Litterman wins
every metric. It is the empirical examination of how equilibrium anchoring
changes allocation stability and implementation characteristics across
heterogeneous markets.

Negative and mixed results remain part of the research evidence.

## 14. Reproducibility status

The audit branch removes hard-coded primary performance exports, implements HAC
factor inference, replaces placeholder tests, removes synthetic publication
figures and creates a machine-derived results/recomputed/ path.

The published result family remains a reference table until an end-to-end run
with the intended data and equilibrium-prior specification is validated.
