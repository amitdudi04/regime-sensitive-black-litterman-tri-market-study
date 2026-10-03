# Project Implementation — Audit-Aligned Version

## 1. Scope

This document describes the cleaned empirical implementation of the project
*Regime-Sensitive Black-Litterman Portfolio Allocation: A Cross-Market Empirical Analysis of Stability, Turnover, and Crisis Resilience*.

The canonical executable comparison is between historical-mean Markowitz allocation and an equilibrium-anchored Black-Litterman specification across US, China and India ETF baskets.

## 2. Research universe

- United States: SPY, QQQ, IWM, XLF, XLK
- China: ASHR, KWEB, MCHI, FXI
- India: INDA, EPI, SMIN, INDY

The requested interval is 2010-2025. The effective sample is determined from the common observed price history of the ETFs actually available in each basket and is exported by the pipeline.

## 3. Canonical executable sequence

1. Download observed ETF prices.
2. Restrict each basket to common observed dates; do not forward-fill prices.
3. Compute simple returns for portfolio P&L.
4. Estimate Ledoit-Wolf covariance on a 252-trading-day rolling window.
5. Construct historical-mean Markowitz expected returns.
6. Construct the Black-Litterman equilibrium prior and posterior.
7. Apply the same long-only, fully-invested optimizer to both expected-return vectors.
8. Hold weights for a 63-trading-day out-of-sample interval.
9. Compute drift-adjusted turnover.
10. Apply proportional transaction cost at rebalance.
11. Export gross/net OOS returns, weight histories, tau timeline and convergence status.
12. Compute annualized return, volatility, Sharpe, max drawdown, ASI and average turnover.
13. Run the Kenneth French US four-factor regression for the US portfolio only.
14. Generate figures only from saved machine-produced outputs.

## 4. Supporting analytical modules

The repository also retains defensible helpers for:

- ex-post Markov regime classification;
- crisis-weight freezing;
- SOE/private segmentation;
- bootstrap and Sharpe-difference diagnostics.

These supporting modules are not presented as fully integrated paper-v1 recomputations unless the canonical pipeline explicitly calls them.

Paper-reported crisis, regime, tau and SOE results are preserved separately under results/reference/ until their corrected end-to-end implementations are integrated and rerun.

## 5. Black-Litterman specification

The prior is:

Pi = lambda × Sigma × w_eq

The posterior combines Pi with P, Q, Omega and tau.

The cleaned implementation uses identity P and the documented mild historical-return view:

Q = Pi + 0.10 × (historical_mean - Pi)

The public repository does not contain a defensible historical ETF market-cap/AUM series. The canonical code therefore uses an explicit equal-weight equilibrium proxy unless a justified prior-weight vector is supplied. It does not describe price × volume as market capitalization.

## 6. Fair optimizer comparison

Black-Litterman and Markowitz use the same objective, covariance matrix, constraints, weight bounds and risk-aversion coefficient.

Model-specific L2 regularization is excluded because it would confound any stability comparison.

## 7. Allocation Stability Index

ASI is the mean L1 distance between consecutive target-weight vectors:

ASI_t = sum_i |w_i,t - w_i,t-1|

Lower ASI indicates a more stable target allocation. ASI is not a dollar transaction-cost measure.

Turnover is computed separately from the drifted pre-trade portfolio.

## 8. Transaction costs

The base case uses a 10-basis-point proportional transaction-cost rate on rebalancing turnover.

This is a stylized implementation friction, not a nonlinear market-impact model.

## 9. Crisis analysis status

The working paper reports frozen-weight crisis tests for:

- 2008 US GFC
- 2015 China equity crash
- 2020 India COVID shock

The crisis reference table remains under results/reference/. The current default runner does not claim to have independently reproduced those paper values.

## 10. Factor regression

The canonical regression is:

Rp - Rf = alpha + beta_MKT MKT + beta_SMB SMB + beta_HML HML + beta_MOM MOM + epsilon

The factor module uses Kenneth French US daily factors with Newey-West/HAC inference and exact-date alignment.

Accordingly, the canonical runner limits this regression to the US portfolio. It does not silently apply US factors as local China/India factor models.

## 11. Regime analysis

Two concepts are deliberately separated:

1. an ex-ante recent-volatility rule used to condition tau; and
2. a two-state Markov-switching model used for ex-post conditional evaluation.

Smoothed Markov probabilities are not described as an ex-ante allocation signal.

## 12. SOE/private study status

The paper's ex-ante hypothesis is that state ownership may provide downside resilience.

The reported paper result does not support a statistically significant SOE-vs-private risk-adjusted performance difference at conventional levels.

Earlier mock/legacy SOE execution code was removed from the research-facing main branch. Only transparent helper functions and labelled paper-reference values remain.

## 13. Published-paper reference values

The working paper reports:

- US BL Sharpe 0.650 vs Markowitz 0.614
- China BL 0.042 vs Markowitz 0.088
- India BL 0.356 vs Markowitz 0.440

These are reference values, not automatically validated machine outputs.

The cleaned code writes fresh results to results/recomputed/.

## 14. Reproducibility policy

A result is considered reproduced only when it can be traced through:

data → canonical pipeline → saved output → figure/table → documentation

Hard-coded performance outputs and simulated research trajectories are not permitted as empirical evidence.

## 15. Unit testing

Tests cover:

- Black-Litterman prior/posterior behavior;
- optimizer constraints;
- rolling OOS chronology;
- no-look-ahead behavior under future-data perturbation;
- transaction-cost direction;
- data-loader missing-price policy.

CI verifies deterministic unit behavior. It does not replace a full external-data empirical rerun.

## 16. Limitations

- ETF proxies instead of firm-level universes;
- small cross-sectional dimensionality;
- stylized proportional transaction costs;
- public-data availability;
- unresolved historical capitalization/AUM prior data;
- benchmark and factor-model choice;
- ex-post crisis-window selection;
- supporting crisis/regime/SOE modules not yet fully reintegrated into the canonical runner.

These limitations are intentionally visible.
