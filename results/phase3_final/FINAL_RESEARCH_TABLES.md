# Final research tables

Machine-readable CSVs retain source precision and explicit provenance. Percentages below are display conversions, not recalculated experiments.

## Table 1 — Dataset Definitions

| Market | ETF Universe | Currency | Common Price Start | Common Price End | Common Price Observations | OOS Start | OOS End | OOS Observations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US | SPY,QQQ,IWM,XLF,XLK | USD (US-listed ETFs) | 2010-01-04 | 2024-12-31 | 3774 | 2011-01-04 | 2024-12-31 | 3521 |
| China | ASHR,KWEB,MCHI,FXI | USD (US-listed ETFs) | 2013-11-06 | 2024-12-31 | 2806 | 2014-11-07 | 2024-12-31 | 2553 |
| India | INDA,EPI,SMIN,INDY | USD (US-listed ETFs) | 2012-02-09 | 2024-12-31 | 3244 | 2013-02-13 | 2024-12-31 | 2991 |

USD-listed ETFs. Price samples are common observed dates; OOS begins after 252 estimation sessions. Passive ETF reference and price counts are in the CSV. The research benchmark is rebalanced 1/N.

Table 1, benchmark definitions:

| Market | Rebalanced Strategy Benchmark | Passive ETF Reference |
| --- | --- | --- |
| US | 1/N, same universe and 63-session schedule | S&P 500 ETF proxy (SPY adjusted-close total return; portfolio constituent) |
| China | 1/N, same universe and 63-session schedule | CSI 300 ETF proxy (ASHR; also in the portfolio universe) |
| India | 1/N, same universe and 63-session schedule | Broad India ETF proxy (INDA adjusted-close total return; portfolio constituent) |

## Table 2 — Principal Performance

| Market | Model | Net Annualized Return | Annualized Volatility | Sharpe Ratio | Max Drawdown | Mean Rebalance L1 Turnover | ASI | Net Terminal Wealth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US | Black-Litterman | 15.4148% | 19.1023% | 0.806964 | -35.0693% | 2.8735% | 0.009409 | 6.667960 |
| US | Markowitz | 15.8896% | 21.3455% | 0.744400 | -31.1532% | 80.2868% | 0.805060 | 6.687777 |
| US | Equal-weight | 15.4183% | 19.0911% | 0.807620 | -35.0716% | 2.6123% | 0.000000 | 6.673219 |
| China | Black-Litterman | 5.8193% | 28.7549% | 0.202377 | -64.2506% | 3.5751% | 0.001479 | 1.189326 |
| China | Markowitz | 4.5276% | 30.2822% | 0.149513 | -65.2639% | 70.7290% | 0.712407 | 0.995031 |
| China | Equal-weight | 5.8210% | 28.7625% | 0.202381 | -64.2611% | 3.5848% | 0.000000 | 1.189269 |
| India | Black-Litterman | 10.8720% | 21.5867% | 0.503642 | -49.7382% | 1.7249% | 0.002346 | 2.750185 |
| India | Markowitz | 13.2072% | 22.6253% | 0.583735 | -47.5871% | 58.3411% | 0.585259 | 3.530754 |
| India | Equal-weight | 10.8700% | 21.5862% | 0.503564 | -49.7414% | 1.7618% | 0.000000 | 2.749585 |

Phase 2; net 10 bps per L1 turnover; 100% target cap; arithmetic annual mean, sample volatility, Sharpe RF=0. Wealth starts at 1 and compounds simple net returns. Rebalance turnover excludes initial cash deployment, which is separately 1 / 10 bps.

## Table 3 — Concentration Robustness

| Market | Model | Target Weight Cap | Net Annualized Return | Sharpe Ratio | Mean Rebalance L1 Turnover | Mean Target HHI | Return Change vs 100% Cap (bps) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| US | Black-Litterman | 100.0000% | 15.4148% | 0.806964 | 2.8735% | 0.200054 | 0.000000 |
| US | Markowitz | 100.0000% | 15.8896% | 0.744400 | 80.2868% | 0.877790 | 0.000000 |
| US | Black-Litterman | 40.0000% | 15.4148% | 0.806964 | 2.8735% | 0.200054 | 0.000000 |
| US | Markowitz | 40.0000% | 15.7193% | 0.797938 | 41.4349% | 0.358195 | -17.023390 |
| China | Black-Litterman | 100.0000% | 5.8193% | 0.202377 | 3.5751% | 0.250002 | 0.000000 |
| China | Markowitz | 100.0000% | 4.5276% | 0.149513 | 70.7290% | 0.884217 | 0.000000 |
| China | Black-Litterman | 40.0000% | 5.8193% | 0.202377 | 3.5751% | 0.250002 | 0.000000 |
| China | Markowitz | 40.0000% | 5.3984% | 0.194447 | 35.7818% | 0.353842 | 87.085256 |
| India | Black-Litterman | 100.0000% | 10.8720% | 0.503642 | 1.7249% | 0.250003 | 0.000000 |
| India | Markowitz | 100.0000% | 13.2072% | 0.583735 | 58.3411% | 0.875524 | 0.000000 |
| India | Black-Litterman | 40.0000% | 10.8720% | 0.503642 | 1.7249% | 0.250003 | 0.000000 |
| India | Markowitz | 40.0000% | 12.1747% | 0.555011 | 26.9045% | 0.358635 | -103.244321 |

