# Final empirical findings — Phase 3

**Readiness: READY_WITH_LIMITATIONS.** The eight requested tables and eight available figures are frozen from verified prior outputs. Crisis daily-path Figure 07 is unavailable; the verified buy-and-hold crisis summary remains Table 6. No optimization, bootstrap, market download, factor refit or regime estimation was run in Phase 3. This is a publication evidence package, not a revised manuscript or a replication of the March 2026 paper.

## Evidence identity and experiment boundaries

- Principal/robustness evidence: Phase 2 run `ff8cacdc-95f8-458e-8d71-d12efbd9a9f9`, executed source `af84ddfbc93edc7a5143c654d6319d67e3139eef`, frozen on Phase 2 commit `7553cf8bff59a4f3d8bad7d15b779707fc533fa1`. Tables 2–5 and Figures 01–06 use these outputs and associated verified daily returns/decisions.
- Supplementary evidence: Phase 1 run `693ec4b2-0e95-4367-afef-904dbac8f9c3`, executed source `f7f96e3c6646e7b171c43b8bb6e8a5b129053609`, archived on completed Phase 1 commit `598fe0d3c0a7cd7ebaf5709ae62b7c6735b92a0d`. Tables 6–8 and Figures 08–09 retain this provenance, not a relabelled Phase 2 fit. Table 1 links Phase 1 dataset coverage to the identical Phase 2 price vintage and OOS samples.
- Frozen price fingerprints agree across these sources. Each input is checked against its protected source commit or the corresponding pinned run-manifest hash. LF/CRLF conversion alone is tolerated for historical text files; actual and canonical hashes are both recorded.
- Machine-readable authority: `table_01_*.csv` through `table_08_*.csv`; all numerical values are selected or explicitly transformed from source evidence. `FINAL_RESEARCH_TABLES.md` is the manuscript-readable rendering. P-values below the display threshold, including machine underflow zeros, are printed as <0.0001; source precision is preserved in CSV.

## What the results support

BL has much lower target ASI than unrestricted historical-mean Markowitz in all three baskets. ASI measures changes in optimizer targets; it is not actual trading, initial deployment or evidence of a significant Sharpe gain. Rebalanced 1/N has zero target ASI but positive rebalance turnover because prices make holdings drift.

BL's returns and Sharpe closely resemble the periodically rebalanced 1/N benchmark. Their differences, derived from Table 2, are:

| Market | BL minus 1/N Net Return (annual bps) | BL minus 1/N Sharpe |
| --- | --- | --- |
| US | -0.347785 | -0.000656 |
| China | -0.165796 | -0.000004 |
| India | 0.194287 | 0.000079 |

These small observed differences do not establish additional economic or causal value from Bayesian updating over 1/N. This is particularly relevant because the default equilibrium prior is an **equal-weight proxy**, not observed market-capitalization weights, and views are a mild historical-mean tilt. The experiment is strongly anchored toward equal allocations by design.

The predefined matched 40% target cap reduces Markowitz target HHI, target instability and traded turnover and narrows its Sharpe gaps with BL. US/China Markowitz Sharpe improves under the cap; India Sharpe declines. The BL cap is inactive in these realized samples. Bounds are applied identically to both optimized strategies at each matched comparison. A 40% target bound is not continuous enforcement on drifting holdings.

BL has no universal return or drawdown dominance: its US/India drawdowns are worse than unrestricted Markowitz in the primary comparison. No claim of statistically superior downside protection follows from descriptive MDDs or selected crisis events.

## Costs, arithmetic returns and compounded wealth

All four cost rates reuse the same gross paths and trading decisions. Positive costs reduce terminal wealth for unchanged paths. Lower turnover alone does not prove better net investment performance. The actual rankings by the two distinct metrics are:

| Market | Cost (bps per L1) | Arithmetic net-return ranking | Terminal-wealth ranking |
| --- | --- | --- | --- |
| US | 0 | Markowitz > Equal-weight > Black-Litterman | Markowitz > Equal-weight > Black-Litterman |
| US | 5 | Markowitz > Equal-weight > Black-Litterman | Markowitz > Equal-weight > Black-Litterman |
| US | 10 | Markowitz > Equal-weight > Black-Litterman | Markowitz > Equal-weight > Black-Litterman |
| US | 20 | Markowitz > Equal-weight > Black-Litterman | Equal-weight > Black-Litterman > Markowitz |
| China | 0 | Equal-weight > Black-Litterman > Markowitz | Black-Litterman > Equal-weight > Markowitz |
| China | 5 | Equal-weight > Black-Litterman > Markowitz | Black-Litterman > Equal-weight > Markowitz |
| China | 10 | Equal-weight > Black-Litterman > Markowitz | Black-Litterman > Equal-weight > Markowitz |
| China | 20 | Equal-weight > Black-Litterman > Markowitz | Black-Litterman > Equal-weight > Markowitz |
| India | 0 | Markowitz > Black-Litterman > Equal-weight | Markowitz > Black-Litterman > Equal-weight |
| India | 5 | Markowitz > Black-Litterman > Equal-weight | Markowitz > Black-Litterman > Equal-weight |
| India | 10 | Markowitz > Black-Litterman > Equal-weight | Markowitz > Black-Litterman > Equal-weight |
| India | 20 | Markowitz > Black-Litterman > Equal-weight | Markowitz > Black-Litterman > Equal-weight |

Thus cost changes can alter a terminal-wealth ranking without altering the arithmetic annual-return ranking. Arithmetic annual mean is daily mean ×252; terminal wealth is the product of one plus each daily net simple return. They must never be described as interchangeable growth rates. Direct modeled fee expenditure is also distinct from gross-minus-net terminal wealth, which includes growth forgone. Transaction costs are proportional to the existing drift-adjusted L1 turnover model; no execution-spread or market-impact calibration is claimed.

