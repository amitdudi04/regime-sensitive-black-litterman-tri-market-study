# Black–Litterman results reconciliation

**Status: not ready to replace the paper tables.** The corrected pipeline was run locally on 2026-10-13 using checksum-verified adjusted-close price snapshots. The run records its inputs, sample windows and metric conventions, but its strategy metrics differ materially from the historical machine-readable paper tables. The discrepancy is not resolved by charging initial deployment costs or changing benchmark labels.

## Sample coverage in the current run

| Market | Common price history starts | Out-of-sample starts | OOS end | OOS observations |
|---|---|---|---|---:|
| US | 2010-01-04 | 2011-01-04 | 2024-12-31 | 3,521 |
| China | 2013-11-06 | 2014-11-07 | 2024-12-31 | 2,553 |
| India | 2012-02-09 | 2013-02-13 | 2024-12-31 | 2,991 |

The requested main-sample end date is exclusive (\`2025-01-01\`), so the final possible date is \`2024-12-31\`. ETF launch dates mean that the three markets do not share the same effective sample. In particular, the current common China ETF basket cannot support a 2010 start.

## Strategy results: historical paper snapshot vs current implementation

The historical figures below come from \`results/paper_results/tri_market_summary.csv\`. Current values come from the local run's \`results/generated/tri_market_summary.csv\`. Return, volatility, Sharpe and drawdown are generated using the same conventions within each run, but the two runs are not reconciled.

| Market | Model | Historical return | Current return | Historical Sharpe | Current Sharpe | Historical ASI | Current ASI |
|---|---|---:|---:|---:|---:|---:|---:|
| US | Black-Litterman | 12.99% | 15.45% | 0.650 | 0.807 | 0.001632 | 0.009242 |
| US | Markowitz | 13.24% | 15.90% | 0.614 | 0.745 | 0.015365 | 0.790682 |
| China | Black-Litterman | 1.20% | 6.16% | 0.042 | 0.213 | 0.000391 | 0.001443 |
| China | Markowitz | 2.64% | 4.54% | 0.088 | 0.150 | 0.010772 | 0.695031 |
| India | Black-Litterman | 7.60% | 10.97% | 0.356 | 0.508 | 0.000322 | 0.002298 |
| India | Markowitz | 9.76% | 13.23% | 0.440 | 0.585 | 0.007822 | 0.573067 |

The turnover values also diverge substantially. In the current implementation, average rebalance turnover is the mean L1 change between the new target and drift-adjusted pre-trade weights, excluding initial deployment. The historical table's exact turnover implementation is not recoverable from this shallow local Git history. Do not compare the turnover columns as equivalent until the historical calculation is established.

The current Markowitz weights frequently concentrate at or near a single ETF, which explains its large current ASI and turnover. The configured optimizer permits weights between 0 and 100%, with no tighter concentration cap. Do **not** add a new cap, shrinkage rule, or regularizer merely to force the results to match the paper: that would change the research design and must be justified in the manuscript before implementation.

## Crisis metrics: historical paper snapshot vs current generator

| Crisis | Model | Historical max drawdown | Current max drawdown | Historical vol. spike | Current vol. spike | Historical recovery days | Current recovery days |
|---|---|---:|---:|---:|---:|---:|---:|
| 2008 US GFC | Black-Litterman | -62.57% | -53.47% | 1.94x | 2.40x | 1,093 | 277 |
| 2008 US GFC | Markowitz | -62.18% | -46.99% | 1.93x | 2.01x | 1,056 | 272 |
| 2015 China crash | Black-Litterman | -43.42% | -37.44% | 1.92x | 1.58x | 458 | 402 |
| 2015 China crash | Markowitz | -43.82% | -49.76% | 1.95x | 1.51x | 459 | 1,220 |
| 2020 India COVID | Black-Litterman | -47.44% | -42.57% | 3.39x | 4.47x | 176 | 140 |
| 2020 India COVID | Markowitz | -47.48% | -41.68% | 3.40x | 4.30x | 176 | 161 |

The corrected generator keeps each pre-crisis target-weight vector frozen from crisis start through recovery. It converts adjusted-close simple asset returns to weighted daily log returns, normalizes the first observed crisis valuation to \(V(t_0)=1.0\), and defines recovery as the first return to that starting value after the trough. This follows the paper's stated crisis-method definition. The resulting values still diverge materially because the current optimizer weights, data history and/or original metric calculations differ from the historical release. The current China volatility baseline has only 139 pre-crisis observations because the common ETF history starts in November 2013; this actual count is included in \`crisis_summary.csv\`.

## Tau sensitivity

The old \`results/paper_results/tau_sensitivity.csv\` values did not identify a market, sample window, observation count or return convention. The new fixed-\(\tau\) generator uses the same US OOS sample for each value.

| \(\tau\) | Historical reported Sharpe | Current fixed-\(\tau\) Sharpe |
|---:|---:|---:|
| 0.01 | 0.3993 | 0.8077 |
| 0.05 | 0.3983 | 0.8069 |
| 0.10 | 0.3949 | 0.8059 |
| 0.15 | 0.3929 | 0.8050 |
| 0.20 | 0.3926 | 0.8041 |

The old and current sensitivity values are not comparable until the original sample and calculation are recovered. Current rows include OOS start/end dates, observation counts, return series, tau rule and equilibrium-weight method.

## Benchmark convention

The regenerated pipeline uses adjusted-close ETF proxies—SPY, ASHR and INDA—so benchmark and portfolio returns use a consistent adjusted-close convention and the same dates. Each proxy is also part of its optimized basket, so it is a constituent-ETF comparison, not an independent index comparison. The paper's prose describes a market-cap-weighted ETF allocation, while its results table reports index-style benchmarks; that inconsistency must be resolved before replacing the benchmark rows.

## Method claims that must be reconciled

- The paper describes a market-capitalization-implied equilibrium prior, while the public implementation defaults to \`equal_weight_proxy\`. The paper must either describe the implemented equal-weight prior accurately or provide the historical capitalization/AUM series and rerun the study.
- The paper says adjusted closes are converted to continuously compounded returns, while the main backtest currently uses simple returns for portfolio P&L. The crisis diagnostic uses weighted daily log returns, matching the paper's specific crisis-method description. The manuscript must distinguish these conventions or the main backtest must be changed and fully rerun.
- The \`tau\` allocation rule is based on a volatility threshold using the training window. The separate Markov-switching model is an ex-post diagnostic; its smoothed probabilities do not drive portfolio weights.
- The benchmark prose and benchmark table are inconsistent. The current pipeline uses SPY, ASHR and INDA adjusted-close ETF proxies, which are constituents of their optimized baskets and are not independent index benchmarks.
- The configured main sample ends on 2024-12-31. The common China ETF basket starts on 2013-11-06, so the repository cannot support a 2010–2025 China ETF backtest without a different historical data source.

## What remains before publication

1. Recover the historical optimizer constraints/weights and exact turnover/ASI calculation if possible.
2. Confirm the intended return convention and benchmark definition; do not mix simple-return P&L, log-return crisis diagnostics, and index-style benchmark claims without stating the difference.
3. Confirm whether the manuscript's Markowitz concentration behavior matches the stated optimization objective and constraints.
4. Save the Kenneth French factor input series and its checksum as well as the price snapshots before claiming end-to-end reproducibility of factor regressions.
5. Reconcile every table, figure, abstract claim and README figure to the generated output.
6. Only then update the paper's numerical results and remove the historical-snapshot warning.

Until those checks are complete, retain \`results/paper_results/\` as historical evidence and treat \`results/generated/\` as a local diagnostic run, not the canonical paper release.