Phase 2; matched BL/MV target bounds, 10 bps. Return change is capped minus the same strategy's 100% result, in annualized arithmetic basis points. The bound applies at rebalances, not continuously to drifting holdings.

## Table 4 — Transaction Cost Sensitivity

| Market | Model | Target Weight Cap | Cost (bps per L1) | Gross Annualized Return | Net Annualized Return | Net Terminal Wealth |
| --- | --- | --- | --- | --- | --- | --- |
| US | Black-Litterman | 100.0000% | 0 | 15.4334% | 15.4334% | 6.685192 |
| US | Black-Litterman | 100.0000% | 5 | 15.4334% | 15.4241% | 6.676571 |
| US | Black-Litterman | 100.0000% | 10 | 15.4334% | 15.4148% | 6.667960 |
| US | Black-Litterman | 100.0000% | 20 | 15.4334% | 15.3963% | 6.650765 |
| US | Markowitz | 100.0000% | 0 | 16.2137% | 16.2137% | 6.996950 |
| US | Markowitz | 100.0000% | 5 | 16.2137% | 16.0517% | 6.840677 |
| US | Markowitz | 100.0000% | 10 | 16.2137% | 15.8896% | 6.687777 |
| US | Markowitz | 100.0000% | 20 | 16.2137% | 15.5654% | 6.391815 |
| US | Black-Litterman | 40.0000% | 0 | 15.4334% | 15.4334% | 6.685192 |
| US | Black-Litterman | 40.0000% | 5 | 15.4334% | 15.4241% | 6.676571 |
| US | Black-Litterman | 40.0000% | 10 | 15.4334% | 15.4148% | 6.667960 |
| US | Black-Litterman | 40.0000% | 20 | 15.4334% | 15.3963% | 6.650765 |
| US | Markowitz | 40.0000% | 0 | 15.8900% | 15.8900% | 7.011731 |
| US | Markowitz | 40.0000% | 5 | 15.8900% | 15.8047% | 6.928808 |
| US | Markowitz | 40.0000% | 10 | 15.8900% | 15.7193% | 6.846833 |
| US | Markowitz | 40.0000% | 20 | 15.8900% | 15.5486% | 6.685690 |
| US | Equal-weight | 100.0000% | 0 | 15.4358% | 15.4358% | 6.689503 |
| US | Equal-weight | 100.0000% | 5 | 15.4358% | 15.4271% | 6.681357 |
| US | Equal-weight | 100.0000% | 10 | 15.4358% | 15.4183% | 6.673219 |
| US | Equal-weight | 100.0000% | 20 | 15.4358% | 15.4009% | 6.656967 |
| China | Black-Litterman | 100.0000% | 0 | 5.8433% | 5.8433% | 1.192220 |
| China | Black-Litterman | 100.0000% | 5 | 5.8433% | 5.8313% | 1.190772 |
| China | Black-Litterman | 100.0000% | 10 | 5.8433% | 5.8193% | 1.189326 |
| China | Black-Litterman | 100.0000% | 20 | 5.8433% | 5.7953% | 1.186437 |
| China | Markowitz | 100.0000% | 0 | 4.8185% | 4.8185% | 1.024632 |
| China | Markowitz | 100.0000% | 5 | 4.8185% | 4.6730% | 1.009729 |
| China | Markowitz | 100.0000% | 10 | 4.8185% | 4.5276% | 0.995031 |
| China | Markowitz | 100.0000% | 20 | 4.8185% | 4.2367% | 0.966239 |
| China | Black-Litterman | 40.0000% | 0 | 5.8433% | 5.8433% | 1.192220 |
| China | Black-Litterman | 40.0000% | 5 | 5.8433% | 5.8313% | 1.190772 |
| China | Black-Litterman | 40.0000% | 10 | 5.8433% | 5.8193% | 1.189326 |
| China | Black-Litterman | 40.0000% | 20 | 5.8433% | 5.7953% | 1.186437 |
| China | Markowitz | 40.0000% | 0 | 5.5500% | 5.5500% | 1.188534 |
| China | Markowitz | 40.0000% | 5 | 5.5500% | 5.4742% | 1.179467 |
| China | Markowitz | 40.0000% | 10 | 5.5500% | 5.3984% | 1.170467 |
| China | Markowitz | 40.0000% | 20 | 5.5500% | 5.2468% | 1.152663 |
| China | Equal-weight | 100.0000% | 0 | 5.8450% | 5.8450% | 1.192168 |
| China | Equal-weight | 100.0000% | 5 | 5.8450% | 5.8330% | 1.190718 |
| China | Equal-weight | 100.0000% | 10 | 5.8450% | 5.8210% | 1.189269 |
| China | Equal-weight | 100.0000% | 20 | 5.8450% | 5.7969% | 1.186376 |
| India | Black-Litterman | 100.0000% | 0 | 10.8872% | 10.8872% | 2.755170 |
| India | Black-Litterman | 100.0000% | 5 | 10.8872% | 10.8796% | 2.752677 |
| India | Black-Litterman | 100.0000% | 10 | 10.8872% | 10.8720% | 2.750185 |
| India | Black-Litterman | 100.0000% | 20 | 10.8872% | 10.8567% | 2.745205 |
| India | Markowitz | 100.0000% | 0 | 13.4475% | 13.4475% | 3.632617 |
| India | Markowitz | 100.0000% | 5 | 13.4475% | 13.3274% | 3.581343 |
| India | Markowitz | 100.0000% | 10 | 13.4475% | 13.2072% | 3.530754 |
| India | Markowitz | 100.0000% | 20 | 13.4475% | 12.9668% | 3.431601 |
| India | Black-Litterman | 40.0000% | 0 | 10.8872% | 10.8872% | 2.755170 |
| India | Black-Litterman | 40.0000% | 5 | 10.8872% | 10.8796% | 2.752677 |
| India | Black-Litterman | 40.0000% | 10 | 10.8872% | 10.8720% | 2.750185 |
| India | Black-Litterman | 40.0000% | 20 | 10.8872% | 10.8567% | 2.745205 |
| India | Markowitz | 40.0000% | 0 | 12.2899% | 12.2899% | 3.224491 |
| India | Markowitz | 40.0000% | 5 | 12.2899% | 12.2323% | 3.202563 |
| India | Markowitz | 40.0000% | 10 | 12.2899% | 12.1747% | 3.180777 |
| India | Markowitz | 40.0000% | 20 | 12.2899% | 12.0596% | 3.137628 |
| India | Equal-weight | 100.0000% | 0 | 10.8854% | 10.8854% | 2.754617 |
| India | Equal-weight | 100.0000% | 5 | 10.8854% | 10.8777% | 2.752100 |
| India | Equal-weight | 100.0000% | 10 | 10.8854% | 10.8700% | 2.749585 |
| India | Equal-weight | 100.0000% | 20 | 10.8854% | 10.8546% | 2.744559 |