## Statistical uncertainty and generalization

Table 5 contains 12 scenario rows, with 0 unadjusted p-values below 0.05. All corresponding 95% percentile intervals include zero. The three cap-inactive BL/1N rows duplicate the main BL/1N results rather than adding independent evidence. The appropriate conclusion is failure to establish a Sharpe difference under the retained approximate paired bootstrap, not proof of equivalence or equal future performance. No new inferential framework or multiplicity adjustment was introduced.

The markets have unequal OOS periods and observation counts (Table 1). Cross-market cumulative wealth is therefore not a common-horizon comparison. These are small, overlapping baskets of **US-listed USD-denominated ETFs** with international equity exposure, not pure local-currency Chinese/Indian market returns. Generalization beyond these instruments, samples and modeled costs is limited.

## Supplementary evidence and missing material

Table 6 is a standalone historical stress test: the last pre-crisis target is purchased before the first event return, then held without trades through recovery. Recovery means the first subsequent return to crisis-start NAV 1 after the crisis-window drawdown trough; the duration is trading-index positions from trough to recovery. It is not recovery to the previous peak or time from crisis start. Missing recovery remains censored. Main rolling OOS returns are not substituted for these frozen-holdings stress paths. Legacy weighted-log summary fields are deliberately excluded.

**CRISIS_DAILY_PATH_UNAVAILABLE:** the retained verified evidence contains primary crisis drawdown/recovery summaries, not frozen-holdings daily crisis curves. Figure 07 is not generated, and no path is reconstructed from summary values. Retain the limitation or recover original verified path evidence before using such a figure.

Table 7 and Figure 08 are US-only factor evidence from Phase 1, with exact sample/factor fingerprints and HAC inference. They do not attribute China/India performance to US factors and are not regressions of Phase 2 capped or 1/N paths. Table 8/Figure 09 are the five pre-existing US fixed-tau runs, distinct from the main historical-volatility adaptive rule. Phase 1 Markov smoothed states remain ex-post descriptions, never prospective trading signals; no regime refit is part of this package.

The historical manuscript PDF is **not available in this task environment**. `MANUSCRIPT_CHANGE_REGISTER.md` therefore uses the existing documented discrepancies and marks every paper-specific entry NOT_INDEPENDENTLY_CHECKED_AGAINST_PDF. Original historical AUM/capitalization inputs, ownership evidence and March run vintages remain unrecovered. The package neither edits the original manuscript nor establishes exact March-paper reproduction.

## Figures and verification

- **01_cumulative_wealth (Phase 2):** Compounded daily net simple returns; 100% target cap. NAV 1 immediately before the first OOS return is anchored at the first plotted date. Panel windows differ; BL and 1/N nearly overlap.
- **02_allocation_stability (Phase 2):** ASI derived from actual consecutive 100%-cap rebalance target vectors; first undefined difference excluded. Values agree with Table 2 at displayed precision. Each market uses its own Table 1 OOS window; target ASI is not traded turnover.
- **03_trading_turnover (Phase 2):** 100%-cap primary strategies, common 63-session schedule within each market. L1 target minus drifted pretrade holdings. Initial cash deployment (L1=1) excluded from this mean and reported separately in Table 2. Market-specific windows are given in Table 1.
- **04_matched_concentration (Phase 2):** BL and Markowitz use the same maximum target bound at each point. The 40% constraint is imposed at rebalance, not continuously on drifting holdings. BL's constraint is inactive. Unequal market samples are listed in Table 1; each line is a same-market matched comparison.
- **05_transaction_costs (Phase 2):** 100%-cap principal strategies, all four predefined cost rates. Same gross path and trading decisions across rates. Terminal wealth is distinct from arithmetic annual return in Table 4. Each panel uses its own Table 1 OOS span and y scale; no cross-market common-horizon ranking is implied.
- **06_statistical_uncertainty (Phase 2):** Net 10 bps. Paired 20-session circular blocks, 2,000 iterations, seed 42; percentile 95% intervals, approximate empirical-mean-centered two-sided p-values, unadjusted. Windows/paired counts are those in Tables 1/5. All intervals include zero. Duplicate inactive-cap BL/1N rows are omitted; they remain in Table 5.
- **08_us_factor_exposures (Phase 1):** OLS betas for Phase 1 US net strategies, 2011-01-04–2024-12-31 (3,521 sessions). HAC/Newey–West t statistics and p-values with maxlags 5 are in Table 7. Not a refit of Phase 2 capped/1N paths and not evidence of China/India factor exposure.
- **09_us_tau_sensitivity (Phase 1):** Five verified fixed-tau US runs, 2011-01-04–2024-12-31 (3,521 sessions), net 10 bps. Omega independent of tau. Each point is the source value; no refit/tuning in Phase 3. These are not the adaptive-main-strategy return series.

Every plotted numeric payload is derived from the cited original files; payload hashes, source hashes, annotations and generated figure hashes are recorded in PHASE3_RUN_MANIFEST.json. The checker regenerates the expected tables/payloads, verifies exact table contents to numerical serialization tolerance, checks table/daily/ASI links, checks SVG annotation text and rejects missing/stale/mismatched manifests. PNGs and SVGs use the same plotted data. Visual inspection is performed on the rendered PNGs before delivery.

The four protected historical branches and original paper records remain unchanged. This phase stops at evidence preparation: no manuscript drafting, SSRN upload, merge or automatic next phase is performed.
