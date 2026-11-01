# Phase 2 results — Essential research experiments

**Status: COMPLETE; READY_WITH_LIMITATIONS to freeze these Phase 2 results for a revised manuscript.** All requested experiments executed successfully with the verified frozen Phase 1 price inputs. No fresh market or factor data were downloaded. No manuscript was edited.

The main new finding is that this equilibrium-anchored BL implementation behaves almost like periodically rebalanced 1/N. Its performance advantage over 1/N is not established. The predefined 40% target cap substantially reduces Markowitz concentration and turnover and narrows BL–Markowitz Sharpe differences in the US and China. No reported paired Sharpe comparison is significant at the unadjusted 5% level; every 95% percentile interval includes zero. These are results to preserve, not targets to optimize away.

## 1. Exact definitions and repository safety

- Base branch: `research/revised-paper-phase1-validation`, SHA `598fe0d3c0a7cd7ebaf5709ae62b7c6735b92a0d`.
- Dedicated branch: `research/revised-paper-phase2-experiments`.
- Executed Phase 2 implementation commit: `af84ddfbc93edc7a5143c654d6319d67e3139eef`, clean working tree at execution. A subsequent documentation/result snapshot commit records these outputs without changing runtime calculations; its final SHA is given in delivery.
- Protected `main` remains `1a82c7599029eb305e60b355b90ac7b80966126f`; original audit remains `77f77d8c6e4fe90d9e81091309fe55d9ce0978ae`; Phase 1 remains the base SHA above. No protected branch, historical paper CSV, original manuscript or unrelated repository was modified. No forced history rewrite, merge or auto-merge was performed.
- Same US/China/India USD-listed ETF universes, aligned main OOS dates, 252-session training and 63-session rebalance schedule, Ledoit–Wolf covariance, risk aversion 3, BL prior/views/tau rules and Phase 1 financial accounting. No verified Phase 1 numerical module was edited.
- **Equal-weight:** targets reset to 1/N at the identical initial deployment and each scheduled rebalance. Holdings drift between trades. A zero target ASI does not imply zero traded turnover: rebalancing offsets price drift.
- **Matched concentration:** maximum target weight 100% versus predefined 40%, applied to both BL and Markowitz with otherwise identical inputs/constraints. Feasible: 5×.4=2 for US and 4×.4=1.6 for China/India, exceeding required full investment. The cap is imposed on targets at trades, not continuously on drifting holdings.
- **Costs:** 0, 5, 10, 20 bps per unit of the existing L1 turnover, including initial cash deployment. `1+r_net=(1+r_gross)*(1−turnover*bps/10000)` on trade dates; no additional daily trades. Exactly two Phase 1 optimizer backtests per market—one per cap—produce common gross paths and trading decisions. All cost rates reuse those paths. Equal-weight uses the same Phase 1 drift, turnover and holding-return helpers.
- **Reported metrics:** arithmetic daily mean×252, sample volatility×sqrt(252), zero-RF Sharpe, drawdown including initial NAV 1, ASI excluding the initial undefined target difference, and drift-adjusted L1 rebalance turnover excluding initial deployment. Every initial deployment has turnover 1 and costs exactly the scenario bps. Terminal NAV is compounded wealth, not arithmetic annualized return.
- **Concentration:** target maximum and mean target HHI (sum squared weights) are recorded along with maximum end-of-day holding weight and mean end-of-day HHI. Holdings can drift above 40% after a valid capped trade; that does not violate the predefined target constraint.
- **Inference:** Phase 1 paired circular bootstrap, block size 20 sessions, 2,000 iterations, seed 42; BL−Markowitz and BL−1/N at 10 bps using identical complete OOS dates. Both cap scenarios are reported. P-values retain Phase 1 empirical-bootstrap-mean centering; intervals are 95% percentile bootstrap intervals. No additional testing framework or multiplicity adjustment was introduced.

## 2. Data windows and provenance

| Market | Start | End | Sessions | ETFs |
| --- | --- | --- | --- | --- |
| US | 2011-01-04 | 2024-12-31 | 3521 | 5 |
| China | 2014-11-07 | 2024-12-31 | 2553 | 4 |
| India | 2013-02-13 | 2024-12-31 | 2991 | 4 |

The prices match the SHA-256 values archived in Phase 1:

| Market | Frozen price SHA-256 |
| --- | --- |
| US | 835a01e377ce0c50c1cdeb7b5ad8653680f83ee4c7c5b6158fcc2f8d0c0fdfc9 |
| China | 9db82332709b7fd366b96461b32d474ecd509383121edb9ed8f3ad677dd3b4a1 |
| India | 655f98c5bfae2a37da7809a51e80249f4853beaac5db2ac5ffe8f1c1a8af5bb2 |

Requests, provider `Adj Close (auto_adjust=False)` definition, dividend/split adjustment, retrieval timestamps, ticker order and alignment metadata are preserved inside `PHASE2_RUN_MANIFEST.json`. China/India results represent USD-listed ETF exposure, not pure local-currency national returns. Requested main data end before 2025-01-01. The common effective starts differ because of ETF availability; no missing early history was fabricated.

The new loader fails explicitly on missing or mismatched frozen snapshots and has no download fallback. Current inputs are the disclosed Phase 1 vintage, not a reconstruction of the March manuscript's raw inputs.

## 3. BL, Markowitz and 1/N at 10 bps

All rows in this table have maximum target bound 100%; 1/N targets remain 20% in US and 25% in China/India.

| Market | Strategy | Net annual return | Net volatility | Sharpe | MDD | ASI | Rebalance L1 | Terminal NAV |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US | Black-Litterman | 15.4148% | 19.1023% | 0.806964 | -35.0693% | 0.009409 | 2.8735% | 6.6680 |
| US | Markowitz | 15.8896% | 21.3455% | 0.744400 | -31.1532% | 0.805060 | 80.2868% | 6.6878 |
| US | Equal-weight | 15.4183% | 19.0911% | 0.807620 | -35.0716% | 0.000000 | 2.6123% | 6.6732 |
| China | Black-Litterman | 5.8193% | 28.7549% | 0.202377 | -64.2506% | 0.001479 | 3.5751% | 1.1893 |
| China | Markowitz | 4.5276% | 30.2822% | 0.149513 | -65.2639% | 0.712407 | 70.7290% | 0.9950 |
| China | Equal-weight | 5.8210% | 28.7625% | 0.202381 | -64.2611% | 0.000000 | 3.5848% | 1.1893 |
| India | Black-Litterman | 10.8720% | 21.5867% | 0.503642 | -49.7382% | 0.002346 | 1.7249% | 2.7502 |
| India | Markowitz | 13.2072% | 22.6253% | 0.583735 | -47.5871% | 0.585259 | 58.3411% | 3.5308 |
| India | Equal-weight | 10.8700% | 21.5862% | 0.503564 | -49.7414% | 0.000000 | 1.7618% | 2.7496 |

BL's net annual arithmetic return differs from 1/N by approximately −0.348 bps in the US, −0.166 bps in China and +0.194 bps in India. Its corresponding Sharpe differences are −0.000656, −0.000004 and +0.000079. These small differences do not establish additional economic value from BL updating beyond this simple rebalanced benchmark.

BL has higher descriptive Sharpe than unrestricted Markowitz in the US and China, but lower Sharpe in India. Markowitz has higher arithmetic net annual return in the US and India; BL has higher return in China. BL does not universally reduce drawdown: its US and India MDD is worse than unrestricted Markowitz. Equal-weight has lower US turnover than BL; BL's China/India turnover is only marginally lower than 1/N. Lower BL trading costs versus Markowitz therefore do not imply a general superiority over 1/N.

The original six Phase 1 model headline rows at 10 bps match the Phase 2 primary rows within 1e-12 across return, volatility, Sharpe, drawdown, ASI and turnover (observed maximum difference: 0.0). No Phase 1 re-audit or old full empirical workflow was rerun to obtain this comparison.

## 4. Matched 40% concentration comparison at 10 bps

