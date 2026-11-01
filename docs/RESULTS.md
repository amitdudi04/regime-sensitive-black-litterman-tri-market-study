# Revised research results

| Market | Strategy | Net annual return | Sharpe | Max drawdown | Mean L1 turnover | ASI |
|---|---|---:|---:|---:|---:|---:|
|US|BL|15.4148%|0.806964|-35.0693%|2.8735%|0.009409|
|US|Markowitz|15.8896%|0.744400|-31.1532%|80.2868%|0.805060|
|US|1/N|15.4183%|0.807620|-35.0716%|2.6123%|0.000000|
|China|BL|5.8193%|0.202377|-64.2506%|3.5751%|0.001479|
|China|Markowitz|4.5276%|0.149513|-65.2639%|70.7290%|0.712407|
|China|1/N|5.8210%|0.202381|-64.2611%|3.5848%|0.000000|
|India|BL|10.8720%|0.503642|-49.7382%|1.7249%|0.002346|
|India|Markowitz|13.2072%|0.583735|-47.5871%|58.3411%|0.585259|
|India|1/N|10.8700%|0.503564|-49.7414%|1.7618%|0.000000|

Principal values: [frozen CSV](../results/phase3_final/table_02_principal_performance.csv). Net 10 bps/L1; arithmetic annual means and zero-RF Sharpe. Turnover excludes separately charged deployment.

## Supplementary findings

Status: RESEARCH_READY_WITH_LIMITATIONS. Author and SSRN/AI-policy clearance remain pending.

1. BL remains extremely close to rebalanced 1/N because of the equal-weight reverse-optimized prior, mild historically generated views and large Omega. Mean absolute active ETF weights are .001828 US, .000426 China and .000558 India; marginal Omega/prior ratios are 200–1,000. No incremental Bayesian alpha is established.
2. Matched 40% target constraints reduce Markowitz concentration and turnover. The specification was introduced in Phase 2 before its recorded execution, without evidence of preregistration. Historical values are unchanged.
3. New exploratory paired decision-block ASI/turnover intervals are negative for BL-minus-Markowitz under both caps. Small decision samples and serial dependence limit inference; unadjusted Monte Carlo p=0 means zero exceedances in finite draws, not a true probability of zero. BL has nonzero ASI versus constant targets, and comparison with 1/N does not establish general turnover superiority.
4. All Sharpe intervals include zero at daily block lengths 10,20,40; minimum approximate p=.102. Failure to reject is not equivalence.
5. Six conditional crisis paths reconcile existing investment summaries. The original archived weight vectors exist, but missing crisis target-selection timelines prevent full independent reproduction of pre-event selection. US crisis evidence remains unfavorable to BL; no missing vectors invented.
6. Independent US OLS/Bartlett HAC calculations reproduce archived coefficients, t-statistics and R2. BL's high fit and market t-value are reproduced, with positive residual variance; same-sample 1/N is a new supplementary diagnostic. No China/India factor conclusions follow.
7. Five fixed-tau values remain unchanged; tau does not cancel because Omega is independent of tau. Large uncertainty and the mild view tilt predict weak sensitivity.
8. Common-calendar results cover 2014-11-07–2024-12-31, 2,553 sessions, net 10 bps per L1. These are slices of existing strategies, not new training/deployment experiments. Full market/model results including both caps are in stage_c_common_period.csv.
9. L1 rebalance turnover is twice half-L1, so the same fee requires twice the coefficient under half-L1. Initial deployment remains purchased weight one. Direct fees differ from terminal-wealth impact.
10. All four private input snapshots match archived hashes. Raw inputs are excluded because redistribution authorization is unestablished. Revised specification, exact frozen-run reproduction and March-paper reproduction are distinct claims.

No historical table or figure value was corrected in this audit; new diagnostics are explicitly supplementary. No full backtests or new market-price downloads were run. The manuscript preserves eight logical tables, eight figure assets and 15 editable equations. Remaining limitations are documented in the issue register, not labeled fully resolved.


[All publication tables and figures](../results/phase3_final/). [Final supplementary evidence](../outputs/final_professor_challenge_resolution/). Historical summaries elsewhere are version records, not competing current results.

## Faculty-review resolution status

The following items are deliberate research boundaries, not outstanding arithmetic defects:

| Challenge | Evidence-backed conclusion | Residual limitation |
|---|---|---|
| Incremental BL value over 1/N | [Active-weight/posterior diagnostics](../outputs/final_professor_challenge_resolution/STAGE_A_IDENTIFICATION.md) show strong anchoring; improvement over 1/N was not established | Bayesian alpha is not identified |
| Unrestricted Markowitz comparator | [Matched 40% bounds](../results/phase3_final/table_03_concentration_robustness.csv) substantially reduce concentration and turnover | One fixed cap does not characterize every feasible investment mandate |
| Crisis selection history | [Reconstructed conditional paths](../outputs/final_professor_challenge_resolution/stage_b_crisis_reconciliation.csv) reconcile six summaries | Original pre-event weight-selection timestamps are missing; ex-ante construction cannot be independently certified |
| Decision-level uncertainty | [Paired estimates](../outputs/final_professor_challenge_resolution/stage_b_decision_uncertainty.csv) use limited dependent rebalance observations | Unadjusted exploratory inference; apparent zero Monte Carlo p-values are finite zero-exceedance counts |
| Sharpe uncertainty | [10/20/40-session block sensitivity](../outputs/final_professor_challenge_resolution/stage_b_sharpe_blocks.csv) does not reject zero Sharpe differences | Non-rejection does not establish equivalence; chosen bootstrap procedures remain approximate |
| Factor fit | [Independent US OLS/HAC calculation](../outputs/final_professor_challenge_resolution/stage_b_factor_audit.csv) reproduces coefficients and high R-squared | Regression fit is not a causal explanation or proof of predictive alpha |
| Cross-market interpretation | [Common-calendar check](../outputs/final_professor_challenge_resolution/stage_c_common_period.csv) shares 2,553 dates | ETF universes, composition and USD exposures differ; no national-market causal identification |
| Modelled fees | [L1 accounting explanation](METHODOLOGY.md) distinguishes fee rate, half-L1 notional, deployment and terminal NAV | Not a realistic estimate of market impact or institution-specific trading expenses |
| Public reproduction | [Reproducibility guidance](REPRODUCIBILITY.md) distinguishes public artifact tests from private data checks | Frozen raw vendor snapshots and derived daily caches are not distributed |
| Publication status | [Current candidate](../outputs/final_professor_challenge_resolution/FINAL_MANUSCRIPT.pdf) is clearly identified | Author verification and SSRN/AI-policy clearance remain pending |

**Release interpretation:** Public CI validates synthetic unit tests and committed artifact hashes, not a complete vendor-data reconstruction. A valid research finding may remain inconclusive: no model retuning, numerical fabrication, or removal of negative results is warranted.
