# Manuscript and Archived October 13 Diagnostic — Historical Reconciliation

**Historical comparison only.** This document records the March paper against the *October 13, 2026* preliminary diagnostic; it is **not** the current corrected-pipeline result. See [the October 30 validated diagnostic](EMPIRICAL_AUDIT_2026-10-30.md) for newer calculations and [the corrections register](REVIEWER_CORRECTIONS.md) for unresolved manuscript claims.

**Diagnostic version warning (2026-10-30):** All numerical values labeled *Current* below were generated on 2026-10-13 **before** the audit branch corrected buy-and-hold daily portfolio accounting and the first-observation ASI denominator. They are prior-run diagnostics, **not validated outputs of the latest code**. The paper-reference numbers are preserved unchanged. Recompute all return-derived, turnover-derived, Sharpe, factor, tau, and allocation values from the original checksum-verified input snapshots before updating the comparisons. Crisis weighted-log diagnostics are a separate convention and must not be represented as the revised buy-and-hold wealth path.

This document separates three things that must not be conflated:

1. **Published-paper values:** figures printed in the supplied March 2026 manuscript and retained in results/paper_results/.
2. **October 13 diagnostic values:** outputs generated locally on 2026-10-13 and retained in the ignored results/generated/ directory.
3. **Reproduction status:** whether the current implementation has been shown to reproduce the paper's methodology and numerical results. It has not.

The manuscript's Table 2, Table 4 and Table 8 values were checked against the corresponding historical CSVs. The displayed figures agree, subject to rounding. This confirms transcription consistency between the paper and historical CSVs; it does **not** establish that the current implementation reproduces the calculations.

## Source-of-truth rules

- Keep the supplied manuscript as the reference for what was published.
- Keep results/paper_results/ unchanged as the historical paper-release record.
- Treat results/generated/ as a separate diagnostic run, not as replacement paper results.
- Do not alter model parameters, impose concentration limits, change data windows or select a different benchmark solely to force a numerical match.
- Do not describe the paper as independently reproduced until the prior, return conventions, benchmark, turnover/ASI calculation, crisis path and evaluation sample have been reconciled.
- Values below are shown rounded for readability. The CSVs retain their stored precision.

## 1. Tri-market performance

The paper-reported values below match the historical tri_market_summary.csv. October 13 values are from the local generated summary.

| Market | Model | Paper return | Oct 13 return | Paper volatility | Oct 13 volatility | Paper Sharpe | Oct 13 Sharpe | Paper ASI | Oct 13 ASI |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| US | Black-Litterman | 12.99% | 15.45% | 20.00% | 19.14% | 0.650 | 0.807 | 0.001632 | 0.009242 |
| US | Markowitz | 13.24% | 15.90% | 21.57% | 21.35% | 0.614 | 0.745 | 0.015365 | 0.790682 |
| China | Black-Litterman | 1.20% | 6.16% | 28.45% | 28.90% | 0.042 | 0.213 | 0.000391 | 0.001443 |
| China | Markowitz | 2.64% | 4.54% | 30.19% | 30.30% | 0.088 | 0.150 | 0.010772 | 0.695031 |
| India | Black-Litterman | 7.60% | 10.97% | 21.34% | 21.58% | 0.356 | 0.508 | 0.000322 | 0.002298 |
| India | Markowitz | 9.76% | 13.23% | 22.18% | 22.62% | 0.440 | 0.585 | 0.007822 | 0.573067 |

The paper also reports maximum drawdowns of -38.04% (US BL), -33.95% (US Markowitz), -68.07% (China BL), -68.58% (China Markowitz), -53.67% (India BL) and -50.07% (India Markowitz). The current run reports -35.41%, -31.15%, -63.90%, -65.35%, -49.67% and -47.59%, respectively. These values differ and remain unresolved.

### Turnover comparison

