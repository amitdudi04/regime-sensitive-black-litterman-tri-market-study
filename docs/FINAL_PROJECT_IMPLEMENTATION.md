# Final Project Implementation — Audit-Aligned Version

## 1. Scope

This document describes the intended empirical implementation of the project
*Regime-Sensitive Black-Litterman Portfolio Allocation: A Cross-Market Empirical
Analysis of Stability, Turnover, and Crisis Resilience*.

The implementation compares classical historical-mean Markowitz allocation with
an equilibrium-anchored Black-Litterman specification across the United States,
China and India.

## 2. Research universe

- United States: SPY, QQQ, IWM, XLF, XLK
- China: ASHR, KWEB, MCHI, FXI
- India: INDA, EPI, SMIN, INDY

The requested study interval is 2010-2025. The effective sample for each market
must be determined from the common observed price history of the ETFs actually
used; the code exports these effective dates rather than assuming that every ETF
exists for the full requested interval.

## 3. Canonical empirical sequence

1. Download observed ETF prices.
2. Restrict the market basket to common observed dates; no price forward-fill.
3. Compute simple returns for portfolio P&L.
4. Estimate Ledoit-Wolf covariance on a 252-trading-day rolling window.
5. Construct Markowitz historical expected returns.
6. Construct the Black-Litterman equilibrium prior and posterior.
7. Apply the same long-only, fully-invested optimizer to both expected-return vectors.
8. Hold weights for a 63-trading-day out-of-sample period.
9. Compute drift-adjusted turnover.
10. Apply proportional transaction cost at rebalance.
11. Export net OOS returns and weight histories.
12. Compute Sharpe, drawdown, ASI and turnover.
13. Run crisis, factor, regime, robustness and ownership analyses.
14. Generate tables and figures only from saved empirical outputs.

## 4. Black-Litterman specification

The prior is defined as:

Pi = lambda * Sigma * w_eq

and the posterior combines Pi with P, Q, Omega and tau.

The reconciliation branch implements the documented absolute-view structure
with identity P and a mild historical-return view:

Q = Pi + 0.10 * (historical_mean - Pi)

The public repository currently does not contain a defensible historical ETF
market-cap/AUM series. Therefore the reconciliation implementation uses an
explicit equal-weight equilibrium proxy unless a justified prior-weight vector
is supplied. It does not describe price x volume as market capitalization.

## 5. Fair optimizer comparison

The Black-Litterman and Markowitz portfolios must use the same objective,
covariance matrix, constraints, weight bounds and risk-aversion coefficient.
Model-specific L2 regularization is excluded from the canonical comparison
because it would confound the interpretation of allocation stability.

## 6. Allocation Stability Index

ASI is the average L1 distance between consecutive target-weight vectors:

ASI_t = sum_i |w_i,t - w_i,t-1|

Lower ASI indicates a more stable target allocation. ASI is not itself a dollar
transaction-cost measure. Turnover is computed separately from the drifted
pre-trade portfolio.

## 7. Transaction costs

The reconciliation base case uses a 10-basis-point proportional transaction-cost
rate on rebalancing turnover. The assumption is stylized and does not model
nonlinear price impact or time-varying bid-ask spreads.

The turnover convention and cost rate must be reported with every empirical
result so they cannot be mistaken for a universal implementation-cost estimate.

## 8. Crisis analysis

The study freezes pre-crisis allocations and evaluates:

- 2008 US Global Financial Crisis
- 2015 China equity crash
- 2020 India COVID shock

Recovery duration is measured in trading days from the crisis trough back to the
portfolio wealth level at crisis start V(t0).

The paper reports recovery durations of:

- US: 1093 days BL, 1056 days Markowitz
- China: 458 days BL, 459 days Markowitz
- India: 176 days for both

These results should not be described as universal Black-Litterman dominance.

## 9. Factor regression

The canonical regression is:

Rp - Rf = alpha + beta_MKT MKT + beta_SMB SMB + beta_HML HML + beta_MOM MOM + epsilon

The corrected analysis module uses Newey-West/HAC standard errors and exact-date
factor alignment. A significant factor loading is interpreted as exposure, not
as proof of a unique causal explanation for portfolio outperformance.

## 10. Regime analysis

The repository contains two distinct regime concepts:

1. an ex-ante recent-volatility rule used to condition tau; and
2. a two-state Markov-switching model used for conditional performance analysis.

These must not be described as the same mechanism. Unless filtered Markov
probabilities are explicitly fed into the portfolio decision rule, the Markov
model is an evaluation layer rather than the allocation engine.

## 11. SOE/private study

The paper's ex-ante hypothesis is that state ownership may provide downside
resilience in China. The reported paper result does not support that hypothesis
at conventional significance levels (reference p-value about 0.572).

The correct interpretation is failure to find statistically significant evidence
of superior SOE risk-adjusted performance, not proof that ownership never matters.

## 12. Published-paper reference values

The paper reports:

- US BL Sharpe 0.650 vs Markowitz 0.614
- China BL 0.042 vs Markowitz 0.088
- India BL 0.356 vs Markowitz 0.440

and substantially lower reported BL ASI and turnover across all three markets.

These values are reference outputs from the working paper. The audit identified
a separate public-repository result family and hard-coded exports. The
reconciliation branch therefore writes fresh machine-derived outputs to
results/recomputed/ and does not overwrite the reference tables until a complete
end-to-end rerun is validated.

## 13. Reproducibility policy

A result is considered reproducible only if it can be traced through:

data -> canonical pipeline -> saved CSV -> figure/table -> README/paper

Hard-coded performance tables and random illustrative trajectories are not
permitted as empirical evidence.

## 14. Unit testing

The repository now includes executable tests for:

- Black-Litterman prior/posterior behavior;
- optimizer bounds and full-investment constraints;
- rolling OOS chronology/no-look-ahead behavior;
- data-loader handling of missing prices.

Further integration tests should be added for transaction costs, crisis recovery,
factor inference and exported result schemas.

## 15. Limitations

The principal limitations remain:

- ETF proxies instead of firm-level universes;
- small cross-sectional dimensionality;
- stylized proportional transaction costs;
- dependence on public market-data availability;
- unresolved historical capitalization/AUM prior data;
- benchmark and factor-model choice;
- selected crisis windows identified ex post.

These limitations should remain visible in the research record.
