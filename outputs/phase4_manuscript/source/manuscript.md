ABSTRACT

This study compares Black-Litterman (BL) and historical-mean Markowitz allocation in small US-listed ETF baskets providing exposure to the United States, China and India. The revised experiment uses 252-session rolling estimation windows, Ledoit-Wolf covariance shrinkage, long-only fully invested portfolios, rebalancing every 63 sessions and self-financing buy-and-hold accounting between trades. BL uses an explicitly equal-weight equilibrium proxy and a mild historically derived view tilt. Periodically rebalanced equal-weight allocation provides a direct benchmark for this anchoring choice. Additional comparisons impose matched 40% maximum target weights and evaluate proportional trading costs of 0, 5, 10 and 20 basis points per unit of drift-adjusted L1 turnover. At 10 basis points, BL has substantially lower target instability and turnover than unrestricted Markowitz, but its returns and Sharpe ratios are nearly those of rebalanced 1/N. Matched concentration limits substantially reduce Markowitz concentration and instability; US and China Sharpe ratios improve, whereas India's declines. No statistically significant Sharpe-ratio differences were established under the specified paired bootstrap procedure. Cost rankings depend on whether performance is measured by arithmetic annualized return or compounded terminal wealth. Separate historical crisis tests are event-specific, and US factor and fixed-tau diagnostics retain their separate source provenance. The contribution is a transparent comparison of stabilization, concentration and implementation trade-offs across the three ETF baskets; the evidence does not establish universal BL superiority, incremental value over 1/N or causal benefits of Bayesian updating.

# 1 Introduction

The primary research objective of this study is to evaluate portfolio-weight instability in mean-variance optimization and assess the effectiveness of Black-Litterman equilibrium anchoring across distinct investment baskets. The Markowitz framework defines a clear risk-return allocation problem, but the inputs used by an investor are estimates rather than known population quantities. Optimizing against noisy expected returns can produce concentrated targets and substantial changes in allocation as an estimation window advances. The distinction between an optimal portfolio conditional on inputs and a reliably implemented investment rule motivates this comparison [[Markowitz1952;Markowitz1959;ChopraZiemba1993]].

Black-Litterman changes expected-return inputs by combining a prior return vector with views and their uncertainty [[BlackLitterman1992;HeLitterman1999]]. In this application, the prior is reverse-engineered from an equal-weight allocation under a specified risk-aversion parameter. This is a transparent equilibrium proxy, not an observed capitalization-weighted market portfolio. The views are a small tilt toward rolling historical means, not independently elicited analyst forecasts. Lower instability is therefore partly a consequence of the chosen anchor and uncertainty scale. The empirical question is whether that stabilization is accompanied by investment performance that exceeds a simple, similarly implemented alternative.

Portfolio comparisons also depend on constraints and trading rules. A highly concentrated historical-mean optimizer is a demanding but incomplete benchmark for a strongly anchored allocation. We retain that unrestricted long-only comparison and add a predefined 40% target cap for both optimized strategies. Rebalanced 1/N separates the effect of maintaining diversified weights from any incremental value of the BL posterior. Both checks are motivated by the importance of constraints and estimation error in empirical portfolio evaluation [[DeMiguel2009;JagannathanMa2003]].

Implementation friction matters because changes in target weights are not identical to trades. Between scheduled rebalances, asset returns change the weights of fixed holdings. The amount traded at the next rebalance depends on those drifted holdings as well as the new target. We therefore distinguish allocation stability, actual modeled L1 turnover, initial deployment and proportional trading costs. We also distinguish arithmetic annualized mean return from compounded terminal wealth. Neither low turnover nor a higher arithmetic mean alone establishes superior net investment growth.

The United States, China and India provide three distinct sets of equity exposures. All instruments are US-listed, USD-denominated ETFs. The study does not identify a causal effect of national market efficiency, ownership structure or local microstructure: the samples differ in length, ETFs overlap in holdings and all returns are measured from the same listing market. The cross-market contribution is an empirical comparison under common calculation rules, not an experiment that isolates institutional differences among countries.

The March 2026 version motivated the same stability and implementation questions but contained numerical and interpretive inconsistencies. This revision replaces its empirical record with separately verified results, adds 1/N and matched-constraint comparisons, specifies the accounting conventions and weakens claims not supported by the uncertainty estimates. The original version remains a historical record; its reported numbers are not presented as independently reproduced.

# 2 Literature review

## 2.1 Mean-variance estimation and covariance shrinkage

Mean-variance portfolio selection provides the mathematical foundation for the optimization problem studied here [[Markowitz1952;Markowitz1959]]. The practical concern is sensitivity to estimated inputs. Chopra and Ziemba examine how errors in means, variances and covariances affect portfolio choice; this motivates assessing allocations and implementation behavior in addition to a portfolio's realized mean and volatility [[ChopraZiemba1993]]. It does not imply that every historical-mean optimizer must underperform every stabilized alternative.

Covariance shrinkage is one response to estimation uncertainty [[LedoitWolf2003;LedoitWolf2004a]]. The executable estimator in this study shrinks centered covariance estimates toward a scaled identity target, corresponding to the Ledoit-Wolf formulation described in their Journal of Multivariate Analysis article [[LedoitWolf2004b]]. Shrinkage is used identically for BL and Markowitz. Consequently, differences between the two strategies cannot be attributed to one model receiving covariance shrinkage while the other does not. The present ETF universes are small, so this application should not be treated as a direct test of large-dimensional asymptotic results.

## 2.2 Equilibrium anchoring and investor views

The equilibrium-return perspective in Black-Litterman is related to the role of market equilibrium in asset pricing [[Sharpe1964;Lintner1965;BlackLitterman1992]]. Reverse optimization supplies a neutral expected-return starting point conditional on the specified covariance, reference weights and risk aversion. It does not establish that an arbitrary ETF proxy is the true market portfolio or that its implied expected returns are correctly calibrated.

