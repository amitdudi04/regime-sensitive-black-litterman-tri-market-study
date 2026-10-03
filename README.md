# Regime-Sensitive Black-Litterman Portfolio Allocation

### Cross-market stability, turnover and crisis analysis in the US, China and India

**Author:** Amit Kumar Dudi  
**Research status:** working-paper project with an active reproducibility reconciliation

## Research question

Classical mean-variance optimization is highly sensitive to expected-return
estimation error. This project studies whether an equilibrium-anchored
Black-Litterman return model can produce more stable implementable allocations
than a classical historical-mean Markowitz specification.

The empirical design compares the two approaches across:

- **United States:** SPY, QQQ, IWM, XLF, XLK
- **China:** ASHR, KWEB, MCHI, FXI
- **India:** INDA, EPI, SMIN, INDY

The analysis considers allocation stability, turnover, transaction costs,
crisis behavior, factor exposures and volatility regimes.

## Canonical research flow

Observed market data -> common-date validation -> simple returns -> 252-day
rolling estimation -> Ledoit-Wolf covariance -> Markowitz historical means and
Black-Litterman posterior -> identical long-only fully-invested optimizer ->
63-trading-day OOS holding period -> drift-adjusted turnover and proportional
trading cost -> net returns -> ASI/drawdown/Sharpe/crisis/factor/regime analysis.

## Methodological controls

- No hard-coded performance results in the canonical paper-v1 runner.
- The same optimizer and constraints are applied to Markowitz and BL.
- No silent synthetic-price fallback is permitted in the canonical empirical path.
- Missing ETF prices are not forward-filled in the canonical data loader.
- Portfolio P&L uses simple returns.
- Factor inference uses Newey-West/HAC standard errors and exact-date factor alignment.
- Research figures must be generated from saved empirical series; the figure script no longer produces random realistic-looking paths.

## Black-Litterman specification

The equilibrium return vector is Pi = lambda * Sigma * w_eq.

The posterior combines Pi with an absolute-view system P, Q and Omega. For the
reconciliation implementation:

- P is the identity matrix;
- the documented synthetic momentum view is Q = Pi + 0.10 * (historical_mean - Pi);
- Omega is diagonal and expressed in annualized return-variance units;
- tau is conditioned by an ex-ante volatility rule;
- the default equilibrium-weight vector is currently an explicit equal-weight
  proxy because the public repository does not contain a defensible historical
  ETF market-cap/AUM weight series.

The published paper describes a capitalization-weighted equilibrium prior.
That point remains under reconciliation and is not silently approximated by
price x volume.

## Allocation Stability Index

ASI_t = sum_i |w_i,t - w_i,t-1|.

The reported ASI is the mean L1 target-weight change across rebalances. It is a
model-stability metric, not a dollar transaction-cost measure. Turnover is
calculated separately from the drifted pre-trade portfolio weights.

## Published-paper reference results

The working paper reports:

| Market | Model | Return | Volatility | Sharpe | Turnover | ASI | Max Drawdown |
|---|---|---:|---:|---:|---:|---:|---:|
| US | Black-Litterman | 12.99% | 20.00% | 0.650 | 0.20% | 0.001632 | -38.04% |
| US | Markowitz | 13.24% | 21.57% | 0.614 | 1.58% | 0.015365 | -33.95% |
| China | Black-Litterman | 1.20% | 28.45% | 0.042 | 0.08% | 0.000391 | -68.07% |
| China | Markowitz | 2.64% | 30.19% | 0.088 | 1.12% | 0.010772 | -68.58% |
| India | Black-Litterman | 7.60% | 21.34% | 0.356 | 0.07% | 0.000322 | -53.67% |
| India | Markowitz | 9.76% | 22.18% | 0.440 | 0.82% | 0.007822 | -50.07% |

These are published-paper reference values. The audit found that an older
repository result family did not match this table. The corrected code therefore
writes fresh outputs to results/recomputed/ and does not claim that the
published values have been independently reproduced until the intended
data/prior specification is rerun end to end.

See docs/RECONCILIATION_STATUS.md.

## Crisis stress testing

The paper reports corrected recovery durations measured in trading days from
the crisis trough back to the crisis-start wealth level V(t0):

| Crisis | BL recovery | Markowitz recovery |
|---|---:|---:|
| US 2008 GFC | 1093 | 1056 |
| China 2015 crash | 458 | 459 |
| India 2020 COVID | 176 | 176 |

These results do not establish universal crisis dominance by Black-Litterman.
They show that recovery behavior can be similar across allocation methods when
systematic market exposure dominates.

## Factor interpretation

The study uses a four-factor regression (MKT, SMB, HML, MOM). The canonical
factor module now uses HAC/Newey-West inference.

A significant loading should be interpreted as factor exposure, not proof that
the factor caused all observed outperformance. The project therefore avoids
describing Markowitz emerging-market performance as mechanically proven to
come from momentum.

## SOE / private-company sub-study

The paper's ex-ante hypothesis is that state ownership may provide downside
resilience. The reported result does not support that hypothesis at conventional
significance levels (paper reference p-value approximately 0.572). This is a
failure to find statistically significant evidence of a difference, not proof
that ownership can never matter.

## Execution

Install dependencies with:

    pip install -r requirements.txt

Run the reconciliation study with:

    python -m pipelines.paper_v1_pipeline

or the backward-compatible entry point:

    python -m pipelines.run_tri_market_pipeline

Fresh outputs are written to results/recomputed/.

Generate figures only after a successful empirical run:

    python scripts/generate_research_figures.py

## Repository structure

- core/ — data and return utilities
- models/ — BL posterior and common optimizer
- backtesting/ — walk-forward portfolio simulation
- analysis/ — factor, regime and statistical analysis
- pipelines/ — executable empirical workflows
- results/ — published-reference and recomputed outputs
- tests/ — executable mathematical / no-look-ahead tests
- docs/ — paper, implementation and audit documentation
- legacy/ — historical implementation pending final migration

## Limitations

The study uses ETF proxies, stylized proportional transaction costs and a
relatively small cross-section. The reconciliation also identifies an important
prior-specification limitation: the public repository presently lacks the
historical ETF capitalization/AUM series needed to reproduce the paper's stated
capitalization-weighted BL equilibrium prior.

The Markov-switching model should be interpreted as a regime-evaluation layer
unless its filtered probabilities are explicitly incorporated into the
portfolio decision rule.

## Research integrity

Negative and non-dominant results are retained. In particular:

- Markowitz has higher reported gross Sharpe in China and India in the published reference table;
- the US benchmark Sharpe in the paper exceeds BL's published Sharpe;
- BL does not dominate every crisis drawdown/recovery outcome;
- the SOE hypothesis is not statistically supported.

The purpose of the repository is empirical evaluation, not to force
Black-Litterman to win every metric.
