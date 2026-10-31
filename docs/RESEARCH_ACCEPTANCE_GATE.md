# Reproducibility Status and Research Limitations

**Scope:** the March 2026 SSRN research record versus the corrected public tri-market Python implementation. **The historical manuscript is preserved**. This document defines what *can* be verified and what remains blocked by missing evidence.

## 1. Corrected and automatically checked

| Component | Implementation / evidence | Outcome |
|---|---|---|
| Chronological OOS backtest | 252 sessions of training, 63-session rebalance | Automated chronology tests |
| Daily portfolio wealth | Self-financing buy-and-hold weights between rebalances | Exact two-asset wealth test |
| Initial investment and trading friction | Cost deducted multiplicatively from wealth at the trade | Cost-accounting tests |
| Turnover and ASI | Turnover from drift-adjusted pretrade holdings; ASI from consecutive target vectors with first null difference excluded | Numeric tests |
| Capitalization-equilibrium inputs | Static or dated user-supplied prior, as-of selected before rebalance training cutoff; default equal-weight **proxy** | Chronology and invalid-prior tests; as-of histories |
| Crisis exposure | Paper-convention weighted-log diagnostic and a separately named no-trade buy-and-hold crisis path | Synthetic stress tests |
| Sample, price, benchmark evidence | Effective dates, provider retrieval metadata, hashes, provider-specific passive ETF proxy labels | Generated manifests and cache tests |
| Factor regression | US Kenneth French aligned daily factors, excess returns, HAC SE, exact factor-data hash and sample dates | Generated regression and provenance metadata |
| Regime classification | Two-state **smoothed** probabilities for ex-post description only | Per-market sample partition and state table |
| Resampling | Paired circular-block bootstrap of annualized BL-minus-Markowitz Sharpe | Generated per-market p-values with seed, block and count |
| Ownership comparison | Optional source-backed daily gross descriptive diagnostics require contemporaneously available stock-level SOE/private classification | Positive and fail-closed input tests; no fabricated ownership dataset |
| Numerical audit | Historical performance, crisis, and tau reference cells are compared with **generated** results | MATCH, MISMATCH, MISSING or INCOMPARABLE_BENCHMARK |
| Artifact validation | Output schema, strategy counts, finances, dated prior manifests, factor provenance, regime coverage, and reconciliation flags | `python -m scripts.validate_generated_outputs` |

## 2. Corrected data-dependent evidence

The latest complete reproducible public-data execution is **not the original paper release**. Distinct source inputs, prior and benchmark definitions prevent an assumption of numeric equivalence.

- US revised BL annual return approximately **15.41%**, Sharpe approximately **0.807**, versus manuscript 12.99% and 0.650.
- China revised BL annual return approximately **5.82%**, Sharpe approximately **0.202**, versus manuscript 1.20% and 0.042.
- India revised BL annual return approximately **10.87%**, Sharpe approximately **0.504**, versus manuscript 7.60% and 0.356.
- Revised factor regression coefficients differ from manuscript Table 5; revised tau results differ from manuscript Table 8.
- Revision has ex-post regime and block-bootstrap diagnostics for each market, but these are **not a recovery of Table 7 or Section 13 historical tests**.

The generated paper comparison intentionally treats the three historical benchmark rows as *not directly comparable* with the present SPY/ASHR/INDA ETF-proxy benchmark definitions. A different benchmark is not a missing output.

## 3. Original paper evidence that cannot be reconstructed from current public Git

1. Exact historical, as-of market-capitalization/AUM weights used to construct the claimed equilibrium prior.
2. Original frozen adjusted-price snapshots, original optimizer weights, actual return/turnover frequency conventions and data-vintage checksums.
3. Original pre-2008 constituent history needed to verify the manuscript's 2008 crisis recovery calculation under identical specifications.
4. Original non-ETF Chinese SOE/private ownership classifications, constituent daily returns and trading-cost/test inputs. The project ETF basket is not an adequate substitute for this stock-level comparison.
5. Historical regime-state classifications, estimation sample and Table 7 source outputs.
6. Original factor-model inputs and data vintage used for Table 5, plus its inconsistent momentum t-statistic sign.
7. Historical block-bootstrap test samples, statistics, block size and seed for volatility and ASI p-values.
8. Figure 1 Sharpe-annotation definitions and original plotting data, which do not reconcile with Table 2.

## 4. Paper statements requiring a formal corrigendum or revised manuscript

- Do not claim market-cap implied equilibrium weights when the analysis defaults to equal weights.
- Do not claim uniform effective 2010–2025 ETF coverage.
- Do not call Markov smoothed ex-post states a live trading signal.
- Do not claim universal Black–Litterman drawdown superiority; in paper Table 2 the US and India BL maximum drawdowns are worse than Markowitz.
- The paper's p = 0.0106 is significant at 5% but not 1%. The paper's p = 0.0046 is significant at 1%.
- Do not say SOE/private outperformance was established from p = 0.572.
- Correct Figure 1 versus Table 2 Sharpe annotations, factor t-statistic sign and descriptions of gross/net P&L and benchmark instruments.

## 5. Reproducibility status

**Software and auditability:** can pass when unit CI, full pipeline and generated output validation pass.

**New revised research study:** can be reported under fully declared equal-weight, benchmark and sample conventions, while retaining caveats about short ETF baskets and ex-post inference.

**Exact reproduction of the March 2026 manuscript:** **BLOCKED BY MISSING ORIGINAL EMPIRICAL INPUTS AND INCOMPATIBLE METHODOLOGY**. No optimizer parameter is tuned to force agreement, no published table is overwritten, and a passing workflow does not overturn this status.

**Publication and branch distinction:** the corrected implementation can be assessed independently from the March manuscript. Changes to the public default branch should be made only with a clear version label and preserved paper-reference files; code validation alone cannot resolve manuscript evidence gaps.