He and Litterman explain how views alter an equilibrium-based allocation, while Idzorek discusses the treatment of view confidence [[HeLitterman1999;Idzorek2004]]. Meucci provides a broader presentation of the original model and its extensions [[Meucci2010]]. These contributions distinguish an allocation framework from the empirical validity of any particular prior or forecast. In this study, the equal-weight reference and historically constructed views are explicit modeling assumptions whose implications must be assessed against 1/N.

Fernandes, Ornelas and Cusicanqui combine equilibrium, resampling and analyst views in a portfolio methodology [[Fernandes2012]]. That work places this paper's concern with diversification and allocation stability in an established literature. The present revision does not implement their resampling-based portfolio-construction model. Nor does it claim to invent the L1 distance between allocations; the label Allocation Stability Index is used as a descriptive summary of that established distance.

## 2.3 Equal weighting constraints and costs

The out-of-sample comparison with 1/N is central to determining whether estimation-intensive procedures add investment value [[DeMiguel2009]]. Constraints can also affect estimated portfolio risk and concentration [[JagannathanMa2003]]. These findings motivate two controls here: common rebalancing and accounting for 1/N, and identical upper bounds for BL and Markowitz. A comparison that changed the optimizer's constraints for only one strategy would conflate expected-return estimation with portfolio feasibility.

Turnover and implementation costs are established components of active portfolio management [[GrinoldKahn2000]]. Gârleanu and Pedersen model dynamic trading when returns are predictable and trading is costly [[GarleanuPedersen2013]]. Their optimization problem is not implemented here: our strategies optimize gross mean-variance utility and then apply a common proportional-cost accounting rule. The cost analysis is therefore sensitivity analysis of fixed trading decisions, rather than a claim to estimate an optimal execution policy or an institution's realized market impact.

## 2.4 Regimes factors and performance inference

Hamilton's regime-switching framework and subsequent asset-allocation applications show why changing return distributions deserve attention [[Hamilton1989;AngBekaert2002;GuidolinTimmermann2007]]. Our main strategy instead uses a training-only volatility rule to select tau. A separately retained Markov analysis uses full-sample smoothed states for ex-post description. Those states are not inputs to the trading simulation, and no claim of real-time regime prediction follows from them.

The US diagnostic uses the Fama-French factors and a momentum factor in the spirit of four-factor performance analysis [[FamaFrench1993;Carhart1997]]. Inference uses HAC covariance estimates [[NeweyWest1987]]. The coefficients describe exposures conditional on this specification; they do not identify a causal investment mechanism or explain untested China and India portfolios.

Sharpe comparisons require uncertainty estimates. Classical tests include those of Jobson and Korkie and Memmel [[JobsonKorkie1981;Memmel2003]]. Ledoit and Wolf discuss robust performance inference and a studentized time-series bootstrap [[LedoitWolf2008]]. Our retained empirical procedure is a different, explicitly approximate paired circular-block bootstrap with percentile intervals and empirical-mean-centered p-values. It is not described as an implementation of their studentized method, and its finite-sample limitations remain part of the interpretation.

# 3 Research questions and contribution

The first question is whether equilibrium-anchored BL produces smaller changes in target allocations and lower drift-adjusted turnover than unrestricted historical-mean Markowitz. These are separate implementation outcomes: targets can remain constant while trades are required to offset price drift.

The second question is whether the resulting return, Sharpe and drawdown differences are economically meaningful and supported by statistical uncertainty. Rebalanced equal weighting provides a direct comparison for the chosen prior. The third question is whether a common concentration constraint reduces the apparent differences between the optimized strategies. The fourth concerns the effect of proportional costs on arithmetic net returns and compounded wealth. Finally, standalone crisis tests, US factor estimates and fixed-tau results describe selected risk and specification sensitivities without being recast as prospective trading evidence.

The contribution is an empirical cross-market assessment under traceable data, constraints and accounting conventions. It links target stability to actual modeled trading and compares optimization stabilization with a simple diversified rule. The evidence supports conclusions about this specified implementation. It does not constitute a new L1 stability measure, a proof of Bayesian superiority, a causal national-market comparison or an ownership-based downside-protection study. The earlier SOE/private empirical section is withdrawn from the revised results because its original stock-level inputs cannot be verified.

# 4 Dataset and investment assumptions

Table 1 identifies the ETF universes, currency, common price histories and out-of-sample coverage. The United States basket contains SPY, QQQ, IWM, XLF and XLK; China contains ASHR, KWEB, MCHI and FXI; India contains INDA, EPI, SMIN and INDY. These are exposures through US-listed instruments rather than direct local-currency national equity returns. Sector and broad-market ETFs overlap, so neither the number of tickers nor the market labels imply independent underlying holdings.

The revised study uses Yahoo Finance provider-adjusted closing prices obtained through yfinance with auto_adjust=False and an explicit Adj Close field. These series are provider proxies incorporating dividend and split adjustments; they are not a record of executable intraday prices or an independently reconstructed distribution-reinvestment strategy. No Refinitiv input is used in the verified revised experiment. Data are aligned on common observed dates within each basket, without forward or backward filling. Missing required tickers, ambiguous raw-close substitution, duplicate dates, invalid prices and nonfinite observations are not silently accepted.

The main request begins on 2010-01-01 and ends before 2025-01-01. Common price histories begin later for China and India because their ETF baskets have different observed availability. The OOS windows are {{1|US|*|OOS Start|str}} to {{1|US|*|OOS End|str}} in the US, {{1|China|*|OOS Start|str}} to {{1|China|*|OOS End|str}} in China, and {{1|India|*|OOS Start|str}} to {{1|India|*|OOS End|str}} in India. The corresponding samples contain {{1|US|*|OOS Observations|int}}; {{1|China|*|OOS Observations|int}}; and {{1|India|*|OOS Observations|int}} return observations. No 2025 trading observations are included.

[[TABLE1]]

The common price sample is distinct from the rolling OOS sample, because the first estimation window does not earn simulated strategy returns. All three primary strategies within a market use identical OOS dates and the same initial deployment date. Cross-market terminal wealth must not be interpreted as performance over a common horizon. SPY, ASHR and INDA remain separately identified passive ETF references in the dataset record; the primary research benchmark introduced in this revision is rebalanced 1/N, not a relabeling of the original manuscript's generic benchmark row.

