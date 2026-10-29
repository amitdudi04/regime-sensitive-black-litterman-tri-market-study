# Finance Committee Review: Correction Register and Manuscript Errata

This register is for the March 2026 manuscript, *Black–Litterman vs. Markowitz: Stability, Turnover, and Crisis Dynamics Across Global Markets*. It distinguishes corrected code from historically published figures. It does **not** constitute a rewritten manuscript, a data release, or a claim of numerical replication.

## A. Computational corrections on the audit branch

| Issue | Current branch treatment | Validation | Implication |
|---|---|---|---|
| Daily holding-period accounting | Daily simple-return buy-and-hold performance now uses naturally drifting weights, rather than a constant target allocation at each day's close | Synthetic deterministic wealth test and CI | Older 2026-10-13 diagnostics are stale |
| Initial investment and rebalance friction | Initial deployment is charged; costs reduce available wealth multiplicatively before the next return; non-initial turnover uses drift-adjusted holdings | Unit tests and CI | Net returns and Sharpe must be recomputed |
| ASI first observation | Excludes the undefined initial weight difference rather than counting it as zero | Hand-calculated ASI test | Historical paper ASI is not thereby verified |
| Historical equilibrium priors | Static or dated ex-ante prior vectors are supported; dated rows are selected strictly as-of the preceding training cutoff. Invalid priors fail validation; a prior history is saved per market. | Synthetic chronology and invalid-prior tests | The default remains equal-weight because historical AUM snapshots are not in the repository |
| Crisis and fixed-tau generators | Existing PR #5 implements separate generators and metadata. A second buy-and-hold crisis path now uses self-financing frozen holdings and includes the first event return; the weighted-log historical diagnostic is retained separately. | Synthetic tests plus full public-data GitHub Actions diagnostics | Both definitions differ from the paper values and require formal interpretation |
| Price provenance | Existing PR #5 stores local checksum-verified snapshots and effective date manifests | Cache-integrity tests | Snapshots are Git-ignored and are not reconstructable from Git alone |
| Paper comparison | `python -m scripts.verify_paper_results` checks every numeric cell in the three tracked paper-result CSVs against freshly generated results | Missing-data, mismatch, duplicate-key tests | A match proves numerical agreement only, not method provenance |

## B. Manuscript corrections requiring a **formal paper revision**

1. **Central prior definition.** Manuscript states a capitalization-implied equilibrium. The code defaults to equal ETF weights. Either recover the original dated market capitalization/AUM inputs and rerun, or revise the manuscript to identify the actual equal-weight proxy. Do not imply the two are mathematically equivalent.
2. **Time coverage.** The requested main analysis ends on **2024-12-31**, due to the exclusive 2025-01-01 end. The China four-ETF common history begins in **November 2013** and India's in **February 2012** in the previous diagnostic. A uniform 2010–2025 effective history for all baskets is unsupported. The 2008 crisis uses a distinct pre-2010 sample and must be described separately.
3. **Figure 1 versus Table 2.** Figure 1's figure-level Sharpe annotations are inconsistent with Table 2's quoted Sharpe ratios. Reconstruct the figure from verified outputs, label the exact window and conventions, or explicitly identify the different calculation if justified.
4. **Downside-protection overstatement.** In Table 2, Black–Litterman has **worse** maximum drawdown than Markowitz in the US (-38.04% versus -33.95%) and India (-53.67% versus -50.07%). Claim lower target-weight instability, not universal drawdown superiority.
5. **Gross/net and benchmark definitions.** The manuscript describes a capitalization-weighted ETF benchmark but historical rows use index-style comparisons; the corrected diagnostics use ETF proxies SPY, ASHR and INDA. These are not interchangeable. Distinguish gross and net returns as well as percentage versus fraction turnover and absolute L1 turnover versus one-way traded notional.
6. **Factor regression inconsistency.** The published table and narrative have opposite signs for the Black–Litterman momentum t statistic (approximately +0.856 versus -0.856). Confirm against an original regression artifact rather than guessing which is correct. Save factor data vintage, sample dates and HAC lags.
7. **Statistical significance.** The reported volatility-suppression p = 0.0106 is significant at 5% but **not 1%**; the ASI p = 0.0046 is significant at 1%. An exact bootstrap rerun requires archived inputs, test statistic, resampling unit, block length, number of resamples and random seed. A new paired daily circular-block bootstrap of BL-minus-Markowitz Sharpe is generated with explicit block length, seed and iterations; this is a NEW inference exercise and not the original volatility or ASI hypothesis test.
8. **Regime inference.** Markov **smoothed** probabilities use information from the complete series and are appropriate for ex-post description. Do not interpret them as real-time signals or a proven causal mechanism without filtered, ex-ante evaluation. The new `analysis/supplementary_diagnostics.py` generates a separately labeled ex-post regime table and date-level classifications; it is not evidence that original Table 7 has been reproduced.
9. **SOE/private hypothesis.** The reported ownership comparison p = 0.572 does not support a statistically established difference. A complete implementation needs dated classifications, constituent histories, returns, costs and the stated test.
10. **Crisis convention.** A weighted sum of asset log returns with frozen constant *weights* describes a constant-mix-style diagnostic, not a no-trade buy-and-hold wealth path. The paper's frozen-weight wording and actual financial mechanics must be reconciled. The diagnostic is retained separately for provenance, not claimed equivalent to the corrected main portfolio account.

## C. Outputs and decision criteria

After running `python -m pipelines.run_tri_market_pipeline`, run:

```bash
python -m scripts.verify_paper_results
```

The resulting `results/generated/paper_reconciliation.csv` records `MATCH`, `MISMATCH` and `MISSING` for paper reference cells, including differences. `results/generated/paper_reconciliation.json` supplies a machine-readable summary. Use `--strict` to return failure unless every compared cell matches. Do **not** set `--strict` as a routine pipeline gate before resolving known method differences: failures are expected and academically informative.

GitHub Actions `Empirical reproduction audit` attempts the entire diagnostic and publishes **summary outputs only**, not third-party raw price snapshots, as a temporary workflow artifact.

**Final acceptance remains blocked** until: (i) the intended prior and main/crisis return conventions are academically specified, (ii) the exact source data and weights are recovered or the missing provenance is explicitly acknowledged, (iii) all data-dependent results are regenerated, (iv) every mismatch is explained or corrected in a formally revised paper, and (v) no unsupported statistical claim remains. A passing unit-test workflow alone is insufficient.
