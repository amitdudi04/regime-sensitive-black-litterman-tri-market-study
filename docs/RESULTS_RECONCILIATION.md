# Black–Litterman results reconciliation

**Status: not ready to replace the paper tables.** The corrected pipeline was run locally on 2026-10-13 using freshly retrieved adjusted-close price data. The run is reproducible from source code and records sample windows, but its strategy metrics differ materially from the historical machine-readable paper tables. The discrepancy is not resolved by adding initial deployment costs or changing the benchmark labels.

## Sample coverage in the current run

| Market | Common price history starts | Out-of-sample starts | OOS end | OOS observations |
|---|---|---|---|---:|
| US | 2010-01-04 | 2011-01-04 | 2024-12-31 | 3,521 |
| China | 2013-11-06 | 2014-11-07 | 2024-12-31 | 2,553 |
| India | 2012-02-09 | 2013-02-13 | 2024-12-31 | 2,991 |

The requested main-sample end date is exclusive (\`2025-01-01\`), so the final possible date is \`2024-12-31\`. ETF launch dates mean that the three markets do not share the same effective sample.

## Strategy results: historical paper snapshot vs current implementation

The historical figures below come from \`results/paper_results/tri_market_summary.csv\`. Current values come from the local run's \`results/generated/tri_market_summary.csv\`. Return, volatility, Sharpe and drawdown are generated using the same conventions within each run, but the two runs are not reconciled.

| Market | Model | Historical return | Current return | Historical Sharpe | Current Sharpe | Historical ASI | Current ASI |
|---|---|---:|---:|---:|---:|---:|---:|
| US | Black-Litterman | 12.99% | 15.45% | 0.650 | 0.807 | 0.001632 | 0.009241 |
| US | Markowitz | 13.24% | 15.90% | 0.614 | 0.745 | 0.015365 | 0.790684 |
| China | Black-Litterman | 1.20% | 6.16% | 0.042 | 0.213 | 0.000391 | 0.001443 |
| China | Markowitz | 2.64% | 4.54% | 0.088 | 0.150 | 0.010772 | 0.695032 |
| India | Black-Litterman | 7.60% | 10.97% | 0.356 | 0.508 | 0.000322 | 0.002298 |
| India | Markowitz | 9.76% | 13.23% | 0.440 | 0.585 | 0.007822 | 0.573067 |

The turnover values also diverge substantially. In the current implementation, average rebalance turnover is the mean L1 change between the new target and drift-adjusted pre-trade weights, excluding initial deployment. The historical table's exact turnover implementation is not recoverable from this shallow local Git history. Do not compare the turnover columns as equivalent until the historical calculation is established.

The current Markowitz weights frequently concentrate at or near a single ETF, which explains its large current ASI and turnover. The configured optimizer permits weights between 0 and 100%, with no tighter concentration cap. Do **not** add a new cap, shrinkage rule, or regularizer merely to force the results to match the paper: that would change the research design and must be justified in the manuscript before implementation.

## Crisis recovery discrepancy

| Crisis | Historical paper BL / Markowitz | Current generator BL / Markowitz |
|---|---:|---:|
| 2008 US GFC | 1,093 / 1,056 days | 270 / 272 days |
| 2015 China crash | 458 / 459 days | 378 / 459 days |
| 2020 India COVID shock | 176 / 176 days | 160 / 166 days |

The current generator explicitly measures recovery from the crisis trough to the first return to wealth 1.0, the value at crisis start. The historical table's recovery definition may be different. The China volatility baseline also has only 139 pre-crisis observations because the common ETF history starts in November 2013; this actual count is included in \`crisis_summary.csv\`. These numbers must not replace the manuscript's recovery table until the original definition is confirmed.

## Benchmark convention

The regenerated pipeline uses adjusted-close ETF proxies—SPY, ASHR and INDA—so benchmark and portfolio returns use a consistent adjusted-close convention and the same dates. Each proxy is also part of its optimized basket, so it is a constituent-ETF comparison, not an independent index comparison. The historical paper uses index-style benchmarks; its old benchmark figures are not directly comparable to the regenerated proxy values.

## What remains before publication

1. Recover the exact original calculation or confirm the intended definitions for turnover, ASI, crisis recovery and benchmark returns.
2. Confirm whether the manuscript's Markowitz concentration behavior matches the stated optimization objective and constraints.
3. Run the same confirmed method over a frozen, documented data snapshot; save source hashes and output checksums.
4. Reconcile every table, figure, abstract claim and README figure to the generated output.
5. Only then update the paper's numerical results and remove the historical-snapshot warning.

Until those checks are complete, retain \`results/paper_results/\` as historical evidence and treat \`results/generated/\` as a local diagnostic run, not the canonical paper release.