Frozen input snapshots and their retrieval metadata are retained locally with SHA-256 fingerprints. Phase 4 uses the committed Phase 3 tables and figures rather than obtaining a new market-data vintage. Exact input, source-run and output identities are described in Section 10. The separate crisis-history request permits a US 2008 stress test and is not silently added to the main 2010-requested rolling experiment.

# 5 Methodology

## 5.1 Returns and common mean-variance objective

For asset i and session t, the adjusted-price simple return is defined by Equation (1). Investment wealth is compounded from simple returns; log returns are not substituted into this accounting.

[[EQ1]]

Both optimized strategies maximize the same annual-unit utility in Equation (2), subject to full investment, nonnegative weights and a common maximum target weight u. Risk aversion lambda is 3. The unrestricted long-only case uses u=1; the robustness scenario uses u=0.4. Markowitz estimates annual expected returns by multiplying the training-window mean daily simple return by 252. The common objective differs between strategies through expected returns, not a model-specific penalty or covariance estimator.

[[EQ2]]

## 5.2 Covariance estimation and units

Ledoit-Wolf covariance is estimated from centered daily training returns and annualized by 252. Equation (3) summarizes the shrinkage form: S is the centered daily empirical covariance, delta is the estimated shrinkage intensity, N is the number of assets and I is the identity matrix. The target scale is the average variance, not an independently estimated factor covariance.

[[EQ3]]

Expected-return vectors and covariance matrices are therefore on compatible annual scales in utility, reverse optimization and posterior construction. Annualized realized volatility is a separate descriptive metric based on daily sample standard deviation. Covariance shrinkage addresses one component of estimation uncertainty; it does not ensure accurate expected returns or establish general out-of-sample superiority.

## 5.3 Equal-weight equilibrium proxy

Equation (4) defines the implied prior. The reference weights are equal across ETFs. They are not historical ETF AUM weights, observed capitalization weights or a reconstruction of the original paper's claimed market portfolio. The prior should be interpreted as the return vector that rationalizes the chosen proxy under the assumed covariance and lambda.

[[EQ4]]

This distinction is economically important. The experiment evaluates a deliberately diversified anchor, not an empirical test of whether market capitalization contains superior equilibrium information. The mathematical framework can accommodate other priors, but the missing original dated capitalization inputs are not replaced by fabricated historical observations.

## 5.4 Views posterior and tau rule

Absolute views use an identity pick matrix and a mild historical-return tilt, as summarized in Equation (5). The blend b equals 0.10. Omega is diagonal with entries equal to ten times the corresponding annualized variances, with a 10⁻¹² numerical floor in the executable construction. Its dependence on annualized variance, and independence from tau, are retained from the verified specification.

[[EQ5]]

The posterior mean follows the Gaussian conditioning expression in Equation (6), equivalent to the familiar precision representation on nonsingular inputs. The implementation solves the conditioning system rather than taking explicit matrix inverses. P maps asset returns into view portfolios; Q is the view-return vector; Omega expresses view uncertainty; tau scales prior uncertainty. These are model inputs, not observed evidence of investor foresight.

[[EQ6]]

Within each 252-session training window, a 60-session rolling standard deviation is computed for each asset. The latest cross-asset average volatility is compared with the median of the cross-asset averages available inside that same training window. Tau is 0.01 when the latest value exceeds that median and 0.05 otherwise. Only prior observations enter the decision. A smaller tau gives less weight to the historical tilt relative to the prior in this construction. The rule was not selected in Phase 4 to improve performance.

The small blend and comparatively large view uncertainty produce strong anchoring. This is a substantive reason to compare the strategy with 1/N rather than attributing every low-turnover outcome to an independently informative Bayesian forecast. The main tau rule is not the ex-post Markov classifier, and fixed-tau diagnostics in Section 6.8 are separate runs rather than observations of a single adaptive strategy.

## 5.5 Rolling portfolio accounting

Each decision uses 252 completed sessions and applies the resulting weights to the next holding interval of up to 63 sessions. Training excludes the current holding-period return. The final interval may contain fewer than 63 observations. Long-only portfolios remain fully invested in the ETF basket after modeled fees; there is no interim rebalancing between scheduled decisions.

Let h_t denote weights entering session t after any scheduled trade. Equation (7) gives the gross portfolio return and the subsequent drift of fixed holdings. New targets replace those drifted weights only on a rebalance date.

[[EQ7]]

At rebalance k, the L1 traded-weight convention is the sum of absolute differences between the new target and drifted pretrade weights. Initial deployment from cash has L1 purchased weight 1, reported separately from subsequent rebalance averages.

[[EQ8]]

For a cost rate c per unit of L1 turnover, the wealth fraction removed is cTₖ on a trade date and zero otherwise. Equation (9) applies the fraction before the first holding-period asset return. Costs are not subtracted twice and are not estimated from successive target vectors without considering drift.

[[EQ9]]

This is a proportional weight-turnover cost convention. It differs from half-L1 turnover or one-way-notional conventions, and it does not solve an implicit brokerage-dollar fee-funding equation. The implemented trading targets are obtained from gross utility, not from a transaction-cost-aware optimization objective. These qualifications define the experiment rather than alleging that modeled costs equal actual commissions, spreads or market impact.

## 5.6 Allocation stability and realized performance

Equation (10) defines mean target-weight ASI across K rebalance decisions. The first undefined target difference is excluded. ASI is an established L1 allocation distance used descriptively here, not a proprietary mathematical innovation or an independently tested significance statistic.

[[EQ10]]

Equation (11) reports the arithmetic annualized mean, annualized sample volatility and zero-risk-free-rate Sharpe. The overbar on r denotes the daily net sample mean and s_r its sample standard deviation. A zero risk-free rate is the main performance convention; it differs from the actual RF subtraction used in the US factor regression.

[[EQ11]]

