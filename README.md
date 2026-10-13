# Regime-Sensitive Black-Litterman Portfolio Allocation

A rolling out-of-sample comparison of Black-Litterman and classical mean-variance (Markowitz) allocation across US, China and India ETF baskets.

**Author:** Amit Kumar Dudi

**Research manuscript used as the published-results reference:** *Black-Litterman vs. Markowitz: Stability, Turnover, and Crisis Dynamics Across Global Markets* (March 2026; SSRN 6479462).

## Research question

Does equilibrium anchoring in the Black-Litterman framework reduce target-weight instability and trading turnover relative to a historical-mean Markowitz optimizer, and how do the approaches compare in performance and selected crisis windows?

## Asset universes

| Market | ETFs |
|---|---|
| United States | SPY, QQQ, IWM, XLF, XLK |
| China | ASHR, KWEB, MCHI, FXI |
| India | INDA, EPI, SMIN, INDY |

The configured main sample requests 2010-01-01 through 2024-12-31 (the configured end date, 2025-01-01, is exclusive). Effective common-history dates differ by market because the ETFs did not all trade over the same period.

## Method in the current public implementation

- 252-trading-day estimation window and 63-trading-day rebalance interval.
- Ledoit-Wolf covariance shrinkage.
- Long-only, fully invested portfolios, with weights permitted from 0% to 100%.
- Historical-mean expected returns for Markowitz.
- Black-Litterman posterior expected returns using an identity view matrix and the view blend: Q = Pi + 0.10 * (mu_hist - Pi).
- Proportional transaction costs of 10 basis points per unit of L1 turnover.
- Rolling out-of-sample evaluation and separate crisis and fixed-tau diagnostics.

**Important implementation distinction:** the public implementation currently defaults to an equal-weight equilibrium prior. The manuscript describes a market-capitalization-implied prior. The published paper results therefore must not be described as reproduced by the current implementation until this difference and the related output discrepancies are resolved.

## Published-paper performance results

The table below preserves the values reported in the manuscript's Table 2 and the historical tri-market CSV. These are **paper-release reference values**, not outputs verified by the current implementation.

| Market | Model | Return | Volatility | Sharpe | Turnover | ASI | Max drawdown |
|---|---|---:|---:|---:|---:|---:|---:|
| US | Black-Litterman | 12.99% | 20.00% | 0.650 | 0.20% | 0.001632 | -38.04% |
| US | Markowitz | 13.24% | 21.57% | 0.614 | 1.58% | 0.015365 | -33.95% |
| US | Benchmark | 13.19% | 19.83% | 0.665 | - | - | -37.87% |
| China | Black-Litterman | 1.20% | 28.45% | 0.042 | 0.08% | 0.000391 | -68.07% |
| China | Markowitz | 2.64% | 30.19% | 0.088 | 1.12% | 0.010772 | -68.58% |
| China | Benchmark | 1.20% | 28.74% | 0.042 | - | - | -68.66% |
| India | Black-Litterman | 7.60% | 21.34% | 0.356 | 0.07% | 0.000322 | -53.67% |
| India | Markowitz | 9.76% | 22.18% | 0.440 | 0.82% | 0.007822 | -50.07% |
| India | Benchmark | 7.54% | 21.33% | 0.353 | - | - | -53.78% |

**Interpretation note.** In the published table, Black-Litterman has lower reported ASI and turnover in all three markets. It does not dominate every return metric: Markowitz has a higher reported Sharpe ratio in China and India, and the US benchmark Sharpe is higher than the Black-Litterman Sharpe. These are historical reported findings, not evidence of universal superiority.

**Comparability note.** The paper and repository do not yet have a fully reconciled calculation trail for every published metric. The historical figures are preserved to avoid silently replacing the manuscript's results with numbers from a different run. Metric definitions, effective sample dates, benchmark construction and the equilibrium prior must be reconciled before claiming exact computational reproduction.

## Current local diagnostic run - not the paper results

A local pipeline run was recorded on 2026-10-13 using checksum-identified adjusted-close price snapshots. Its outputs are under the ignored results/generated directory and are not committed as canonical research results. The values differ materially from the historical paper-release table.

Examples:

| Market | Model | Paper ASI | Current diagnostic ASI | Status |
|---|---|---:|---:|---|
| US | Black-Litterman | 0.001632 | 0.009242 | Unresolved |
| US | Markowitz | 0.015365 | 0.790682 | Unresolved |
| China | Black-Litterman | 0.000391 | 0.001443 | Unresolved |
| China | Markowitz | 0.010772 | 0.695031 | Unresolved |
| India | Black-Litterman | 0.000322 | 0.002298 | Unresolved |
| India | Markowitz | 0.007822 | 0.573067 | Unresolved |

The current Markowitz run often places nearly all weight in one ETF. The configured optimizer permits up to 100% in one asset. No concentration cap or regularizer has been added to force agreement with the paper.

### Crisis results reported in the paper

| Crisis | Model | Max drawdown | Volatility spike | Recovery trading days |
|---|---|---:|---:|---:|
| 2008 US GFC | Black-Litterman | -62.57% | 1.94x | 1,093 |
| 2008 US GFC | Markowitz | -62.18% | 1.93x | 1,056 |
| 2015 China crash | Black-Litterman | -43.42% | 1.92x | 458 |
| 2015 China crash | Markowitz | -43.82% | 1.95x | 459 |
| 2020 India COVID | Black-Litterman | -47.44% | 3.39x | 176 |
| 2020 India COVID | Markowitz | -47.48% | 3.40x | 176 |

The current diagnostic crisis metrics also differ from these values. The current generator uses frozen pre-crisis target weights, a crisis-start wealth reference of 1.0, and weighted daily log returns; it records actual baseline observation counts. These definitions are documented in docs/METHODOLOGY.md. The differences remain unresolved, so the generated figures must not be substituted into the published table.

### Tau sensitivity reported in the paper

| Tau | Paper-reported Sharpe |
|---:|---:|
| 0.01 | 0.3993 |
| 0.05 | 0.3983 |
| 0.10 | 0.3949 |
| 0.15 | 0.3929 |
| 0.20 | 0.3926 |

The current fixed-tau diagnostic produces materially different Sharpe ratios (approximately 0.808 to 0.804). The original paper's sample, prior, and calculation details have not been recovered sufficiently to treat the two series as comparable.

## Research notes and limitations

1. **Equilibrium prior:** the manuscript describes a market-capitalization-implied prior; the current default is equal weight.
2. **Return convention:** the current main backtest uses simple returns for portfolio P&L. The crisis diagnostic uses weighted log returns. The manuscript describes continuously compounded returns in its data section, so these conventions need to be distinguished before claiming a full reproduction.
3. **Benchmarks:** the current run uses SPY, ASHR and INDA adjusted-close ETF proxies, each also present in its optimized basket. The historical paper table labels index-style benchmarks. These are not equivalent benchmark definitions.
4. **Sample coverage:** the current common China ETF history begins in November 2013 and India in February 2012; these baskets do not provide identical 2010-start coverage.
5. **Turnover:** historical turnover excludes initial cash-to-portfolio deployment, while the current run records that deployment separately. The exact historical calculation has not been recovered.
6. **Crisis results and tau sensitivity:** current diagnostics do not match the paper values and remain unresolved.
7. **Inference:** crisis windows are selected historical events; transaction costs are proportional assumptions and do not model nonlinear market impact.

See [the results reconciliation](docs/RESULTS_RECONCILIATION.md) for the detailed comparison and unresolved items, and [the methodology](docs/METHODOLOGY.md) for implementation conventions.

## Run the pipeline

Install dependencies:

    pip install -r requirements.txt

Run the tri-market pipeline:

    python -m pipelines.run_tri_market_pipeline

The pipeline writes local outputs to results/generated/, including result tables, date manifests, factor regression, crisis diagnostics, tau sensitivity and RUN_MANIFEST.json. Price snapshots and their hashes are retained locally and excluded from version control. A run creates diagnostic outputs; it does not automatically validate or replace the paper-release values.

Generate figures from the latest local run:

    python scripts/generate_research_figures.py

Run tests:

    python -m unittest discover -s tests -v

## Repository layout

- core/ - market data and return utilities
- models/ - Black-Litterman model and optimizer
- backtesting/ - rolling backtest and crisis helpers
- analysis/ - factor, regime and statistical analysis
- pipelines/ - end-to-end tri-market pipeline
- results/paper_results/ - historical paper-release tables
- results/generated/ - local diagnostic outputs (ignored by Git)
- docs/ - methodology and results reconciliation
- tests/ - numerical and chronology tests
