# Finance reviewer challenge checklist

Evidence-based review for an MSc Finance research portfolio. All answers describe the existing frozen design; no additional experiment is implied.

1. **Does BL add value beyond the chosen prior?**

   It is nearly identical to rebalanced 1/N on returns and Sharpe. The study establishes stabilization versus unrestricted historical-mean MV, not incremental alpha from Bayesian information. Evidence: Tables 2, 5; 6.1–6.2, 7.

2. **Is the prior actually a market portfolio?**

   No. It is an explicitly assumed equal-weight proxy, Pi=lambda Sigma w_eq. Original dated capitalization/AUM inputs remain missing. Evidence: 5.3, 8; Phase 1/2 configuration.

3. **Are the views independent information?**

   No. Q mildly tilts the implied prior toward historical sample means. Low blend and large diagonal Omega create strong anchoring. No causal decomposition or independent forecast skill is established. Evidence: 5.4; Equations 5–6.

4. **Are units compatible in reverse optimization and posterior?**

   Annual mean and annual covariance use 252 daily sessions consistently. Realized volatility uses sample daily standard deviation × sqrt(252), distinguished from fitted covariance. Evidence: 5.1–5.2, 5.6.

5. **Does tau cancel from Omega?**

   Omega is 10 times diagonal annual covariance with a floor, independent of tau. It therefore does not algebraically cancel with tau in this specification. Fixed-tau results are separate US diagnostics. Evidence: 5.4, 6.8; Table 8.

6. **Is the Markowitz comparator artificially weak?**

   Unrestricted historical means produce strong concentration. Matched 40% caps reduce instability and improve US/China Sharpe while lowering India Sharpe. Both specifications are retained; no claim that the chosen cap is optimal. Evidence: Table 3; Figure 4; 6.3.

7. **Do the two optimizers receive identical covariance and risk aversion?**

   Yes, both use the same LW scaled-identity covariance, annual units, lambda=3 and scenario constraints. Inputs differ through the expected-return construction. Evidence: 5.1–5.4; Phase 2 configuration.

8. **What exactly does the 40% cap constrain?**

   Targets at scheduled trades only. Weights drift afterward and can exceed the target cap. Max end-of-day weights remain separately recorded in the source CSV. Evidence: 5.7; Table 3 notes.

9. **Is equal weighting unfairly rebalanced every day?**

   No. It resets on the same 63-session schedule and drifts between trades. It pays the same deployment and L1-based modeled fees. Evidence: 5.5, 5.7; Tables 2, 4.

10. **Is ASI the quantity actually traded?**

   No. ASI is mean successive-target L1 distance excluding the first undefined target difference. Trading turnover compares targets with drifted pretrade holdings. Constant 1/N targets have ASI zero but require trades. Evidence: Equations 7–10; Figures 2–3.

11. **Are costs funded consistently and counted once?**

   Fees remove c times L1 turnover from available wealth before the holding-period return. Initial deployment turnover is 1. This is a weight-based proportional model, not an implicit broker-dollar trade-notional equation. Evidence: 5.5; Equations 8–9; Phase 1 validation.

12. **Can fees change gross decision paths in this experiment?**

   The objective ignores costs and fixed trades use common proportional NAV scaling; drifted weight ratios and gross decisions are unchanged across fee rates. Cost-aware optimization is not claimed. Evidence: 5.8; Table 4.

13. **Why can MV retain higher mean return but lower terminal wealth?**

   Annual arithmetic mean averages daily returns; terminal wealth multiplies growth factors. US 20-bps MV has higher arithmetic mean and lower terminal NAV than BL. This is not an accounting contradiction. Evidence: Table 4A/B; 6.4.

14. **Are direct fees the terminal gross–net wealth gap?**

   No. Fee totals sum pretrade NAV × fee fraction relative to initial NAV. The gross–net terminal gap additionally incorporates foregone investment growth. Neither total is a universal annual fee rate. Evidence: Table 4C; 5.6, 6.4.

15. **Are national markets directly comparable over a common horizon?**

   No. USD-listed ETF exposures overlap and have unequal effective dates. The comparisons are within each basket, not identification of local-market efficiency, institutional quality or currency-neutral differences. Evidence: Table 1; 4, 8.