Equation (12) defines compounded net wealth and maximum drawdown from initial NAV 1, including a loss on the first OOS observation. The arithmetic annual mean is not a compounded growth rate. A positive arithmetic annualized mean can coexist with terminal wealth below 1. Direct modeled fee expenditure is the sum of pretrade net NAV times the relevant fee fraction, in units of initial NAV; it is not the gross-minus-net terminal wealth difference, which also includes investment growth forgone.

[[EQ12]]

## 5.7 Equal weighting and matched concentration

The 1/N portfolio is deployed at the identical initial date and reset to equal weights at the identical 63-session rebalance schedule. Its holdings drift between trades under Equation (7), and it pays the same modeled initial and subsequent costs. Its target ASI is zero, but its actual traded turnover need not be zero. It is therefore a periodic allocation rule, not a permanently static vector applied to every day's return.

The 40% target cap is predefined, not searched for using realized performance. Feasibility follows from N times the maximum weight being at least 1 for all baskets. The additional comparison applies the same bound to BL and Markowitz, while retaining their common covariance, risk aversion, windows, return data and accounting. The constraint governs targets at trades; weights can drift above 40% afterward. Concentration is summarized by maximum target weight and mean target HHI, the sum of squared weights. End-of-day concentration is separately identified in the source evidence.

## 5.8 Transaction-cost sensitivity

The cost scenarios are 0, 5, 10 and 20 basis points per unit of the existing L1 convention. For fixed targets and holding intervals, cost rates do not affect gross asset returns, the optimizer inputs or drifted weight ratios. Gross portfolio paths and trading decisions can therefore be reused while changing only the multiplicative fee factors. Table 4 reports both return and wealth metrics and separately identifies direct modeled fees. A reduction in fees is not itself proof that one strategy delivers higher net return or higher terminal wealth.

## 5.9 Paired statistical uncertainty

At net 10 basis points, BL is compared with Markowitz and 1/N on identical complete OOS dates within each market. Twenty-session contiguous blocks are sampled with circular wrapping and common indices for each strategy pair. The procedure uses 2,000 replications and seed 42. Each draw produces an annualized Sharpe difference. The 95% interval is the percentile interval of those bootstrap differences; Equation (13) records the retained approximate two-sided probability, centered on the bootstrap mean.

[[EQ13]]

Here d_obs is the observed BL-minus-comparator Sharpe difference, d*b is its value in draw b, B is the number of draws, and the overbar denotes their empirical mean. The procedure is an approximate centered-bootstrap diagnostic, not an exact finite-sample test and not the studentized procedure of Ledoit and Wolf. Undefined Sharpe statistics are rejected. P-values are unadjusted across the reported comparisons. The cap-inactive BL/1N rows repeat the same return comparison and are not independent corroboration. Intervals containing zero do not establish exact strategy equivalence. The original manuscript's volatility and ASI test inputs have not been recovered; those historical tests are not replaced by new claims of their reproduction.

## 5.10 Standalone historical crisis tests

The crisis evaluations retain Phase 1's separate frozen-holdings buy-and-hold convention. For each selected event, the last target observed strictly before the requested crisis start is purchased before the first event return at gross initial NAV 1. Holdings then drift without interim trades through the recovery observation period. This is a standalone stress portfolio, not the adaptive strategy's actual drifted holdings frozen at the crisis boundary, and it is not part of the main rolling OOS performance sample.

Equation (14) gives the fixed-holdings wealth path. Crisis-window drawdown uses the running maximum including the pre-return NAV of 1. The trough is the date of maximum drawdown within the event window. Recovery is the first subsequent return to crisis-start NAV 1; duration is the difference in trading-index positions from that trough to recovery. It is not time from crisis start or recovery to a previously attained peak. Peak-based recovery is a legitimate different question, so the crisis-start definition is not described as the only defensible financial convention.

[[EQ14]]

Unrecovered cases remain censored rather than receiving a zero or arbitrary duration. Table 6 retains the verified summary outcomes; verified daily crisis curves are not available in the archived evidence, so no crisis wealth figure is reconstructed. Legacy weighted sums of daily log returns are not treated as equivalent to self-financing buy-and-hold wealth.

## 5.11 US factor and fixed-tau diagnostics

The Phase 1 US regression estimates daily portfolio excess return on US market excess return, SMB, HML and momentum, with an intercept, as in Equation (15). Kenneth French source percentages are divided by 100 and matched by exact trading date; future factor values are not backfilled. OLS coefficients are accompanied by Newey-West/HAC inference with a maximum lag of 5. Daily alpha and its arithmetic annualization by 252 are identified separately.

[[EQ15]]

These are retained Phase 1 regressions of that run's US net strategy returns, not new regressions of Phase 2 capped or 1/N portfolios. Their source sample and factor fingerprints are recorded. They are not extended to China and India. The same provenance distinction applies to the five existing US fixed-tau scenarios. Ex-post smoothed Markov states remain descriptive and are not used to select allocations or to establish statistically superior regime protection.

# 6 Empirical results

## 6.1 Principal strategy comparison

Table 2 reports the three strategies at net 10 basis points with the unrestricted long-only target bound. Figure 1 uses their actual daily net returns. All strategies within a panel share the same sample and deployment date; the three market panels do not share a common horizon.

[[TABLE2]]

[[FIGURE1]]

In the US, BL's annualized arithmetic net return is {{2|US|Black-Litterman|Net Annualized Return|pct4}}, compared with {{2|US|Markowitz|Net Annualized Return|pct4}} for Markowitz and {{2|US|Equal-weight|Net Annualized Return|pct4}} for 1/N. BL's Sharpe is {{2|US|Black-Litterman|Sharpe Ratio|f6}}, versus {{2|US|Markowitz|Sharpe Ratio|f6}} and {{2|US|Equal-weight|Sharpe Ratio|f6}}. BL therefore has higher descriptive Sharpe than unrestricted Markowitz, but a marginally lower Sharpe than 1/N. Its maximum drawdown, {{2|US|Black-Litterman|Max Drawdown|pct4}}, is worse than Markowitz's {{2|US|Markowitz|Max Drawdown|pct4}}. These outcomes do not show universal downside superiority.