Phase 2; all four cost assumptions and both optimized caps. Arithmetic annual return and compounded terminal wealth are distinct metrics. Gross paths and trading decisions are reused across costs. Full cost expenditure and turnover are retained in CSV.

## Table 5 — Statistical Comparisons

| Market | Target Weight Cap | Strategy B | Sharpe Difference A minus B | 95% CI Lower | 95% CI Upper | Two-sided P-value | Paired Observations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| US | 100.0000% | Markowitz | 0.062564 | -0.136167 | 0.277879 | 0.5370 | 3521 |
| US | 100.0000% | Equal-weight | -0.000656 | -0.001556 | 0.000285 | 0.1725 | 3521 |
| US | 40.0000% | Markowitz | 0.009026 | -0.107492 | 0.141051 | 0.8905 | 3521 |
| US | 40.0000% | Equal-weight | -0.000656 | -0.001556 | 0.000285 | 0.1725 | 3521 |
| China | 100.0000% | Markowitz | 0.052864 | -0.215295 | 0.320003 | 0.6915 | 2553 |
| China | 100.0000% | Equal-weight | -0.000004 | -0.000377 | 0.000382 | 0.9835 | 2553 |
| China | 40.0000% | Markowitz | 0.007930 | -0.091777 | 0.100244 | 0.8725 | 2553 |
| China | 40.0000% | Equal-weight | -0.000004 | -0.000377 | 0.000382 | 0.9835 | 2553 |
| India | 100.0000% | Markowitz | -0.080092 | -0.213058 | 0.064457 | 0.2735 | 2991 |
| India | 100.0000% | Equal-weight | 0.000079 | -0.000176 | 0.000304 | 0.5070 | 2991 |
| India | 40.0000% | Markowitz | -0.051369 | -0.113396 | 0.013004 | 0.1110 | 2991 |
| India | 40.0000% | Equal-weight | 0.000079 | -0.000176 | 0.000304 | 0.5070 | 2991 |

