# Authoritative final research findings

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