In China, the annualized arithmetic net returns are {{2|China|Black-Litterman|Net Annualized Return|pct4}} for BL, {{2|China|Markowitz|Net Annualized Return|pct4}} for Markowitz and {{2|China|Equal-weight|Net Annualized Return|pct4}} for 1/N. Their Sharpes are {{2|China|Black-Litterman|Sharpe Ratio|f6}}, {{2|China|Markowitz|Sharpe Ratio|f6}} and {{2|China|Equal-weight|Sharpe Ratio|f6}}. BL outperforms unrestricted Markowitz on these descriptive metrics, while nearly matching 1/N. The basket experiences substantial drawdowns under all three rules. The country label does not identify a causal policy or ownership explanation for those paths.

In India, Markowitz has a higher annualized arithmetic net return, {{2|India|Markowitz|Net Annualized Return|pct4}}, and Sharpe, {{2|India|Markowitz|Sharpe Ratio|f6}}, than BL's {{2|India|Black-Litterman|Net Annualized Return|pct4}} and {{2|India|Black-Litterman|Sharpe Ratio|f6}}. The corresponding 1/N values are {{2|India|Equal-weight|Net Annualized Return|pct4}} and {{2|India|Equal-weight|Sharpe Ratio|f6}}. BL and 1/N are again very close, while BL's drawdown is worse than unrestricted Markowitz's. This market is a direct counterexample to a universal BL performance claim.

## 6.2 Target stability and trading turnover

Figures 2 and 3 separate target ASI from drift-adjusted traded turnover. BL's mean ASI is {{2|US|Black-Litterman|ASI|f6}} in US, {{2|China|Black-Litterman|ASI|f6}} in China and {{2|India|Black-Litterman|ASI|f6}} in India. Markowitz's corresponding values are {{2|US|Markowitz|ASI|f6}}, {{2|China|Markowitz|ASI|f6}} and {{2|India|Markowitz|ASI|f6}}. These are large descriptive differences in optimizer target behavior. No new significance test of ASI or volatility is inferred from them.

[[FIGURE2]]

Average subsequent rebalance L1 turnover is {{2|US|Black-Litterman|Mean Rebalance L1 Turnover|pct2}} versus {{2|US|Markowitz|Mean Rebalance L1 Turnover|pct2}} in US; {{2|China|Black-Litterman|Mean Rebalance L1 Turnover|pct2}} versus {{2|China|Markowitz|Mean Rebalance L1 Turnover|pct2}} in China; and {{2|India|Black-Litterman|Mean Rebalance L1 Turnover|pct2}} versus {{2|India|Markowitz|Mean Rebalance L1 Turnover|pct2}} in India. BL therefore trades much less than unrestricted Markowitz under the modeled convention. Initial cash deployment is excluded from these averages and charged separately.

[[FIGURE3]]

Rebalanced 1/N illustrates why target stability does not imply no trading. Its ASI is zero, yet its turnover is {{2|US|Equal-weight|Mean Rebalance L1 Turnover|pct2}}, {{2|China|Equal-weight|Mean Rebalance L1 Turnover|pct2}} and {{2|India|Equal-weight|Mean Rebalance L1 Turnover|pct2}}. It trades less than BL in the US and only slightly more in China and India. Strong equilibrium anchoring therefore explains a specific comparison with a concentrated optimizer, not a general implementation advantage over every simple allocation rule.

## 6.3 Matched concentration robustness

Table 3 and Figure 4 apply the same predefined 40% maximum target weight to both optimized strategies. BL's cap is inactive in the realized samples, so its capped and unrestricted paths coincide. Markowitz's mean target HHI declines from {{3|US|Markowitz|Mean Target HHI|f6|cap=1}} to {{3|US|Markowitz|Mean Target HHI|f6|cap=0.4}} in US, from {{3|China|Markowitz|Mean Target HHI|f6|cap=1}} to {{3|China|Markowitz|Mean Target HHI|f6|cap=0.4}} in China and from {{3|India|Markowitz|Mean Target HHI|f6|cap=1}} to {{3|India|Markowitz|Mean Target HHI|f6|cap=0.4}} in India.

[[TABLE3]]

The cap also reduces Markowitz target ASI and rebalance turnover. Capped turnover becomes {{3|US|Markowitz|Mean Rebalance L1 Turnover|pct2|cap=0.4}}, {{3|China|Markowitz|Mean Rebalance L1 Turnover|pct2|cap=0.4}} and {{3|India|Markowitz|Mean Rebalance L1 Turnover|pct2|cap=0.4}}. This demonstrates that the instability contrast is sensitive to reasonable portfolio constraints rather than being an immutable distinction between two optimization paradigms.

[[FIGURE4]]

Capped Markowitz Sharpe rises to {{3|US|Markowitz|Sharpe Ratio|f6|cap=0.4}} in US and {{3|China|Markowitz|Sharpe Ratio|f6|cap=0.4}} in China, but declines to {{3|India|Markowitz|Sharpe Ratio|f6|cap=0.4}} in India. The matched-cap BL-minus-Markowitz differences are smaller in US and China. These are descriptive robustness results, not an optimized cap choice or a claim that every concentration restriction improves performance.

## 6.4 Transaction costs and investment growth

Table 4 separates gross and net arithmetic annual returns, direct modeled fee expenditure and terminal wealth for the four cost rates. Both optimized cap scenarios and the primary 1/N benchmark are represented. Figure 5 illustrates terminal wealth for the unrestricted primary strategies. No portfolio optimization is repeated merely to change the cost assumption.

[[TABLE4]]

[[FIGURE5]]

