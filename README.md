# Black–Litterman and Markowitz Across Three ETF Markets

**Portfolio stability, turnover, and out-of-sample risk**  
Research implementation by Amit Kumar Dudi

The [Phase 1 financial validation](docs/PHASE1_FINANCIAL_VALIDATION.md) records 71 passing tests, independent financial identities, complete current-data execution, a frozen-input baseline comparison and deterministic repeatability. Its `READY_WITH_LIMITATIONS` decision applies to the revised research implementation; original-paper reproduction remains unestablished.

This study compares equilibrium-anchored Black–Litterman allocation with historical-mean Markowitz optimization in ETF baskets representing the United States, China, and India. It asks whether more stable portfolio targets translate into lower trading turnover, and whether that stability is accompanied by better investment performance.

The repository contains a corrected, test-validated **2026 diagnostic implementation** and an **earlier research manuscript**: *Black–Litterman vs. Markowitz: Stability, Turnover, and Crisis Dynamics Across Global Markets* (March 2026, SSRN 6479462). The manuscript's reported results have **not** been numerically reproduced by the current code. They are retained separately, not represented as verified outputs of the corrected study.

## Data and method

| Market | Investable ETFs | Corrected main out-of-sample window |
|---|---|---|
| US | SPY, QQQ, IWM, XLF, XLK | 2011-01-04 to 2024-12-31 |
| China | ASHR, KWEB, MCHI, FXI | 2014-11-07 to 2024-12-31 |
| India | INDA, EPI, SMIN, INDY | 2013-02-13 to 2024-12-31 |

The configured main download starts on 2010-01-01 and ends **before** 2025-01-01. ETF listing histories and the 252-session estimation window shorten the effective out-of-sample periods. The 2008 US crisis is evaluated in a distinct historical crisis sample, not as part of the main backtest.

Both strategies use the same Ledoit–Wolf covariance estimate, 252-session training windows, long-only fully invested optimization, and rebalancing every 63 trading sessions. Portfolio weights **drift naturally between rebalances**. The current model applies 10 basis points per unit of L1 traded-weight turnover, including a separately reported initial investment from cash.

Markowitz uses rolling historical means. Black–Litterman uses the equilibrium-implied vector \(\Pi = \lambda\Sigma w_{eq}\) and absolute views \(Q = \Pi + 0.10(\mu_{hist}-\Pi)\). **The default equilibrium weights are equal-weight proxies, not observed capitalization weights.** Dated, historical capitalization/AUM weights can be supplied as-of the training cutoff, but the original manuscript's historical capitalization input data have not been recovered.

“Regime-sensitive” refers to an **ex-ante training-window volatility rule used to choose** \(\tau\). The separate Markov-switching analysis uses **ex-post smoothed** states for description; it does not drive trading decisions.

## Corrected-pipeline findings

These are results from the [October 2026 corrected-pipeline audit](docs/EMPIRICAL_AUDIT_2026-10-30.md), not values reproduced from the March manuscript. The table reports **net arithmetic annualized simple returns**, zero-risk-free-rate Sharpe ratios, drift-adjusted rebalance turnover, and mean L1 changes in target allocations (ASI).

| Market | Method | Annualized return | Sharpe | Mean rebalance L1 turnover | ASI |
|---|---|---:|---:|---:|---:|
| US | Black–Litterman | 15.41% | 0.807 | 2.87% | 0.00941 |
| US | Markowitz | 15.89% | 0.744 | 80.29% | 0.80506 |
| China | Black–Litterman | 5.82% | 0.202 | 3.58% | 0.00148 |
| China | Markowitz | 4.53% | 0.150 | 70.73% | 0.71241 |
| India | Black–Litterman | 10.87% | 0.504 | 1.72% | 0.00235 |
| India | Markowitz | 13.21% | 0.584 | 58.34% | 0.58526 |

The revised Black–Litterman strategy changes target weights less frequently and incurs substantially lower modeled turnover in all three baskets. Its Sharpe ratio is higher in the US and China, but **lower in India**. The comparison does not show universal return or drawdown dominance. Markowitz is sometimes highly concentrated because the optimization permits up to 100% in one ETF.

A new paired 20-session circular-block bootstrap (2,000 iterations; seed 42) gives BL-minus-Markowitz Sharpe p-values of **0.5370 (US), 0.6915 (China), and 0.2735 (India)**. None is below 0.05; these tests are distinct from the manuscript's original volatility and ASI hypotheses. Markov-state performance is **descriptive and ex-post**, not a trading validation.

## Published paper versus current implementation

The manuscript reports different returns, risk metrics, factor coefficients, crisis outcomes, and tau sensitivity. Automated comparison of its historical performance, crisis and tau reference CSVs against the revised pipeline found **59 numerical mismatches** and **12 benchmark values that are not directly comparable because different instruments were used**, across 71 checked cells. No cell qualified as an exact match under the specified comparison tolerance.

This difference cannot be resolved by rounding or altering published tables. The original dated capitalization/AUM inputs, full historical price snapshots, optimizer allocations, and some original hypothesis-testing inputs have not been recovered. The paper also contains figure annotations and interpretations that need a documented manuscript revision. Until then, **do not cite the corrected figures as reproducing the March 2026 manuscript**.

The historical numbers are preserved unchanged in [`results/paper_results/`](results/paper_results/). For the full distinction between published, earlier diagnostic, and corrected-run findings, see [research reconciliation](docs/RESULTS_RECONCILIATION.md).

## Reproduce and examine

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m pipelines.run_tri_market_pipeline
python -m scripts.verify_paper_results
python -m scripts.validate_generated_outputs
python scripts/generate_research_figures.py
```

The current test suite had **35 passing tests** in the [verified GitHub Actions run](https://github.com/amitdudi04/regime-sensitive-black-litterman-tri-market-study/actions/runs/40942721530). That run completed the three-market pipeline, crisis and fixed-tau analyses, supplementary regime/Sharpe diagnostics, and output-invariant validation. Passing these checks demonstrates **internal consistency**, not historical-paper replication.

Price data come from Yahoo Finance via `yfinance`. The pipeline records per-market effective dates, download timestamps, checksums and factor-data fingerprints. Raw downloaded snapshots are excluded from version control, so a later fresh-data run may not exactly reproduce the archived output; see [methodology and data limitations](docs/METHODOLOGY.md). The current factor regression is US-only. The separate ownership-analysis helper requires **real, dated Chinese stock classifications and returns** and does not reproduce the paper's SOE/private table without them.

## Further documentation

- [Methodology and return conventions](docs/METHODOLOGY.md)
- [Architecture and output flow](docs/ARCHITECTURE.md)
- [Most recent validated diagnostic and numerical evidence](docs/EMPIRICAL_AUDIT_2026-10-30.md)
- [Published-results reconciliation, including the archived October 13 diagnostic](docs/RESULTS_RECONCILIATION.md)
- [Manuscript issues requiring evidence or formal revision](docs/REVIEWER_CORRECTIONS.md)
- [31 October paper-reproduction assessment: cost, wealth-curve and data discrepancies](docs/MANUSCRIPT_REPRODUCTION_ASSESSMENT_2026-10-31.md)

**Scope and limitations:** Small ETF baskets, unequal sample histories, an equal-weight default prior, proportional transaction-cost assumptions, selected historical stress events, and ex-post regime classifications limit generalization. The aim is to assess allocation stability and risk tradeoffs transparently—not to establish that Black–Litterman is superior in every market.
