# Manuscript-to-Code Reproduction Assessment — 31 October 2026

**Scope:** March 2026 manuscript *Black–Litterman vs. Markowitz: Stability, Turnover, and Crisis Dynamics Across Global Markets* (SSRN 6479462), unchanged historical paper-result CSVs, and the updated public ETF research code.

**Status: March manuscript NOT reproduced; corrected diagnostic study executed successfully.** Do not overwrite the paper's historical tables with a different model's numbers and call it replication.

## Fresh reproducibility evidence

The [31 October 2026 GitHub Actions run](https://github.com/amitdudi04/regime-sensitive-black-litterman-tri-market-study/actions/runs/41205248281) ran the audit-branch research suite (35 tests passed), three-market data pipeline, crisis and tau analyses, paper-vs-generated reconciler, internal output verifier and new manuscript arithmetic check. It generated `paper_arithmetic_audit.csv/json` and all diagnostic result CSVs.

Its report classifies 71 published-table cells as 59 numerical **MISMATCH** and 12 **INCOMPARABLE_BENCHMARK**; no exact matches. The latter means different instrument definitions, not absent results. This applies to paper Tables 2, 4, and 8, not to unarchived source inputs for Tables 5–7.

### Current study compared with the historical paper

| Market | Model | Paper return | Current net annualized return | Paper Sharpe | Current Sharpe | Paper L1 turnover | Current rebalance L1 turnover | Paper ASI | Current ASI |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| US | BL | 12.99% | 15.41% | 0.650 | 0.807 | 0.20% | 2.87% | 0.001632 | 0.009410 |
| US | MV | 13.24% | 15.89% | 0.614 | 0.744 | 1.58% | 80.29% | 0.015365 | 0.805058 |
| China | BL | 1.20% | 5.82% | 0.042 | 0.202 | 0.08% | 3.58% | 0.000391 | 0.001479 |
| China | MV | 2.64% | 4.53% | 0.088 | 0.150 | 1.12% | 70.73% | 0.010772 | 0.712407 |
| India | BL | 7.60% | 10.87% | 0.356 | 0.504 | 0.07% | 1.72% | 0.000322 | 0.002347 |
| India | MV | 9.76% | 13.21% | 0.440 | 0.584 | 0.82% | 58.34% | 0.007822 | 0.585260 |

**Different data effective dates, prior type, portfolio accounting and benchmark definitions mean these values must not be interpreted as a same-experiment validation.** The corrected study uses 2011-01-04–2024-12-31 (US), 2014-11-07–2024-12-31 (China) and 2013-02-13–2024-12-31 (India).

## Material problems discovered within the manuscript itself

### 1. Figure 1 is inconsistent with Table 2 on two separate dimensions

The Figure 1 panels annotate **BL Sharpe US 1.208, China 0.669, India 1.075**. The paper's Table 2 reports **0.650, 0.042, 0.356** respectively. A different calculation or dataset would require explicit documentation.

Figure 1's cumulative wealth curves appear to end at approximately **100–250x in US portfolios, roughly 30x for China BL, and around 14x for India BL**, despite corresponding Table 2 annualized returns of **12.99%, 13.24%, 1.20%, and 7.60%**. The figure labels the wealth paths as starting at one unit. Under standard arithmetic annualization of *simple daily returns*, Jensen's inequality implies a maximum terminal wealth over 3,500 sessions:

`terminal wealth <= (1 + annualized arithmetic mean / 252) ^ 3500`.

This upper bound is about **6.07x for US BL, 6.29x for US Markowitz, 1.18x for China BL, and 2.87x for India BL**. The figure's visibly much larger endings cannot represent those same annualized simple-return series. The manuscript elsewhere refers to continuously compounded returns, but interpreting 12.99% as a log-return rate also yields only around 6x across 3,500 sessions. If the graph is unnormalized, uses percentages as wealth units, different assets, or a different calculation, it must be corrected and fully labeled, not asserted to match Table 2.

Figure 1 also uses approximately 3,500 x-axis trading sessions in the China and India panels despite the late listing dates of ETF constituents in the publicly identified universes.

### 2. Table 3 and Section 10 imply cost drag that does not follow from Table 2 turnover

Under 10 basis points cost per unit of **L1 rebalance turnover**, quarterly rebalancing (252/63=4 rebalances/year), and the *paper Table 2* reported turnover, implied annual trading-cost drag before the initial deployment is:

| Market | Paper BL implied annual cost | Paper MV implied annual cost | Difference |
|---|---:|---:|---:|
| US | 0.080 bps | 0.632 bps | 0.552 bps |
| China | 0.032 bps | 0.448 bps | 0.416 bps |
| India | 0.028 bps | 0.328 bps | 0.300 bps |

The manuscript's **15–30 bps annually** is not supported by those displayed inputs. In the *new* corrected diagnostic, Markowitz mean rebalance turnover is drastically higher (approximately **80.29%, 70.73%, 58.34%**), corresponding to a conditional annualized cost of roughly **32.11, 28.29, 23.34 bps**. The new higher turnover makes the order of magnitude plausible *for the new study*, **not the old published Table 2**. These conditional estimates require confirmation of the paper's actual turnover period, unit and one-way versus L1 convention. A lower trading cost does not alone prove that BL beats MV net of cost; neither the published nor the current table establishes that general claim in all markets.

### 3. Main sampling and historical crisis sampling are separate

The public configuration ends before **2025-01-01**, so it does not include 2025 trading returns. China and India baskets cannot provide a common trading history for all their ETFs from 2010. A US 2008 GFC diagnostic is possible only using a separately requested pre-2010 crisis-history sample. The manuscript's blanket statements about identical 2010–2025 coverage need replacement with actual dates.

### 4. Equilibrium prior is materially different

The paper specifies a market-capitalization-implied equilibrium, while the executable default uses an equal-weight proxy. The branch can accept historical dated capitalization/AUM series but **none of the original dated inputs is available**. This difference affects BL posterior returns, allocation weights, turnover, and every strategy-performance metric.

### 5. US factor results do not support untested China and India momentum claims

The paper attributes China/India Markowitz performance to significant momentum exposure while the documented four-factor regression is **US only**. The historical Table 5 and the updated US factor outputs do not agree: paper **US BL market beta about 0.821 and Markowitz 0.904** versus current **1.064 and 1.148**; paper Markowitz momentum beta **0.115** versus current **0.224**. A US-only factor model cannot formally attribute emerging-market return differences to momentum factors. The manuscript also has a sign inconsistency in the BL momentum t-statistic. Claims of “indistinguishable” betas require a direct test of the difference.

### 6. Drawdown, crisis and recovery language is overstated

Paper Table 2 has *worse* BL maximum drawdown in US and India; its Table 4 recovery time is *slower* for BL in the 2008 US GFC and only marginally faster or equal in China/India. The 31 October corrected pipeline's crisis results differ substantially from the historical tables and include two explicitly different portfolio-return conventions. This does not support universal downside-protection claims.

### 7. Significance and ownership limitations

The manuscript treats p=0.0106 as significant at the 1% level, but it is **not**. Its Chinese SOE/private p=0.572 supports a failure to reject the null, not evidence of equivalence or proven absence of an ownership effect. The manuscript's ownership statement about crisis recovery in India and the US is not backed by the Chinese stock-level SOE experiment. The original stock-level ownership labels, constituent return histories and test artifacts are missing. The updated helper does not recreate them.

### 8. Low instability is partly a feature of the design

The BL prior defaults to equal weights and the investor views are a small tilt toward historical means. Near-equal, persistent target weights are thus unsurprising; the comparator is an unconstrained historical-mean Markowitz optimizer that may put nearly 100% into one ETF. This is a meaningful *specific comparator result*, not proof that Bayesian updating is superior to equal weighting or other stabilized alternatives. A **passive equal-weight portfolio** and at least one regularized or constrained Markowitz comparator should be included in a future prespecified sensitivity study, not silently incorporated into a claim about the original paper.

## What to publish / defend

**Recommended choice:** create an explicitly labeled **revised manuscript v2 based on the fresh corrected-pipeline study**, preserve the earlier SSRN manuscript and historical CSVs, and regenerate all v2 tables/figures directly from one frozen data snapshot and script commit. Record the dataset hashes, actual dividend-adjustment field, market windows and benchmark instruments; add equal-weight baseline and realistic sensitivity analyses **before freezing v2**. Separate descriptive regimes from ex-ante trading. Downgrade non-significant Sharpe, SOE and causal claims. Cite remaining input-provenance limits.

**Not recommended:** changing the original historical CSVs until they numerically match the executable output while presenting the altered values as a reproduction of March 2026. This would lose provenance and misrepresent a model-specification change as an arithmetic correction.

**Research status:** fully executable and internally validated **new diagnostic implementation**; incomplete independently reproducible *historical* research; original manuscript needs a formal correction/replacement with traceable empirical evidence.