For US unrestricted Markowitz, the net arithmetic annualized return changes from {{4|US|Markowitz|Net Annualized Return|pct4|cap=1,cost=0}} at zero costs to {{4|US|Markowitz|Net Annualized Return|pct4|cap=1,cost=20}} at 20 basis points. BL changes from {{4|US|Black-Litterman|Net Annualized Return|pct4|cap=1,cost=0}} to {{4|US|Black-Litterman|Net Annualized Return|pct4|cap=1,cost=20}}. At 20 basis points, Markowitz still has the higher arithmetic annual return, but its terminal NAV of {{4|US|Markowitz|Net Terminal Wealth|f4|cap=1,cost=20}} is below BL's {{4|US|Black-Litterman|Net Terminal Wealth|f4|cap=1,cost=20}} and 1/N's {{4|US|Equal-weight|Net Terminal Wealth|f4|cap=1,cost=20}}. There is no contradiction: a sample arithmetic mean and a product of daily growth factors summarize different aspects of the return path.

In China, unrestricted Markowitz's 20-bps arithmetic mean is {{4|China|Markowitz|Net Annualized Return|pct4|cap=1,cost=20}}, while its terminal NAV is {{4|China|Markowitz|Net Terminal Wealth|f4|cap=1,cost=20}}, below the initial 1. BL and 1/N finish close to each other and above that value. In India, unrestricted Markowitz remains ahead of BL on both arithmetic annual return and terminal wealth at the highest tested cost: {{4|India|Markowitz|Net Annualized Return|pct4|cap=1,cost=20}} and {{4|India|Markowitz|Net Terminal Wealth|f4|cap=1,cost=20}}, versus {{4|India|Black-Litterman|Net Annualized Return|pct4|cap=1,cost=20}} and {{4|India|Black-Litterman|Net Terminal Wealth|f4|cap=1,cost=20}}. Lower BL turnover therefore does not establish a universal net-performance ranking.

The cost fractions are a specified sensitivity grid, not empirically measured spreads or an estimated institutional implementation frontier. Direct fee totals are expressed relative to initial NAV over different sample lengths; they should not be compared as annual cost rates or interpreted as a fraction of a common terminal portfolio. The original manuscript's broad assurance that reasonable costs entirely neutralize Markowitz's advantage is replaced by these metric- and market-specific results.

## 6.5 Paired Sharpe differences

Table 5 reports observed differences, percentile intervals and approximate two-sided probabilities at 10 basis points. Figure 6 displays the six primary comparisons and the three distinct matched-cap BL-Markowitz comparisons. The repeated inactive-cap BL/1N results remain identified in the table rather than counted as additional independent findings.

[[TABLE5]]

[[FIGURE6]]

The unrestricted BL-minus-Markowitz Sharpe differences are {{5|US|Markowitz|Sharpe Difference A minus B|f6|cap=1}}, {{5|China|Markowitz|Sharpe Difference A minus B|f6|cap=1}} and {{5|India|Markowitz|Sharpe Difference A minus B|f6|cap=1}}, with p-values {{5|US|Markowitz|Two-sided P-value|p4|cap=1}}, {{5|China|Markowitz|Two-sided P-value|p4|cap=1}} and {{5|India|Markowitz|Two-sided P-value|p4|cap=1}}. The BL-minus-1/N probabilities are {{5|US|Equal-weight|Two-sided P-value|p4|cap=1}}, {{5|China|Equal-weight|Two-sided P-value|p4|cap=1}} and {{5|India|Equal-weight|Two-sided P-value|p4|cap=1}}. The matched-cap BL-Markowitz probabilities are {{5|US|Markowitz|Two-sided P-value|p4|cap=0.4}}, {{5|China|Markowitz|Two-sided P-value|p4|cap=0.4}} and {{5|India|Markowitz|Two-sided P-value|p4|cap=0.4}}.

No statistically significant Sharpe-ratio differences were established under the specified paired bootstrap procedure. All reported intervals include zero, and no unadjusted p-value is below 0.05. This does not establish exact equivalence, validate a causal mechanism or demonstrate that all economically relevant differences are zero. It limits how strongly this experiment can support superiority claims. These results also cannot be substituted for the original manuscript's unreproduced volatility and ASI tests.

## 6.6 Historical crisis behavior

Table 6 retains the primary Phase 1 standalone frozen-holdings stress results. US GFC buy-and-hold drawdown is {{6|US|Black-Litterman|Buy-Hold Max Drawdown|pct4}} for BL and {{6|US|Markowitz|Buy-Hold Max Drawdown|pct4}} for Markowitz. The corresponding trough-to-crisis-start-NAV recovery durations are {{6|US|Black-Litterman|Buy-Hold Recovery Trading Days|int}} and {{6|US|Markowitz|Buy-Hold Recovery Trading Days|int}} trading-index positions. BL is worse on both descriptive outcomes in that event.

[[TABLE6]]

For the China event, BL's drawdown is {{6|China|Black-Litterman|Buy-Hold Max Drawdown|pct4}} versus {{6|China|Markowitz|Buy-Hold Max Drawdown|pct4}}, with recovery durations of {{6|China|Black-Litterman|Buy-Hold Recovery Trading Days|int}} versus {{6|China|Markowitz|Buy-Hold Recovery Trading Days|int}}. In India, drawdowns are {{6|India|Black-Litterman|Buy-Hold Max Drawdown|pct4}} versus {{6|India|Markowitz|Buy-Hold Max Drawdown|pct4}}, and recovery durations are {{6|India|Black-Litterman|Buy-Hold Recovery Trading Days|int}} versus {{6|India|Markowitz|Buy-Hold Recovery Trading Days|int}}. The event pattern is mixed; it does not support universal crisis protection.

The fixed-holdings design deliberately excludes adaptive trading during each stress evaluation. It therefore cannot show that a strategy reduces capitulation-driven allocation changes during the crisis, nor does comparison with an index's historical recovery date validate these portfolio-specific results. Daily frozen-holdings curves were not retained in the verified archive, so no crisis curve is inserted. The summary evidence and its source limitations are preserved rather than reverse-engineering a visually plausible path.

## 6.7 US factor exposures