| Market | Strategy | Target cap | Net return | Sharpe | MDD | ASI | Rebalance L1 | Target max | Target HHI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US | Black-Litterman | 100.0000% | 15.4148% | 0.806964 | -35.0693% | 0.009409 | 2.8735% | 20.9875% | 0.200054 |
| US | Markowitz | 100.0000% | 15.8896% | 0.744400 | -31.1532% | 0.805060 | 80.2868% | 100.0000% | 0.877790 |
| US | Black-Litterman | 40.0000% | 15.4148% | 0.806964 | -35.0693% | 0.009409 | 2.8735% | 20.9875% | 0.200054 |
| US | Markowitz | 40.0000% | 15.7193% | 0.797938 | -32.0288% | 0.409051 | 41.4349% | 40.0000% | 0.358195 |
| China | Black-Litterman | 100.0000% | 5.8193% | 0.202377 | -64.2506% | 0.001479 | 3.5751% | 25.3056% | 0.250002 |
| China | Markowitz | 100.0000% | 4.5276% | 0.149513 | -65.2639% | 0.712407 | 70.7290% | 100.0000% | 0.884217 |
| China | Black-Litterman | 40.0000% | 5.8193% | 0.202377 | -64.2506% | 0.001479 | 3.5751% | 25.3056% | 0.250002 |
| China | Markowitz | 40.0000% | 5.3984% | 0.194447 | -63.1135% | 0.351323 | 35.7818% | 40.0000% | 0.353842 |
| India | Black-Litterman | 100.0000% | 10.8720% | 0.503642 | -49.7382% | 0.002346 | 1.7249% | 25.3062% | 0.250003 |
| India | Markowitz | 100.0000% | 13.2072% | 0.583735 | -47.5871% | 0.585259 | 58.3411% | 100.0000% | 0.875524 |
| India | Black-Litterman | 40.0000% | 10.8720% | 0.503642 | -49.7382% | 0.002346 | 1.7249% | 25.3062% | 0.250003 |
| India | Markowitz | 40.0000% | 12.1747% | 0.555011 | -47.1920% | 0.263175 | 26.9045% | 40.0000% | 0.358635 |

For Markowitz, mean target HHI falls from approximately .878/.884/.876 to .358/.354/.359 in US/China/India. Average L1 rebalance turnover falls from 80.29%/70.73%/58.34% to 41.43%/35.78%/26.90%. The predefined cap lowers concentration and trading activity substantially but does not create a universal return or Sharpe improvement: US/China Sharpe rises to .797938/.194447, while India Sharpe falls to .555011.

The cap is inactive for BL in the realized samples, so BL's capped and unrestricted gross/net paths are identical. The relevant matched comparisons are capped BL versus capped Markowitz; capped Markowitz is not presented as having the same constraints as unrestricted BL. With matched caps, BL−Markowitz Sharpe gaps become .009026 (US), .007930 (China), and −.051369 (India). None is statistically significant under the retained test.

## 5. Transaction-cost sensitivity

Primary strategies, 100% target bound; annual arithmetic returns:

| Market | Strategy | Gross annual return | 0 bps net | 5 bps net | 10 bps net | 20 bps net |
| --- | --- | --- | --- | --- | --- | --- |
| US | Black-Litterman | 15.4334% | 15.4334% | 15.4241% | 15.4148% | 15.3963% |
| US | Markowitz | 16.2137% | 16.2137% | 16.0517% | 15.8896% | 15.5654% |
| US | Equal-weight | 15.4358% | 15.4358% | 15.4271% | 15.4183% | 15.4009% |
| China | Black-Litterman | 5.8433% | 5.8433% | 5.8313% | 5.8193% | 5.7953% |
| China | Markowitz | 4.8185% | 4.8185% | 4.6730% | 4.5276% | 4.2367% |
| China | Equal-weight | 5.8450% | 5.8450% | 5.8330% | 5.8210% | 5.7969% |
| India | Black-Litterman | 10.8872% | 10.8872% | 10.8796% | 10.8720% | 10.8567% |
| India | Markowitz | 13.4475% | 13.4475% | 13.3274% | 13.2072% | 12.9668% |
| India | Equal-weight | 10.8854% | 10.8854% | 10.8777% | 10.8700% | 10.8546% |

Net compounded terminal wealth from initial NAV 1:

| Market | Strategy | 0 bps NAV | 5 bps NAV | 10 bps NAV | 20 bps NAV |
| --- | --- | --- | --- | --- | --- |
| US | Black-Litterman | 6.6852 | 6.6766 | 6.6680 | 6.6508 |
| US | Markowitz | 6.9969 | 6.8407 | 6.6878 | 6.3918 |
| US | Equal-weight | 6.6895 | 6.6814 | 6.6732 | 6.6570 |
| China | Black-Litterman | 1.1922 | 1.1908 | 1.1893 | 1.1864 |
| China | Markowitz | 1.0246 | 1.0097 | 0.9950 | 0.9662 |
| China | Equal-weight | 1.1922 | 1.1907 | 1.1893 | 1.1864 |
| India | Black-Litterman | 2.7552 | 2.7527 | 2.7502 | 2.7452 |
| India | Markowitz | 3.6326 | 3.5813 | 3.5308 | 3.4316 |
| India | Equal-weight | 2.7546 | 2.7521 | 2.7496 | 2.7446 |

Direct modeled fees in units of initial NAV, accumulated over the full market-specific sample:

| Market | Strategy | 0 bps costs / initial NAV | 5 bps costs / initial NAV | 10 bps costs / initial NAV | 20 bps costs / initial NAV |
| --- | --- | --- | --- | --- | --- |
| US | Black-Litterman | 0.000000 | 0.002726 | 0.005447 | 0.010877 |
| US | Markowitz | 0.000000 | 0.068525 | 0.135064 | 0.262378 |
| US | Equal-weight | 0.000000 | 0.002568 | 0.005131 | 0.010247 |
| China | Black-Litterman | 0.000000 | 0.001444 | 0.002886 | 0.005766 |
| China | Markowitz | 0.000000 | 0.016250 | 0.032277 | 0.063671 |
| China | Equal-weight | 0.000000 | 0.001447 | 0.002893 | 0.005779 |
| India | Black-Litterman | 0.000000 | 0.001108 | 0.002216 | 0.004428 |
| India | Markowitz | 0.000000 | 0.029079 | 0.057674 | 0.113440 |
| India | Equal-weight | 0.000000 | 0.001120 | 0.002239 | 0.004474 |

The CSV includes gross return, net return, net volatility/Sharpe, turnover, direct fees and terminal NAV at all four rates for both optimized constraint scenarios and 1/N (60 rows). Gross paths, target weights, ASI and turnover are unchanged when only costs change. Zero-cost net returns equal gross; higher positive rates reduce terminal wealth for every unchanged path. The cap scenarios are additional rows in the same cost table, not a new cap search.

Direct costs are `sum(pretrade net NAV * fee_fraction)`, expressed relative to initial NAV. They are not an annual cost percentage, a sum of trade-date NAV fractions, or the gross-minus-net terminal wealth difference, which also reflects investment growth forgone. No brokerage-dollar implicit fee-funding model, bid/ask spread or market-impact model was added.

Cost savings alone do not determine net performance. At 20 bps, unrestricted US Markowitz still has higher arithmetic annual return than BL (15.5654% versus 15.3963%), but BL has higher terminal NAV (6.6508 versus 6.3918). Volatility and compounding make those rankings different. At the same cost rate, India Markowitz remains ahead of BL on both measures. China Markowitz can have positive arithmetic annualized mean yet terminal NAV below 1; these metrics must not be interchanged.

## 6. Paired statistical uncertainty at 10 bps

| Market | Target cap | Comparison | Sharpe difference | 95% percentile CI | p-value |
| --- | --- | --- | --- | --- | --- |
| US | 100.0000% | BL − Markowitz | 0.062564 | [-0.136167, 0.277879] | 0.5370 |
| US | 100.0000% | BL − Equal-weight | -0.000656 | [-0.001556, 0.000285] | 0.1725 |
| US | 40.0000% | BL − Markowitz | 0.009026 | [-0.107492, 0.141051] | 0.8905 |
| China | 100.0000% | BL − Markowitz | 0.052864 | [-0.215295, 0.320003] | 0.6915 |
| China | 100.0000% | BL − Equal-weight | -0.000004 | [-0.000377, 0.000382] | 0.9835 |
| China | 40.0000% | BL − Markowitz | 0.007930 | [-0.091777, 0.100244] | 0.8725 |
| India | 100.0000% | BL − Markowitz | -0.080092 | [-0.213058, 0.064457] | 0.2735 |
| India | 100.0000% | BL − Equal-weight | 0.000079 | [-0.000176, 0.000304] | 0.5070 |
| India | 40.0000% | BL − Markowitz | -0.051369 | [-0.113396, 0.013004] | 0.1110 |

