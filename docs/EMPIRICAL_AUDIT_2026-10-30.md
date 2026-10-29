# Black–Litterman Audit — Final Verified Public-Data Run (2026-10-30)

**Disposition:** corrected Python diagnostic pipeline and numerical/format checks **PASS**; exact reconstruction of the March 2026 manuscript **NOT ESTABLISHED**. The manuscript and historical `results/paper_results/` files are preserved without modification.

## Execution and numerical status

- Code snapshot: `b278d5ff14db0b4c80e87c1603196af5c7483f2c`.
- [GitHub Actions full empirical validation](https://github.com/amitdudi04/regime-sensitive-black-litterman-tri-market-study/actions/runs/40942721530): **SUCCESS**.
- **35 unit tests passed**, full US/China/India public-data backtests completed, all crisis and tau diagnostics executed, provenance recorded and generated financial-output invariants passed.
- Financial output validation: `internal_consistency = PASS`; paper reproduction `NOT_ESTABLISHED`.
- Paper comparison: **71 numerical cells**: **59 MISMATCH**, **12 INCOMPARABLE_BENCHMARK**, **0 MATCH**. The twelve incomparable cells represent the historical generic/index benchmark rows versus different current ETF proxies, not absent analysis files.
- Results artifact includes 6 strategy rows, 6 crisis rows, 5 tau settings, 6 ex-post regime rows and 3 paired block-bootstrap rows. The three model benchmarks are additional rows in the main summary.
- Exact input price snapshots remain on the CI job only and are not included in Git. The run manifest preserves checksums and provider timestamps. A newer provider pull may produce different source vintage.

## Recomputed 2026-10-30 diagnostic metrics

Simple daily net portfolio returns, arithmetic annualization, zero risk-free rate for Sharpe; initial deployment costs included; target weights allowed to drift between scheduled rebalances.

| Market | Model | Annualized return | Sharpe | Target-weight ASI |
|---|---|---:|---:|---:|
| US | Black–Litterman | 15.4148% | 0.806964 | 0.009410 |
| US | Markowitz | 15.8896% | 0.744401 | 0.805056 |
| China | Black–Litterman | 5.8193% | 0.202377 | 0.001479 |
| China | Markowitz | 4.5276% | 0.149513 | 0.712407 |
| India | Black–Litterman | 10.8720% | 0.503643 | 0.002347 |
| India | Markowitz | 13.2072% | 0.583735 | 0.585261 |

**These are not the manuscript's reported findings.** The original prior/price/weight configurations needed for an exact reconstruction are not in the current repository.

## Supplementary ex-post regime evidence

Markov two-state *smoothed* states are classified with full-sample information and **cannot** be used as point-in-time signals.

| Market | Regime | Sessions | BL Sharpe | Markowitz Sharpe |
|---|---|---:|---:|---:|
| US | Low volatility | 2,368 | 3.084 | 2.636 |
| US | High volatility | 1,153 | -0.700 | -0.751 |
| China | Low volatility | 1,973 | 0.212 | 0.343 |
| China | High volatility | 580 | 0.218 | -0.116 |
| India | Low volatility | 2,810 | 0.739 | 0.817 |
| India | High volatility | 181 | -0.236 | -0.213 |

This newly executed diagnostic **does not** reproduce paper Table 7 or demonstrate causal downside protection.

## New net Sharpe-difference uncertainty

Paired 20-session circular-block bootstrap, 2,000 iterations, seed 42. The displayed two-sided p-values belong to the new BL-minus-Markowitz Sharpe-difference test, **not** the manuscript's volatility or ASI significance tests.

| Market | BL minus Markowitz Sharpe | Two-sided p-value |
|---|---:|---:|
| US | 0.062562 | 0.5370 |
| China | 0.052864 | 0.6915 |
| India | -0.080092 | 0.2735 |

These tests provide no conventional 5% significance evidence for a difference in the revised strategies' aggregate Sharpe ratios.

## Factor, crisis, tau and ownership

- The US factor regression now records a dated aligned Kenneth French input hash, HAC lag, actual observation count, coefficients and t statistics. **Its coefficients do not recover paper Table 5**.
- Crisis analysis records both the historical weighted-log diagnostic and an economically consistent frozen-holdings, no-interim-trades buy-and-hold wealth path. **Neither has been shown to reproduce paper Table 4**.
- Fixed-tau sensitivity is regenerated on the main US out-of-sample window. **Its Sharpe values differ from paper Table 8**.
- The optional ownership module accepts *real individual-stock returns* and *dated SOE/private classifications*, rejects future-only labels and does not fabricate an ETF-level ownership proxy. Original Table 6 classification and test data are not accessible, so no reproduced Table 6 is reported.

## Merge and publication decision

The corrected code, reproducibility metadata, and internal output schemas are test-validated. Exact manuscript replication remains **blocked**, primarily because the historical market-cap/AUM priors, data snapshots, SOE/private constituents and old statistical-test artifacts are not recoverable from the public repository. Manuscript Figure 1, benchmark descriptions, momentum t-statistic sign, statistical-threshold prose and universal downside-protection wording still require a formal paper revision or original evidence.

**Keep PR #5 draft and unmerged. Preserve `main` and original paper CSVs.** Do not present corrected-run diagnostics as published-paper reproductions or rewrite historical observations for numerical agreement.