| Market | Model | Paper turnover | Oct 13 average rebalance turnover |
|---|---|---:|---:|
| US | Black-Litterman | 0.20% | 2.87% |
| US | Markowitz | 1.58% | 80.29% |
| China | Black-Litterman | 0.08% | 3.58% |
| China | Markowitz | 1.12% | 70.73% |
| India | Black-Litterman | 0.07% | 1.72% |
| India | Markowitz | 0.82% | 58.34% |

**Interpretation note.** The paper reports lower ASI and turnover for Black-Litterman in all three markets. That is a description of the published table, not a conclusion verified by the current run. The current Markowitz portfolios frequently concentrate at or near one ETF, which produces very large weight changes and turnover. The configured optimizer allows 0-100% weights; no cap or regularizer has been added to force agreement.

**Comparability note.** The historical calculation details for turnover and ASI have not been recovered sufficiently to establish that the current metrics are computed identically. The current run separately records initial cash-to-portfolio deployment; the historical turnover figures exclude that initial deployment. This difference alone does not explain the full discrepancy.

## 2. Effective sample and benchmark coverage

| Market | Current common price history starts | Current OOS start | Current OOS end | OOS observations |
|---|---|---|---|---:|
| US | 2010-01-04 | 2011-01-04 | 2024-12-31 | 3,521 |
| China | 2013-11-06 | 2014-11-07 | 2024-12-31 | 2,553 |
| India | 2012-02-09 | 2013-02-13 | 2024-12-31 | 2,991 |

The configured end date is exclusive: 2025-01-01 means the last possible date is 2024-12-31. The common China ETF basket does not provide observations back to 2010, and the India basket also starts later than 2010. The paper's stated 2010-2025 coverage must not be read as proof that every current ETF basket has identical coverage.

**Benchmark note.** The paper describes market/index-style benchmarks, while the October 13 diagnostic uses adjusted-close ETF proxies SPY, ASHR and INDA. Each proxy is also a constituent of the optimized basket. These are not equivalent benchmark definitions, and the current proxy results must not be substituted for the historical benchmark rows.

## 3. Crisis results

| Crisis | Model | Paper max drawdown | Oct 13 max drawdown | Paper volatility spike | Oct 13 volatility spike | Paper recovery days | Oct 13 recovery days |
|---|---|---:|---:|---:|---:|---:|---:|
| 2008 US GFC | Black-Litterman | -62.57% | -53.47% | 1.94x | 2.40x | 1,093 | 277 |
| 2008 US GFC | Markowitz | -62.18% | -46.99% | 1.93x | 2.01x | 1,056 | 272 |
| 2015 China crash | Black-Litterman | -43.42% | -37.44% | 1.92x | 1.58x | 458 | 402 |
| 2015 China crash | Markowitz | -43.82% | -49.76% | 1.95x | 1.51x | 459 | 1,220 |
| 2020 India COVID | Black-Litterman | -47.44% | -42.57% | 3.39x | 4.47x | 176 | 140 |
| 2020 India COVID | Markowitz | -47.48% | -41.68% | 3.40x | 4.30x | 176 | 161 |

The manuscript defines recovery against the portfolio value at crisis start, with recovery duration measured in trading-index positions from trough to recovery. The current generator freezes the last target weights strictly before the crisis, normalizes crisis-start wealth to 1.0, uses weighted daily log returns for the crisis diagnostic, and keeps the weights frozen through recovery. The outputs still differ materially.

**Interpretation note.** A matching written definition does not prove matching calculations. The historical weight vectors, exact price history and original crisis metric implementation have not been recovered. The China 2015 diagnostic has only 139 available pre-crisis observations because the common ETF history starts in November 2013. Until the source of the differences is identified, neither set should be represented as a fresh reproduction of the other.

## 4. Tau sensitivity

| Tau | Paper-reported Sharpe | Oct 13 fixed-tau Sharpe |
|---:|---:|---:|
| 0.01 | 0.3993 | 0.8077 |
| 0.05 | 0.3983 | 0.8069 |
| 0.10 | 0.3949 | 0.8059 |
| 0.15 | 0.3929 | 0.8050 |
| 0.20 | 0.3926 | 0.8041 |