Phase 2; BL minus comparator at net 10 bps, paired 20-session circular bootstrap, 2,000 iterations, seed 42. Same-date block indices preserve pairing. Approximate empirical-mean-centered null; two-sided p-values, percentile 95% intervals, no multiplicity adjustment. Capped BL/1N duplicates inactive-cap comparisons.

## Table 6 — Crisis Stress Tests

| Market | Model | Requested Crisis Start | Requested Crisis End | Buy-Hold Max Drawdown | Buy-Hold Trough Date | Buy-Hold Recovery Date | Buy-Hold Recovery Trading Days |
| --- | --- | --- | --- | --- | --- | --- | --- |
| US | Black-Litterman | 2008-08-01 | 2009-03-09 | -52.1204% | 2009-03-09 | 2010-04-14 | 277 |
| US | Markowitz | 2008-08-01 | 2009-03-09 | -46.9902% | 2008-11-20 | 2009-12-22 | 273 |
| China | Black-Litterman | 2015-06-01 | 2016-02-01 | -36.9642% | 2016-01-28 | 2017-07-26 | 376 |
| China | Markowitz | 2015-06-01 | 2016-02-01 | -49.7631% | 2016-01-28 | 2020-11-04 | 1202 |
| India | Black-Litterman | 2020-02-15 | 2020-05-01 | -42.5592% | 2020-03-23 | 2020-11-06 | 160 |
| India | Markowitz | 2020-02-15 | 2020-05-01 | -41.7125% | 2020-03-23 | 2020-11-09 | 161 |

Phase 1 standalone gross stress test; last target strictly before event, purchased before first event return, no further trades through recovery. Recovery target is crisis-start NAV 1, duration is trading-index positions from crisis-window maximum-drawdown trough to first subsequent recovery. This is neither recovery to the previous peak nor time from crisis start. Missing recovery is censored. Legacy weighted-log metrics are excluded.

## Table 7 — Us Factor Exposures

| Model | Term | Coefficient | HAC t-statistic | HAC p-value | Alpha Annualized Arithmetic | Observations | HAC Max Lags |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Black-Litterman | Alpha | 0.000019 | 0.839222 | 0.4013 | 0.004868 | 3521 | 5 |
| Black-Litterman | MKT | 1.063528 | 247.378806 | <0.0001 | — | 3521 | 5 |
| Black-Litterman | SMB | 0.073759 | 11.975850 | <0.0001 | — | 3521 | 5 |
| Black-Litterman | HML | 0.031096 | 4.928017 | <0.0001 | — | 3521 | 5 |
| Black-Litterman | MOM | 0.004003 | 0.736257 | 0.4616 | — | 3521 | 5 |
| Markowitz | Alpha | -0.000045 | -0.555258 | 0.5787 | -0.011363 | 3521 | 5 |
| Markowitz | MKT | 1.148195 | 108.565686 | <0.0001 | — | 3521 | 5 |
| Markowitz | SMB | -0.047236 | -2.018287 | 0.0436 | — | 3521 | 5 |
| Markowitz | HML | -0.021556 | -0.783129 | 0.4336 | — | 3521 | 5 |
| Markowitz | MOM | 0.224115 | 16.181575 | <0.0001 | — | 3521 | 5 |

Phase 1 US-only daily Rp−RF on US FF3+momentum, source percentages divided by 100, intercept OLS with Newey–West/HAC maxlags 5. Sample 2011-01-04–2024-12-31, 3,521 observations. Coefficient alpha is daily; the annual alpha column multiplies by 252. Blank annual alpha for beta rows is not missing estimation evidence. These are not refitted Phase 2 capped/1N regressions.

## Table 8 — Tau Sensitivity

| Market | Tau | Sharpe Ratio | OOS Start | OOS End | OOS Observations |
| --- | --- | --- | --- | --- | --- |
| US | 0.010000 | 0.807438 | 2011-01-04 | 2024-12-31 | 3521 |
| US | 0.050000 | 0.806660 | 2011-01-04 | 2024-12-31 | 3521 |
| US | 0.100000 | 0.805679 | 2011-01-04 | 2024-12-31 | 3521 |
| US | 0.150000 | 0.804723 | 2011-01-04 | 2024-12-31 | 3521 |
| US | 0.200000 | 0.803797 | 2011-01-04 | 2024-12-31 | 3521 |

Phase 1 US fixed-tau net 10 bps runs, same universe/window/constraints/cost convention. Omega independent of tau. Distinct from the main strategy's ex-ante trailing-volatility tau selection; no tuning or new optimization in Phase 3.
