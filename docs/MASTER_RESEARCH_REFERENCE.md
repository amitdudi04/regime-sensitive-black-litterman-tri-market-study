# Master Research Reference — Audit-Aligned Version

## 1. Research objective

The project evaluates whether Black-Litterman equilibrium anchoring can reduce the allocation instability associated with historical-mean Markowitz optimization without assuming that Black-Litterman must outperform on every return metric.

The intended empirical scope covers US, Chinese and Indian ETF baskets, with separate discussion of stability, turnover, crisis behavior, factor exposure, ownership structure and volatility regimes.

## 2. Hypotheses

- **H1 — Risk-adjusted performance:** Black-Litterman may improve risk-adjusted performance under estimation uncertainty.
- **H2 — Allocation stability:** Black-Litterman should reduce target-weight instability relative to historical-mean Markowitz allocation.
- **H3 — Implementation friction:** lower allocation drift and turnover should reduce proportional transaction-cost drag.
- **H4 — SOE stability:** Chinese state-owned exposure may provide greater downside resilience than private-sector exposure.

H4 is an ex-ante hypothesis. The paper's reported evidence does not support it at conventional significance levels.

## 3. Dataset

Intended ETF baskets:

- US: SPY, QQQ, IWM, XLF, XLK
- China: ASHR, KWEB, MCHI, FXI
- India: INDA, EPI, SMIN, INDY

The requested interval is 2010-2025. Effective market-specific dates depend on common observed ETF histories and must be read from the recomputed dataset manifest.

## 4. Estimation design

The canonical study uses a 252-trading-day rolling estimation window and 63-trading-day holding/rebalance interval.

Ledoit-Wolf covariance shrinkage is applied inside each training window.

Both Markowitz and Black-Litterman portfolios are long-only and fully invested and use the same optimizer and risk model. The intended difference is the expected-return construction.

## 5. Black-Litterman model

Equilibrium returns are:

Pi = lambda × Sigma × w_eq

The cleaned code uses identity P and the mild historical view:

Q = Pi + 0.10 × (historical_mean - Pi)

The working paper describes a capitalization-weighted prior. The public repository does not contain a defensible historical ETF market-cap/AUM series, so the canonical implementation uses an explicit equal-weight proxy unless such data are supplied.

## 6. Published-paper performance reference

| Market | BL Sharpe | Markowitz Sharpe | BL Turnover | Markowitz Turnover | BL ASI | Markowitz ASI |
|---|---:|---:|---:|---:|---:|---:|
| US | 0.650 | 0.614 | 0.20% | 1.58% | 0.001632 | 0.015365 |
| China | 0.042 | 0.088 | 0.08% | 1.12% | 0.000391 | 0.010772 |
| India | 0.356 | 0.440 | 0.07% | 0.82% | 0.000322 | 0.007822 |

These values are reported in the working paper. They are not presented as fresh outputs from the cleaned pipeline.

The paper therefore supports a stability interpretation more strongly than universal return superiority.

## 7. Allocation Stability Index

ASI is mean L1 target-weight drift:

ASI_t = sum_i |w_i,t - w_i,t-1|

It is distinct from trading turnover, which should account for drift before each rebalance.

The paper reference results show lower BL ASI in the three evaluated markets. This is sample-specific evidence, not universal mathematical dominance.

## 8. Crisis results

Paper-reference recovery durations:

- US 2008: BL 1093, Markowitz 1056 trading days
- China 2015: BL 458, Markowitz 459
- India 2020: both 176

BL does not dominate every crisis statistic.

The current canonical runner does not yet claim an independent recomputation of these crisis values.

## 9. Factor interpretation

The cleaned factor module uses Kenneth French US MKT, SMB, HML and MOM factors with HAC/Newey-West inference.

The canonical runner applies this only to the US portfolio. China and India require a separately justified factor specification.

A significant momentum loading is described as consistent with momentum exposure, not proof that momentum uniquely caused all observed outperformance.

## 10. Ownership result

The paper-reference p-value near 0.572 does not support statistically significant SOE-vs-private risk-adjusted performance differences.

The correct phrasing is **H4 not supported**, not proof of no ownership effect.

## 11. Regime analysis

An ex-ante rolling-volatility rule conditions tau in the allocation code.

A separate Markov-switching helper provides ex-post smoothed regime classification. Smoothed regime probabilities are not described as an ex-ante trading signal.

## 12. Tau sensitivity

The working paper reports a narrow Sharpe range as tau varies. A later stale repository table reported an identical Sharpe for every tau value and has been removed from main.

Tau sensitivity remains a paper-reference result until it is regenerated from the cleaned parameterization.

## 13. Research interpretation

The strongest defensible contribution is the empirical examination of how equilibrium anchoring changes allocation stability and implementation characteristics across heterogeneous markets.

Negative and mixed results are part of the evidence.

## 14. Reproducibility status

The research-facing main branch removes hard-coded primary performance exports, mock statistical outputs, synthetic publication trajectories, stale result families, legacy market-cap proxies and other noncanonical execution paths.

Fresh results belong in results/recomputed/. Published values remain clearly labelled under results/reference/ until a complete rerun is reconciled.