16. **Does the bootstrap establish significance or equivalence?**

   No significant Sharpe differences were established. Every interval includes zero; every unadjusted p is >=0.05. This is neither proof of equivalence nor evidence that economically relevant differences are zero. Evidence: Table 5; 6.5.

17. **Is the inference method an exact Ledoit–Wolf bootstrap?**

   No. It uses paired 20-session circular blocks, 2,000 draws, seed 42, percentile intervals and approximate empirical-mean centering. It is not studentized and does not guarantee exact finite-sample coverage; one block choice and possible nonstationarity remain limits. Evidence: 5.9; Equation 13; 8.

18. **How are multiple comparisons handled?**

   They are unadjusted and explicitly labeled. Inactive-cap BL–1/N rows duplicate paths and are not independent evidence. No additional significance is inferred from repeated rows. Evidence: Table 5 notes; 5.9, 6.5.

19. **Were original volatility and ASI hypothesis tests reproduced?**

   No. Missing original test artifacts prevent that. Original p=.0106 is not significant at 1%; revised Sharpe tests answer a different question. Evidence: Change log p.23; 5.9, 6.5.

20. **Does the crisis experiment evaluate adaptive trading through stress?**

   No. Last pre-event target weights are purchased at event start and held without interim trades. This differs from freezing actual live drifted holdings and from the main rolling simulation. Evidence: 5.10; Table 6.

21. **What does crisis recovery mean?**

   Recovery targets event-start NAV 1 after the event-window MDD trough, counted by trading-index position difference. It is not previous-peak recovery or elapsed time since event onset. No daily stress curve is fabricated from summaries. Evidence: Equation 14; Table 6; 6.6.

22. **Does BL provide universal crisis protection?**

   No. US BL MDD and recovery are worse; China favors BL; India has worse BL MDD and marginally faster start-NAV recovery. Events are selected diagnostics without downside-superiority tests. Evidence: Table 6; 6.6.

23. **Can the US momentum regression explain China or India?**

   No. The fit is US-only, conditional and noncausal, with actual RF subtraction and HAC lag 5. No capped or 1/N regressions are invented. Alpha is not statistically positive. Evidence: Table 7; 5.11, 6.7.

24. **Was an original opposite momentum t-sign actually found?**

   No. Direct reading of original pp.22–23 gives −0.856 in both places, correcting the earlier documentary audit allegation. New verified regression values differ but do not prove that alleged historical contradiction. Evidence: Change log; original PDF hash.

25. **Can ex-post regimes support a real-time strategy claim?**

   No. Smoothed Markov states are retrospective descriptions. The trading tau selector uses only its training-window volatility observations, and no causal or statistically superior regime outcome is asserted. Evidence: 2.4; 5.4, 5.11; 8.

26. **Where is the ownership mechanism evidence?**

   Original dated stock-level inputs are unavailable. SOE/private empirical claims and old exhibits are withdrawn; obtaining genuine dated inputs is future work. Evidence: 3, 8–10; change log pp.24–25.

27. **Can someone exactly reproduce the March numbers?**

   Not from the available archive. Frozen revised-study provenance is supplied; original vintages, capitalization priors, ownership data and tests remain missing. Fresh vendor data may differ and raw snapshots are not in Git. Evidence: 10; Phase 1–3 manifests.

28. **Does verified software make the research institutionally implementable?**

   No. It checks identities and internal consistency, not model optimality, liquidity, capacity, taxes, execution quality or price impact. These remain substantive scope limits. Evidence: 7–8, 10.

29. **What is the contribution if outperformance is insignificant?**

   A transparent cross-basket comparison of target stability, actual modeled trading, matched constraints, simple anchoring and statistical uncertainty. Mixed outcomes and close 1/N performance sharpen the implementation interpretation. Evidence: 3, 7, 11.

30. **Has the author already approved all scholarship and disclosures?**

   No. This is an author-review draft. Funding/conflicts, AI use and oversight, author metadata, reference-review items and final interpretations require approval before submission. No SSRN upload occurred. Evidence: Declarations; validation report.