Table 7 and Figure 7 present Phase 1's US four-factor diagnostic. Market beta is {{7|US|Black-Litterman|Coefficient|f6|term=MKT}} for BL and {{7|US|Markowitz|Coefficient|f6|term=MKT}} for Markowitz. No direct cross-strategy test of beta equality is supplied, so the estimates are not called statistically indistinguishable. The US BL SMB coefficient is positive and its HML coefficient is positive in the retained fit; the Markowitz size loading is negative, while its HML coefficient has substantial statistical uncertainty. Full coefficients and HAC inference are reported rather than inferring their signs from a figure alone.

[[TABLE7]]

[[FIGURE7]]

The momentum coefficient is {{7|US|Black-Litterman|Coefficient|f6|term=MOM}} for BL, with HAC p={{7|US|Black-Litterman|HAC p-value|p4|term=MOM}}, and {{7|US|Markowitz|Coefficient|f6|term=MOM}} for Markowitz, with p={{7|US|Markowitz|HAC p-value|p4|term=MOM}}. The latter is a statistically strong conditional US loading, not proof that optimization causally generates a momentum strategy or that it explains China/India performance.

BL's arithmetic annualized alpha is {{7|US|Black-Litterman|Alpha Annualized Arithmetic|pct4|term=Alpha}}, with p={{7|US|Black-Litterman|HAC p-value|p4|term=Alpha}}; Markowitz's is {{7|US|Markowitz|Alpha Annualized Arithmetic|pct4|term=Alpha}}, with p={{7|US|Markowitz|HAC p-value|p4|term=Alpha}}. Neither establishes positive active alpha under this regression. The model's R-squared and statistical associations are conditional descriptive evidence. These estimates were not refitted to the Phase 2 capped or 1/N paths, even though the principal experiments use the same frozen price vintage and OOS coverage.

## 6.8 Fixed-tau sensitivity

Table 8 and Figure 8 retain the five verified Phase 1 US fixed-tau settings. Sharpe changes from {{8|US|*|Sharpe Ratio|f6|tau=0.01}} at tau 0.01 to {{8|US|*|Sharpe Ratio|f6|tau=0.2}} at tau 0.20. The small decline is descriptive of this uncertainty scale, view construction, ETF basket and sample. It is not a search for the best tau or a demonstration of general robustness outside the tested values.

[[TABLE8]]

[[FIGURE8]]

Omega is independent of tau in these runs, so tau does not mechanically cancel from the posterior update. The five fixed scenarios are separate from the main trailing-volatility adaptive rule. The close-to-1/N behavior in the principal experiment remains a limitation on interpreting small fixed-tau differences as evidence of incremental predictive skill.

# 7 Discussion and implementation implications

The clearest implementation result is lower target instability and turnover for equilibrium-anchored BL relative to unrestricted historical-mean Markowitz. This supports the practical value of examining allocation mechanics rather than ranking methods by a single return statistic. It does not establish that the BL framework, regardless of prior and views, intrinsically suppresses trades or dominates alternative estimators.

The 1/N comparison changes the interpretation of stabilization. In these baskets, a recurring equal-weight target produces very similar investment outcomes without estimating a historical-mean view tilt. BL's strong equal-weight anchor therefore explains much of the observed behavior. Stabilizing an optimization input is not the same as generating incremental investment alpha, and failure to reject a Sharpe difference is not proof that the procedures are equivalent. The appropriate claim is narrow: this specified anchored implementation is far more stable than the unrestricted comparator and has not demonstrated superior performance over 1/N.

Matched concentration constraints identify another alternative explanation. Capped Markowitz is less concentrated and trades less, with improved US and China Sharpe, though reduced India Sharpe. The results show why an empirical claim about the benefit of expected-return shrinkage depends on the feasible set used by the comparator. They do not justify choosing a cap after observing performance or treating the predefined 40% setting as universally optimal.

For implementation, the distinction between trading and target changes remains important. A stable target still requires trades as holdings drift. The simulation charges initial deployment, models proportional costs consistently and separates fee expenditure from investment growth. It does not establish capacity, execution quality or institutional feasibility at any asset scale. Microstructure costs can be nonlinear and endogenous to order size, liquidity and stress; none is estimated here. The original institutional-grade language is therefore replaced by a discussion of modeled trade-offs.

The crisis and factor results are complementary diagnostics, not causal explanations of the main comparison. Event-specific frozen portfolios can recover to their starting capital at different times because they have different holdings. US factor coefficients summarize one specified return series and risk model. Neither diagnostic establishes universal downside protection, an ownership mechanism or prospective regime timing. These distinctions are necessary to keep a cross-market descriptive study from claiming more identification than its design supplies.

# 8 Limitations

The ETF universes contain only four or five instruments and overlapping exposures. They are useful for a transparent allocation exercise but do not represent a high-dimensional stock-selection problem or every investable opportunity in the named countries. ETF aggregation suppresses firm-level variation, so results cannot be generalized directly to constituent-level covariance estimation, ownership effects or other market structures.

The instruments are US-listed and USD-denominated. Provider-adjusted histories are return proxies subject to vendor revisions, not local-currency national-index series or executable prices. Different observed histories generate unequal effective samples, preventing a common-horizon cross-market ranking. Survivorship and universe-selection effects are not eliminated by consistent arithmetic or verified code.

The BL prior is an equal-weight proxy. Its views are a mild historical-return tilt, and risk aversion, uncertainty scaling and tau rules are assumed rather than estimated as optimal investor preferences. Strong anchoring may account for much of the stability and near-1/N performance. These results do not assess independent analyst forecasts, observed capitalization priors or all alternative BL specifications.

Transaction costs are intentionally stylized. The model does not capture time-varying bid-ask spreads, nonlinear price impact, taxes, financing, execution constraints or liquidity stress. The assumed fees are not necessarily conservative bounds on actual implementation costs. The weight-turnover convention also differs from other reported turnover definitions, so rates cannot be transferred mechanically to an institutional trading-cost forecast.

Inference uses one predefined block length, replication count, seed and approximate centering convention. Percentile intervals and unadjusted multiple comparisons do not guarantee exact finite-sample coverage. Selected historical events are not a representative distribution of future crises, and the retained summary archive does not contain verified daily frozen-holdings curves. Descriptive drawdown differences have no associated test of superior downside protection.