The October 13 diagnostic uses a fixed tau per run, with tau_low_vol and tau_high_vol set equal, on the same US out-of-sample window. The historical sensitivity table does not retain enough metadata to confirm the original market, exact sample, prior construction, net/gross return convention or calculation path. The two series therefore remain **not comparable / unresolved**.

## 5. Other manuscript findings not reproduced by the current run

### Factor exposure (paper Table 5)

The manuscript reports a US four-factor regression with annualized alpha, market/size/value/momentum betas and R-squared. The October 13 diagnostic factor_regression_us.csv uses 3,521 aligned observations and HAC maxlags=5. Its coefficients differ materially from the paper table.

| Model | Paper annualized alpha | Oct 13 annualized alpha | Paper alpha t-stat | Oct 13 alpha t-stat | Paper MKT beta | Oct 13 MKT beta | Paper MOM beta | Oct 13 MOM beta | Paper R-squared | Oct 13 R-squared |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Black-Litterman | -4.27% | 0.50% | -1.213 | 0.869 | 0.821 | 1.0658 | 0.0144 | 0.0045 | 0.6346 | 0.9858 |
| Markowitz | -7.38% | -1.13% | -1.418 | -0.552 | 0.904 | 1.1482 | 0.1150 | 0.2239 | 0.4860 | 0.8826 |

The paper also reports SMB and HML betas that differ from the October 13 diagnostic: paper BL SMB 0.0525 and HML -0.0012; current BL SMB 0.0755 and HML 0.0331. Paper Markowitz SMB -0.0217 and HML 0.0117; current Markowitz SMB -0.0467 and HML -0.0221. The original paper does not provide enough retained run metadata here to establish matching sample dates, exact factor data vintage and HAC lag settings.

**Internal paper note.** The Table 5 BL momentum t-statistic appears as +0.856 in the table, while the narrative later gives -0.856. Both descriptions indicate a non-significant loading, but the sign inconsistency should be checked against the final manuscript source rather than silently resolved in repository documentation.

### Statistical validation (paper Section 13)

The manuscript reports a volatility-suppression statistic of -2.678 (p = 0.0106) and an ASI-reduction statistic of 2.927 (p = 0.0046), attributed to circular block bootstrap testing. The current run does not save a matching output table containing these statistics, sample definitions, block size, iteration count and random seed. The presence of bootstrap helper functions in the code is not evidence that these exact reported tests were reproduced.

**Interpretation note.** Keep these as paper-reported statistics until the exact test inputs and run configuration can be traced. Do not label them independently verified by the current pipeline. There is also a significance-threshold issue in the manuscript prose: p = 0.0106 is below 0.05 but above 0.01, so the reported volatility-suppression result is significant at 5%, not at 1%, under conventional cutoffs. The ASI result (p = 0.0046) is below both thresholds.

### SOE versus private firms (paper Table 6)

| Metric | Paper SOE | Paper private |
|---|---:|---:|
| Annualized net return | 11.49% | 22.96% |
| Annualized volatility | 20.51% | 25.64% |
| Sharpe ratio | 0.41 | 0.78 |
| Maximum drawdown | -43.63% | -39.11% |
| Average turnover | 7.32% | 15.79% |

The paper reports a test statistic of -0.563 and p-value of 0.572. The current repository helper provides descriptive return and volatility summaries for explicitly mapped groups; it is not a complete reproduction of the paper's ownership-level hypothesis test, turnover, drawdown and Sharpe calculations. The October 30 audit adds a dated-classification analysis helper but still lacks the original Chinese stock-level ownership inputs; paper Table 6 is unreproduced.

**Interpretation note.** The paper itself does not reject the null at conventional significance levels (p = 0.572). The descriptive differences should not be presented as statistically established SOE/private outperformance or downside protection.

### Regime-conditioned performance (paper Table 7)

| Regime | Paper BL Sharpe | Paper Markowitz Sharpe | Paper BL return | Paper Markowitz return |
|---|---:|---:|---:|---:|
| Low volatility | 1.282 | 1.397 | 17.27% | 19.80% |
| High volatility | -0.934 | -1.045 | -31.22% | -34.71% |

