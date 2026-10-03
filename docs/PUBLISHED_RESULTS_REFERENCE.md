# Published Working-Paper Result Reference

These tables reproduce values reported in the existing working paper. They are included for comparison during reconciliation and are **not** represented as fresh outputs from the cleaned pipeline.

## Primary performance table

| Market | Model | Return | Volatility | Sharpe | Turnover | ASI | Max Drawdown |
|---|---|---:|---:|---:|---:|---:|---:|
| US | Black-Litterman | 12.99% | 20.00% | 0.650 | 0.20% | 0.001632 | -38.04% |
| US | Markowitz | 13.24% | 21.57% | 0.614 | 1.58% | 0.015365 | -33.95% |
| US | Benchmark | 13.19% | 19.83% | 0.665 | N/A | N/A | -37.87% |
| China | Black-Litterman | 1.20% | 28.45% | 0.042 | 0.08% | 0.000391 | -68.07% |
| China | Markowitz | 2.64% | 30.19% | 0.088 | 1.12% | 0.010772 | -68.58% |
| China | Benchmark | 1.20% | 28.74% | 0.042 | N/A | N/A | -68.66% |
| India | Black-Litterman | 7.60% | 21.34% | 0.356 | 0.07% | 0.000322 | -53.67% |
| India | Markowitz | 9.76% | 22.18% | 0.440 | 0.82% | 0.007822 | -50.07% |
| India | Benchmark | 7.54% | 21.33% | 0.353 | N/A | N/A | -53.78% |

## Crisis reference

| Crisis | Model | Max Drawdown | Volatility Spike | Recovery |
|---|---|---:|---:|---:|
| US 2008 GFC | Black-Litterman | -62.57% | 1.94x | 1093 trading days |
| US 2008 GFC | Markowitz | -62.18% | 1.93x | 1056 trading days |
| China 2015 crash | Black-Litterman | -43.42% | 1.92x | 458 trading days |
| China 2015 crash | Markowitz | -43.82% | 1.95x | 459 trading days |
| India 2020 COVID | Black-Litterman | -47.44% | 3.39x | 176 trading days |
| India 2020 COVID | Markowitz | -47.48% | 3.40x | 176 trading days |

## Tau sensitivity reported in the paper

| Tau | Reported BL Sharpe |
|---:|---:|
| 0.01 | 0.3993 |
| 0.05 | 0.3983 |
| 0.10 | 0.3949 |
| 0.15 | 0.3929 |
| 0.20 | 0.3926 |

## Interpretation discipline

These values should be described as “reported in the working paper” until reproduced by the cleaned pipeline. See PAPER_ERRATA.md and RECONCILIATION_STATUS.md.
