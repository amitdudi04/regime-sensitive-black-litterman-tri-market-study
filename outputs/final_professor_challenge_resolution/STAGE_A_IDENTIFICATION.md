# Stage A: identification and benchmark fairness

Stage A reuses validated Phase 2 run ff8cacdc-95f8-458e-8d71-d12efbd9a9f9 (execution source af84ddfbc93edc7a5143c654d6319d67e3139eef; frozen commit 7553cf8bff59a4f3d8bad7d15b779707fc533fa1). All stored output hashes and source fingerprints were checked. No portfolio backtest was rerun. Missing prior/posterior diagnostics alone were reconstructed at stored decision dates from hash-matched prices, using the exact 252-session covariance and tau code.

## A1: why BL resembles 1/N

Pi=lambda Sigma w_eq and Q-Pi=0.10(mu_hist-Pi), P=I. Thus posterior-Pi = tau Sigma (tau Sigma+Omega)^(-1) 0.10(mu_hist-Pi). Omega=10 diag(Sigma) independent of tau. The marginal view/prior variance ratio is 10/tau: 200 or 1,000. These diagonal ratios are not full correlated-matrix shrinkage eigenvalues. With no view adjustment the common quadratic objective is maximized at w_eq; equal weights satisfy both caps. Small posterior adjustments therefore perturb this diversified anchor. Optimizer numerical tolerances also affect tiny active weights; this analysis does not attribute every residual basis point causally to Bayesian information.

stage_a_diagnostics.csv reports all requested market-level weight, return, risk, trading and wealth differences; active-weight distributions by ETF and per-decision priors/views/posteriors appear in the supporting CSVs. Return and Sharpe differences use zero-RF net 10-bps paths; turnover excludes initial deployment. Mean deviation means mean absolute ETF active weight, not the mechanically zero signed cross-sectional mean. Tracking error uses sample daily standard deviation times sqrt(252). Expected-return adjustments are annual-return units.

The evidence establishes strong diversification anchoring and descriptive stabilization relative to unrestricted historical-mean Markowitz. Incremental Bayesian investment value over rebalanced 1/N is not established. The historical-return views are not independently sourced forecasts.

## A2: fairness and constraints

The stored Phase 2 code calls the same backtest with identical universes, covariance estimator, windows, rebalance dates, lambda, nonnegative/full-investment constraints, accounting and cost scenarios for BL and Markowitz. Only expected-return vectors differ within each cap. stage_a_cap_effects.csv quantifies changes from cap 1 to cap 0.4 using existing validated summaries; original levels remain unchanged. The cap is a target bound, not an intraperiod holdings limit. No extra benchmark family or cap was introduced. Average target concentration is summarized by HHI; it is not independent evidence of better investment performance.

## A3: chronology

The 40% scenario is introduced in the Phase 2 implementation commit af84ddfbc93edc7a5143c654d6319d67e3139eef. The execution manifest names that exact clean source commit and records caps [1.0,0.4]. This establishes specification before that recorded execution, not preregistration or independence from earlier Phase 1 findings. No public preregistration record is evidenced. Recommended wording: “The revised research introduced a fixed 40% maximum target-weight robustness specification, applied to both optimized strategies. It was specified in the Phase 2 implementation before its recorded execution; it was not part of the March study or a preregistered design.” Subsequent interpretations are retrospective.

Residual limitation: no design here isolates a causal benefit of Bayesian updating from prior diversification and matched constraints. Stage A is RESOLVED_WITH_LIMITATIONS.
