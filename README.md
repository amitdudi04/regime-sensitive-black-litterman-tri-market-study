# Regime-Sensitive Black-Litterman Portfolio Allocation

Cross-market research on allocation stability, turnover and crisis behavior in the United States, China and India.

**Author:** Amit Kumar Dudi  
**Repository status:** research-facing, audit-cleaned working-paper repository

## What this repository is

This project studies whether an equilibrium-anchored Black-Litterman expected-return model can reduce the allocation instability associated with classical historical-mean Markowitz optimization.

The intended ETF baskets are:

- **United States:** SPY, QQQ, IWM, XLF, XLK
- **China:** ASHR, KWEB, MCHI, FXI
- **India:** INDA, EPI, SMIN, INDY

The canonical implementation uses a 252-trading-day rolling estimation window and a 63-trading-day holding/rebalance interval.

## Source-of-truth hierarchy

The repository deliberately separates three things:

1. **Working-paper reference results** — values reported in the existing paper.
2. **Canonical code** — the cleaned implementation under core/, models/, backtesting/, analysis/, and pipelines/.
3. **Fresh recomputed outputs** — written to results/recomputed/ when the canonical pipeline is run.

Paper values are not manually copied into executable code to make the project appear reproducible.

## Canonical research flow

Observed prices  
→ common-date validation  
→ simple returns for portfolio P&L  
→ 252-day rolling training window  
→ Ledoit-Wolf covariance  
→ Markowitz historical means / Black-Litterman posterior  
→ identical long-only, fully-invested optimizer  
→ 63-day out-of-sample holding period  
→ drift-adjusted turnover and proportional transaction costs  
→ net OOS returns and weight history  
→ ASI / drawdown / factor / regime analysis

## Black-Litterman specification

The equilibrium prior is:

Pi = lambda × Sigma × w_eq

The posterior combines Pi with P, Q, Omega, and tau.

The reconciliation implementation currently uses:

- identity P for absolute ETF views;
- Q = Pi + 0.10 × (historical_mean - Pi);
- diagonal Omega in annualized return-variance units;
- an ex-ante volatility rule for tau;
- an **explicit equal-weight equilibrium proxy** unless defensible historical ETF capitalization/AUM weights are supplied.

The working paper describes a capitalization-weighted equilibrium prior. The public repository does not contain a defensible historical ETF market-cap/AUM series, so the code does **not** substitute price × volume and call it market capitalization.

## Fair BL-vs-Markowitz comparison

The canonical implementation applies the same covariance estimator, risk-aversion parameter, optimizer, long-only constraint, fully-invested constraint and weight bounds to both models.

The primary structural difference is the expected-return vector. Model-specific L2 regularization is excluded from the canonical comparison.

## Published-paper reference results

The existing working paper reports:

| Market | Model | Return | Volatility | Sharpe | Turnover | ASI | Max Drawdown |
|---|---|---:|---:|---:|---:|---:|---:|
| US | Black-Litterman | 12.99% | 20.00% | 0.650 | 0.20% | 0.001632 | -38.04% |
| US | Markowitz | 13.24% | 21.57% | 0.614 | 1.58% | 0.015365 | -33.95% |
| China | Black-Litterman | 1.20% | 28.45% | 0.042 | 0.08% | 0.000391 | -68.07% |
| China | Markowitz | 2.64% | 30.19% | 0.088 | 1.12% | 0.010772 | -68.58% |
| India | Black-Litterman | 7.60% | 21.34% | 0.356 | 0.07% | 0.000322 | -53.67% |
| India | Markowitz | 9.76% | 22.18% | 0.440 | 0.82% | 0.007822 | -50.07% |

These are **paper-reference values**, not a claim that the cleaned pipeline has already reproduced them.

Machine-readable reference tables are under results/reference/.

## Crisis reference

The paper reports recovery durations, measured in trading days from the crisis trough back to crisis-start wealth V(t0):

- US 2008 GFC: BL 1093, Markowitz 1056
- China 2015 crash: BL 458, Markowitz 459
- India 2020 COVID: 176 for both

These results do not establish universal crisis dominance by Black-Litterman.

## Factor analysis

The current canonical factor module uses Kenneth French **US** daily MKT, SMB, HML and MOM factors with Newey-West/HAC inference.

The paper-v1 runner therefore performs this factor regression for the **US portfolio only**. China and India require an explicitly justified local/global factor specification rather than silently reusing US factors.

A significant loading is interpreted as exposure, not proof of a unique causal explanation for performance.

## Regime analysis

The repository distinguishes:

- an ex-ante recent-volatility rule used to condition tau; and
- a two-state Markov-switching model used as an ex-post conditional evaluation layer.

Unless filtered Markov probabilities are explicitly fed into the allocation rule, the Markov model is not described as the portfolio decision engine.

## SOE/private study

The working paper's ex-ante hypothesis is that Chinese state ownership may provide downside resilience. The reported result does not support a statistically significant SOE-vs-private performance difference at conventional levels.

Earlier mock/legacy SOE execution code has been removed from the research-facing branch and remains available in Git history.

## Run the canonical study

Install:

    pip install -r requirements.txt

Run:

    python -m pipelines.paper_v1_pipeline

Fresh outputs are written to:

    results/recomputed/

Generate figures only after a successful empirical run:

    python scripts/generate_research_figures.py

The figure generator reads saved empirical outputs only. It does not create simulated “realistic-looking” research trajectories.

## Repository structure

- core/ — data and return utilities
- models/ — Black-Litterman posterior and common optimizer
- backtesting/ — canonical walk-forward engine and crisis helpers
- analysis/ — factor, regime, statistics and ownership helpers
- pipelines/ — canonical executable study
- results/reference/ — paper-reported values, explicitly labelled
- results/recomputed/ — generated by the cleaned pipeline
- tests/ — executable mathematical and chronology tests
- docs/ — methodology, architecture, paper status and errata
- scripts/ — empirical figure generation

Historical experiment snapshots, legacy engines, the old GUI and stale result figures were removed from the default branch after being preserved in Git history. A dedicated historical branch also preserves the pre-cleanup state.

## Important limitations

- ETF baskets are low-dimensional proxies for broader markets.
- Transaction costs are stylized proportional frictions, not a full market-impact model.
- The paper's historical capitalization-prior dataset is not present in the public repository.
- Crisis windows are selected ex post, although frozen allocations prevent within-window rebalancing look-ahead.
- The current US factor model should not be treated as a local China/India factor model.
- Published-paper tables remain reference values until the cleaned pipeline is rerun and reconciled end to end.

## Research integrity

Mixed and negative findings are retained:

- Markowitz has higher reported Sharpe in China and India in the paper table.
- The US benchmark Sharpe in the working paper is slightly above BL.
- BL does not dominate every crisis drawdown/recovery outcome.
- The SOE hypothesis is not statistically supported.

The objective is to evaluate Black-Litterman, not to force it to win every metric.