The factor model is US-only. Its return convention subtracts the actual factor-library RF, while headline Sharpe assumes zero RF. Ex-post Markov smoothing is not a trading rule and cannot support real-time regime prediction. Fixed-tau sensitivity covers only five scenarios under the retained specification. Original March price/factor vintages, dated capitalization priors, ownership records and some original test artifacts remain unavailable. These gaps prevent exact reproduction of that historical empirical record, without invalidating the narrower revised-study findings supported by the frozen evidence.

# 9 Future research

Future work should distinguish the information content of independently sourced views from the diversification induced by the reference allocation. Broader universes and clearly documented contemporaneous priors would help assess whether the near-1/N result persists beyond these ETF baskets. A common-period international design could separate horizon effects from differences in exposures more directly.

Execution-aware portfolio choice and genuinely prospective regime evaluation are separate research projects, not completed components of this revision. An ownership study would require real dated classifications and stock-level return histories; no inference about SOE or private-company protection is retained from the unavailable original inputs. These directions identify limits of the present contribution rather than implying that a more complicated model must improve realized performance.

# 10 Reproducibility and revision history

The repository is https://github.com/amitdudi04/regime-sensitive-black-litterman-tri-market-study. The Phase 3 evidence freeze is commit da5d40acfc0e71cac51f0fd8bc288606c6c7aa71 on research/revised-paper-phase3-final-results. Its generation source is recorded as 69112e3abc1997df04387e916e04285cb6cbf87d. Phase 2 principal evidence comes from run ff8cacdc-95f8-458e-8d71-d12efbd9a9f9, executed at af84ddfbc93edc7a5143c654d6319d67e3139eef and frozen on 7553cf8bff59a4f3d8bad7d15b779707fc533fa1. Phase 1 supplementary evidence retains run 693ec4b2-0e95-4367-afef-904dbac8f9c3, executed at f7f96e3c6646e7b171c43b8bb6e8a5b129053609 and archived on completed Phase 1 commit 598fe0d3c0a7cd7ebaf5709ae62b7c6735b92a0d.

The verified numerical environment uses Python 3.12 with observed dependency versions pinned in requirements-phase1-lock.txt. Run manifests record exact versions, configuration, request/effective dates, retrieval timestamps, frozen price checksums, aligned factor fingerprints and output hashes. The revised calculation convention uses Adj Close simple returns, common observed dates and the constraints and fee definitions described above. Manuscript generation reads the eight CSV tables and verified figures directly; numerical prose is linked to source cells rather than entered independently.

The completed validation sequence includes independent financial identities, new-experiment accounting checks and publication-level table/figure consistency checks. These are software and internal-consistency evidence, not proof that a selected empirical model is economically optimal. No backtest, bootstrap distribution or market-data download is repeated to prepare this manuscript. Synthetic test fixtures used in earlier software checks are distinct from empirical research reruns.

Raw vendor snapshots remain local and are not redistributed as part of the public paper. Public data access does not by itself establish a right to redistribute vendor histories. A lawful fresh acquisition may differ from the frozen vintage; exact rerun claims require matching source bytes and configuration. Portfolio return paths and decisions are included in the preserved evidence package for tracing the generated figures. Reproducing the revised frozen experiment, obtaining internally consistent new downloads and reproducing the March paper are three different claims.

Revision note dated 31 October 2026: this revision updates portfolio accounting documentation, sample definitions, equal-weight benchmarking, matched concentration comparisons, cost sensitivity and statistical interpretation. Empirical values differ from the March 2026 version. The revised study uses a clearly specified equal-weight equilibrium proxy and verified ETF windows; missing original inputs prevent a unique attribution of every historical numerical difference. The original manuscript and transcribed tables remain unchanged for historical reference. This author-review manuscript has not been submitted or approved as an SSRN revision.

# 11 Conclusion

In the evaluated ETF baskets, equilibrium-anchored BL produces substantially lower target-weight instability and modeled turnover than unrestricted historical-mean Markowitz. That finding is economically useful as a description of allocation behavior, but it does not establish general investment superiority. BL performs nearly like periodically rebalanced equal weighting, and a reasonable matched concentration cap materially reduces the comparator's instability.

Risk-adjusted results vary across markets, trading costs affect implementation outcomes and arithmetic-return rankings need not match compounded-wealth rankings. No statistically significant Sharpe-ratio differences were established under the specified paired bootstrap procedure. The crisis outcomes are event-specific, while US factor and fixed-tau diagnostics remain limited to their stated samples and designs. The contribution is a transparent empirical assessment of stabilization and implementation trade-offs, with unfavorable and insignificant findings retained. It supports careful benchmark and constraint selection rather than a universal preference for one portfolio model.

# Declarations

Funding and competing interests: the March 2026 version reported no external funding and no conflict of interest. Confirmation that these declarations remain accurate for the revised study is required from the author before submission.

Data availability: revised-study source code, result tables, figures, configuration and provenance are retained in the versioned repository and evidence package. Market prices originate from Yahoo Finance and US factor definitions from the Kenneth French Data Library. Raw vendor input redistribution is not asserted. Exact frozen-data access and matching checksums should accompany any claim of exact revised-study reproduction.

## Generative AI assistance declaration for author approval

OpenAI ChatGPT and Codex tools assisted with code inspection, mathematical-validation support, numerical-test preparation, empirical workflow preparation, research documentation, table and figure generation, and manuscript editing. The revised empirical results were taken from the frozen verified source outputs; tools were not used to fabricate missing market, ownership or historical-paper data. The assistance extended beyond linguistic refinement, so the earlier declaration is not carried forward unchanged.

The author must review the revised manuscript, references, numerical interpretations, code/evidence record and this disclosure before submission. AI tools do not assume authorship or responsibility. No statement is made here that the author has already completed that review or personally verified every new result. The final author-approved declaration should accurately describe actual human oversight and comply with the applicable SSRN and institutional requirements at submission.

# References

[[REFERENCES]]