The current regime helper uses smoothed state probabilities for ex-post descriptive classification. The October 13 diagnostic did not save the matching regime table. New October 30 ex-post regime outputs exist, but they do not reproduce the manuscript's Table 7. Smoothed probabilities use the full sample and are not suitable as real-time trading signals without a separate filtered-probability design.

**Interpretation note.** The table is descriptive unless a corresponding statistical test is specified and retained. The manuscript's phrase "statistically improved downside performance" should not be repeated as a verified statistical conclusion based on Table 7 alone.

### Overall claims and downside interpretation

The paper's broad wording about superior downside mitigation should be read alongside its own Table 2: the reported Black-Litterman maximum drawdown is worse than Markowitz in the US (-38.04% versus -33.95%) and India (-53.67% versus -50.07%), and only slightly less negative in China (-68.07% versus -68.58%). The crisis table may support narrower event-specific observations, but the published cross-market table does not establish universal drawdown superiority.

Likewise, lower reported turnover suggests lower modeled trading costs under the stated cost assumption, but turnover alone does not prove superior net-of-cost returns. The manuscript's gross/net terminology is not fully consistent across sections, and the current run does not reproduce the paper's performance values.
## 6. Methodology differences requiring explicit disclosure

### Equilibrium prior

The manuscript describes a market-capitalization-implied equilibrium prior. The current public implementation defaults to equal_weight_proxy; the historical capitalization/AUM weight series is not available in the repository. This is a research-design difference, not just a documentation typo.

### Return convention

The manuscript's data section describes continuously compounded returns. The current main backtest uses adjusted-close simple returns for portfolio P&L, while the crisis diagnostic uses weighted daily log returns. The documentation must state these separately. We cannot claim exact method reproduction without resolving this difference.

### Benchmark definition

The manuscript's prose refers to a market-capitalization-weighted ETF benchmark, while the historical results table labels index-style benchmarks. The October 13 diagnostic uses SPY, ASHR and INDA as investable ETF proxies that also appear in the optimized baskets. The paper's benchmark prose, table and current proxy definitions are not interchangeable.

### Optimization and concentration

The current optimizer permits weights from 0% to 100% with no tighter concentration cap. The current Markowitz output often becomes highly concentrated. Do not add caps, regularization or other changes simply to make ASI and turnover resemble the historical paper figures. Such a change would alter the research design and would require a separately justified study.

### Initial deployment and turnover

The current run assumes the portfolio starts from cash, records 100% L1 initial deployment for a fully invested long-only portfolio, and charges the associated 10 bps cost. The reported average rebalance turnover excludes that initial deployment. The historical table also excludes initial deployment, but its detailed turnover calculation has not been reconstructed.

## 7. Status and reviewer-facing conclusion

| Item | Status | Documentation treatment |
|---|---|---|
| Paper Table 2 values vs historical tri-market CSV | Matches at displayed precision | Preserve as published-paper reference |
| Paper Table 4 values vs historical crisis CSV | Matches at displayed precision | Preserve as published-paper reference |
| Paper Table 8 values vs historical tau CSV | Matches at displayed precision | Preserve as published-paper reference |
| Current performance metrics vs paper | Unresolved | Keep separate; do not overwrite paper values |
| Current crisis metrics vs paper | Unresolved | Keep separate; explain definition and data limitations |
| Current tau sensitivity vs paper | Unresolved | Keep separate; mark original run metadata as incomplete |
| Market-cap prior vs current equal-weight prior | Methodology discrepancy | Disclose explicitly |
| Paper benchmark descriptions vs current ETF proxies | Methodology discrepancy | Disclose explicitly |
| Full computational reproduction | Not established | Do not claim the current code reproduces the paper |

**Reviewer-facing conclusion:** the repository preserves the numerical values published in the manuscript and makes the October 13 diagnostic differences visible. The paper-to-CSV transcription check passes for the principal performance, crisis and tau tables; the current implementation's computational reproduction of those values remains unresolved.

No model code or numerical output files are changed by this document.