All p-values exceed .05 and all intervals include zero. The complete CSV contains 12 scenario rows; the three capped BL−1/N rows duplicate the unrestricted BL−1/N results because the BL cap is inactive, so they do not constitute independent corroborating evidence. The table above lists the six primary comparisons plus three distinct matched-cap BL−Markowitz comparisons.

The conclusion is failure to establish a Sharpe difference under this finite-sample approximate bootstrap, not proof of equivalence or equal future performance. The retained empirical-mean-centered test and percentile intervals are approximate; reported p-values are unadjusted across comparisons. Sample lengths differ by market, the ETF baskets are small and overlapping, and model costs are stylized. This is not the manuscript's original volatility or ASI hypothesis test and does not demonstrate causal regime protection or international factor attribution.

## 7. Tests, execution and output validation

- Local full suite: `python -m unittest discover -s tests -v` executed once after implementation: **80 passed, zero failures/skips** (71 unchanged existing tests plus 9 focused Phase 2 tests).
- New tests cover equal-weight drift/rebalancing, exact gross wealth and multiplicative costs, cost path reuse, identical matched optimizer configuration and feasibility, target versus drifted concentration, Phase 1 net-path compatibility, strict paired-date alignment, missing frozen-input failure and cross-table consistency. A tampered summary with an updated fingerprint still fails the consistency check.
- Committed clean-source execution: `python -m pipelines.phase2_experiments` completed US/China/India and every requested experiment; no factor retrieval, regime refit or old Phase 1 empirical audit was invoked.
- Explicit output check: `python -m scripts.validate_phase2_outputs` passed. Expected rows: 9 primary strategy, 12 concentration, 60 cost and 12 statistical. The checker reconstructs fixed-holding wealth from frozen asset returns and saved target decisions, verifies drift turnover, cost factors and cap bounds, reconciles all summary metrics and confirms identical paired samples.
- Implementation-commit CI: [80-test research workflow](https://github.com/amitdudi04/regime-sensitive-black-litterman-tri-market-study/actions/runs/41213360522), SUCCESS. Final report-commit CI is checked separately in delivery; the old full Phase 1 workflow is not enabled on this branch.
- A completed output directory is never silently overwritten. To rerun, select a new output directory, e.g. `python -m pipelines.phase2_experiments --output-dir results/generated/phase2_repeat`, retaining the same verified Phase 1 snapshots.

## 8. Deliverables, readiness and limits

Versioned snapshot: `results/phase2_results/` contains the four required CSVs, `PHASE2_RUN_MANIFEST.json` and `PHASE2_OUTPUT_VALIDATION.json`. Full daily gross/four-cost net paths and trading decisions are retained locally under `results/generated/phase2/` and included in the user-facing evidence package. No raw provider prices or factor values are redistributed. The completed run has ID `ff8cacdc-95f8-458e-8d71-d12efbd9a9f9`; its manifest records the actual executed Phase 2 commit, frozen inputs, complete configuration, source/output hashes, environment and calculation definitions. Later report-only commits do not retroactively relabel the executed code SHA.

Files changed are limited to the new experiment runner, new output checker, new focused tests, unit-CI branch/path support, this report and the small result snapshot. Existing Phase 1 financial code, configuration, manuscript and historical results are unchanged. README was not redesigned.

**Freeze decision: READY_WITH_LIMITATIONS.** All four requested experiments are complete and checked; no experiment is blocked. These outputs can be frozen as the specified revised-study empirical record. They support a narrower claim: relative to unrestricted historical-mean Markowitz, BL stabilizes targets and reduces modeled turnover; rebalanced 1/N delivers nearly the same investment outcomes, and a reasonable matched concentration cap materially narrows the Sharpe contrast. A general BL advantage beyond 1/N, statistically significant Sharpe outperformance or universal downside protection is not established.

Keep the original March manuscript and its numerical records separate. Exact historical-paper reproduction is still unestablished because original vintages and priors are missing. Retain the frozen local snapshots under applicable provider terms; a checksum cannot guarantee a later fresh download reproduces that vintage. No manuscript editing, SSRN submission, additional countries/models, cap tuning, ownership reconstruction or subsequent phase was undertaken.
