# Stage B statistical and risk validation

Method fixed before execution in STAGE_B_ANALYSIS_SPECIFICATION.md. Code: scripts/final_audit/stage_b.py. All outputs are supplementary diagnostics; historical evidence is unchanged.

## B1: decision-level uncertainty

Actual paired observations are consecutive-target ASI contributions and post-initial drift-adjusted trade amounts, not daily returns. Sample means use 40–55 aligned differences per market. Paired circular blocks of 3 decisions, 5,000 draws, seed 20261101; percentile 95% intervals and approximate empirical-mean-centered p-values, zero-mean null. Results: stage_b_decision_uncertainty.csv. There are 20 unadjusted p-values below .05 among 24 comparisons. The few decisions, overlapping estimation windows, regime changes and selected block size limit inferential reliability. No multiplicity correction; cap-inactive BL/1N duplicates are not independent evidence. These tests do not reproduce the March manuscript's unavailable original ASI tests. RESOLVED_WITH_LIMITATIONS.

## B2: Sharpe blocks

10, 20 and 40 session blocks, existing paired circular implementation, 2,000 draws, seed 42. All stored 20-session rows reused. Minimum p across the sensitivity grid is 0.1020; all 95% intervals include zero: True. These results do not establish equivalence. Multiplicity remains unadjusted and centered p-values approximate. See stage_b_sharpe_blocks.csv. No parameter search or return-path rerun. RESOLVED_WITH_LIMITATIONS.

## B3: reconstructed crisis paths

All six buy-and-hold summary rows reconcile to tolerance 1e-12 from archived Frozen Weights JSON and hash-matched historical price snapshots. Independent formula NAV_t=sum_i w_i product_s(1+r_i,s), initial NAV before first event return=1; no interim trades. Event running peak includes initial 1; trough is within event; recovery is first subsequent NAV >=1; duration is trading-index positions from trough. stage_b_crisis_paths.csv preserves daily observations through the available end of history; the implicit pre-first-return initial value is 1. stage_b_crisis_reconciliation.csv records outcomes. No prices or weights refitted.

The summary explicitly stores the frozen target vector, but the separate historical crisis optimizer weight timeline was not preserved. Consequently the original selection strictly before the crisis cannot be independently reverified from that timeline. Reconstructing from stored vectors is conditional reconciliation, not independent reproduction of their selection. Status RESOLVED_WITH_LIMITATIONS for paths; UNRESOLVED_SOURCE_EVIDENCE for the missing original target-selection timeline. No changed summary was accepted. Historical weighted-log fields remain a distinct diagnostic, not the investment path.

## B4: factor audit

Independent numpy least-squares and Bartlett HAC sandwich, lag 5, no small-sample correction, reproduce archived Phase 1 coefficients, R² and all reported t-statistics. Exact 3,521-date alignment; net returns minus decimal RF; columns intercept, MKT, SMB, HML, MOM. Cached factors are already divided by 100; analysis/factor_regression.py and cache metadata verify conversion provenance. Raw percent provider response is not archived, so source conversion was inspected rather than independently downloaded/recovered.

stage_b_factor_audit.csv records coefficients, standard errors, t values, residual variance, sample size, design and standardized factor-correlation condition numbers. BL R²=0.985503743 is high but residual variance remains positive; the large market t-statistic is reproduced, not presumed erroneous. US ETF baskets contain broad-market and sector exposures, so strong conditional market fit is economically plausible; that explanation is not a causal attribution test. Design conditioning includes a differently scaled intercept, so standardized factor correlations are also supplied. The same-sample 1/N fit is labeled a new supplementary diagnostic. No China/India factor inference is made. RESOLVED_WITH_LIMITATIONS.

## B5: tau

Five archived fixed-tau values remain unchanged. Omega=10 diag(Sigma) does not scale with tau. Thus tau does not cancel: posterior-Pi=tau Sigma(tau Sigma+Omega)^(-1)0.10(mu-Pi). For small tau relative to Omega the adjustment is approximately linear in tau and small; a strong equal-weight anchor predicts weak sensitivity. Cross-asset covariances mean diagonal ratios alone are not eigenvalue shrinkage factors. Fixed settings are separate runs, while the main rule uses only training-window volatility. No extra optimization runs. RESOLVED_WITH_LIMITATIONS.
