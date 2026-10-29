# Methodology

This document describes the current public implementation, not a claim that the published manuscript has been computationally reproduced. Where the implementation and manuscript differ, retain the published values separately and see [the results reconciliation](RESULTS_RECONCILIATION.md).

## Market universe and sample windows

The study uses liquid ETF baskets representing three equity markets:

- US: SPY, QQQ, IWM, XLF, XLK
- China: ASHR, KWEB, MCHI, FXI
- India: INDA, EPI, SMIN, INDY

The main sample is requested from 2010-01-01 through 2024-12-31; the configured end date 2025-01-01 is exclusive. Each market uses the common observed history available across its ETF basket. Crisis analysis uses a separate historical sample requested from 2005-01-01 so the 2008 US event is not misrepresented as part of the main 2010–2024 sample. The actual effective dates and observation counts are written to `results/generated/dataset_manifest.csv`.

## Data snapshots and repeatability

The pipeline saves the exact adjusted-close price matrices under `results/generated/price_data/`, together with request metadata, retrieval timestamp, and SHA-256 checksum. The folder is excluded from Git. When `prefer_local_price_snapshot: true`, a matching request reuses the checksum-verified local matrix; a changed request reacquires data. Set the flag to `false` or remove the snapshot directory to refresh provider data. This supports local repeatability, but the raw input snapshots are not part of the public Git release.

## Rolling design

The backtest uses:

- 252 trading days for estimation;
- 63 trading days between rebalances;
- Ledoit-Wolf covariance shrinkage;
- long-only weights;
- full investment;
- 10 bps proportional transaction cost per unit of L1 turnover.

No future observation is used when estimating a rebalance-date portfolio. Between the 63-session scheduled rebalances the live portfolio is **buy-and-hold**, not a daily rebalanced constant-mix portfolio. Daily portfolio simple returns use weights drifted by preceding realized asset returns. The drifted holdings at the end of the interval are the pre-trade holdings used at the next scheduled rebalance. This correction changes current-run strategy results relative to previous diagnostics; it does not revise the manuscript's historical tables.

## Markowitz portfolio

Expected returns are estimated from the historical mean inside each rolling training window. The same covariance matrix, optimizer and weight constraints used for Black-Litterman are also used for Markowitz.

## Black-Litterman portfolio

Equilibrium-implied expected returns are:

\[
\Pi = \lambda \Sigma w_{eq}
\]

The public implementation defaults to **equal equilibrium weights** (`equal_weight_proxy`). It does not currently construct a historical market-capitalization-implied prior. A static normalized equilibrium-weight series can be supplied, or a date-indexed DataFrame of historical capitalization/AUM weights can be supplied when the underlying evidence exists. For dated priors, the backtest selects the latest valid row no later than the last training observation, never a future AUM observation. The selected weights and prior source date are written to each market's `equilibrium_prior_history.csv`. The default pipeline **still uses equal-weight proxies** because the dated market-cap/AUM evidence is unavailable; dated-prior support does not reconstruct missing historical research data. Manuscript language that calls the current default a market-cap-weighted prior must therefore be corrected.

Absolute ETF views use:

\[
Q = \Pi + 0.10(\mu_{hist} - \Pi)
\]

with an identity view matrix and diagonal view uncertainty.

The prior scaling parameter (\(\tau\)) follows a pre-specified volatility-threshold rule using only observations inside the training window. The separate two-state Markov-switching analysis is an ex-post diagnostic; its smoothed probabilities do not drive portfolio weights.

## Turnover and transaction costs

Before every rebalance after the first, the previous portfolio is drifted using realized asset returns from the preceding holding period. Turnover is calculated from the difference between drifted pre-trade weights and new target weights, and transaction cost is charged once on the first return after the rebalance.

The first out-of-sample portfolio is assumed to be deployed from cash. Its one-way L1 deployment turnover is the sum of absolute target weights (1.0 for a fully invested long-only portfolio), and the associated cost is charged on the first out-of-sample return. The reported average rebalancing turnover excludes this initial deployment, which is reported separately in the generated summary. This convention avoids silently treating the initial investment as cost-free.

## Allocation Stability Index

ASI measures the mean L1 change in target weights between consecutive rebalances:

\[
ASI_t = \sum_i |w_{i,t} - w_{i,t-1}|
\]

ASI is a target-allocation stability measure. It is distinct from drift-adjusted trading turnover and does not include initial deployment. The first undefined consecutive-weight difference is excluded from the mean rather than counted as a zero observation.

## Performance metrics

Portfolio P&L uses simple daily returns. Annualized return is the arithmetic mean daily return multiplied by 252; annualized volatility is the sample standard deviation multiplied by \(\sqrt{252}\). The reported Sharpe ratio uses a zero risk-free-rate assumption, so it should not be interpreted as a risk-free-adjusted Sharpe. The same convention is applied to the strategy and benchmark rows for comparability.

## Benchmark return convention

The generated comparison uses adjusted-close ETF proxies: SPY for the US, ASHR for China, and INDA for India. The proxies are also constituents of their optimized asset baskets. This provides a consistent adjusted-close return convention, but the benchmarks are not independent of the investable universe and are not identical to the index-style benchmarks in the historical paper. The summary records the metric sample's start date, end date, and observation count for every strategy and benchmark row. The historical paper used index-style benchmarks; its prior numbers are retained as historical snapshots and are not directly comparable to these regenerated ETF-proxy values. Missing benchmark history is recorded as unavailable rather than silently represented as a valid result.

## Factor analysis

For the US portfolio, excess returns are regressed on MKT, SMB, HML and MOM factors from the Kenneth French Data Library. This factor regression is limited to the US portfolio; it does not validate cross-market factor exposure claims for China or India. Inference uses Newey-West/HAC standard errors.

## Tau sensitivity

The pipeline reruns the US backtest for each configured fixed \(\tau\), setting `tau_low_vol` and `tau_high_vol` equal to the tested value. Each run uses the same main-sample returns, asset universe, rebalance schedule, transaction-cost assumption and net return series as the headline US result. The generated output records OOS start/end dates, observation count, return convention and equilibrium-weight method.

## Crisis analysis

The generated crisis summary intentionally reports **two distinct conventions**, never interchangeable. The historical-paper-comparison fields (`Max Drawdown`, `Volatility Spike`, `Recovery Trading Days`) retain the previously implemented *weighted daily log-return* convention and its first-observed-day normalization for provenance. Those columns are not self-financing buy-and-hold performance.

The additional `Buy-Hold Max Drawdown`, `Buy-Hold Recovery Trading Days`, `Buy-Hold Trough Date` and `Buy-Hold Recovery Date` fields treat the last pre-crisis target as actual holdings, apply the first crisis trading return to initial wealth 1, and let holdings drift without further trades until recovery. This is the economically consistent frozen-holdings stress path matching the corrected main portfolio accounting. Existing published manuscript values are **not** relabeled as outcomes of this new definition, and its values must be regenerated before interpretation.


The crisis generator freezes the last target weights observed strictly before a specified crisis start and applies them to every available out-of-sample trading day in the crisis window. The crisis diagnostic converts adjusted-close simple asset returns to daily log returns and takes their dot product with the frozen weights, as specified in the paper. This weighted-log aggregation is a **separate paper-convention diagnostic**, not the self-financing buy-and-hold simple-return strategy used in the corrected main backtest. The two wealth paths are not economically interchangeable, and their differences must be reconciled before claiming crisis-result replication. The wealth path is normalized so the first observed crisis valuation (V(t_0)) is 1.0; maximum drawdown is calculated relative to that starting valuation, and the volatility-spike ratio compares crisis daily portfolio log-return volatility with up to the preceding 252 trading days. The actual baseline observation count is written to the CSV because ETF listing history can limit coverage (139 available observations for the China 2015 window in the current run). Recovery occurs at the first return to wealth 1.0. Recovery duration is the number of trading-index positions from the crisis trough to that first recovery. The pre-crisis target weights remain frozen from crisis start through the recovery date; the path does not resume the adaptive strategy after the crisis window. This matches the paper's stated frozen-weight convention as a written definition only. The generated crisis values still differ from the historical table, so numerical reproduction is not established; see [the results reconciliation](RESULTS_RECONCILIATION.md).

The study considers the 2008 US Global Financial Crisis, the 2015 China equity crash and the 2020 India COVID shock. The generated crisis and tau-sensitivity tables are written under `results/generated/`; they do not overwrite the historical paper tables. All crisis definitions, effective dates, metric conventions and recovery dates should be checked against these generated outputs before the manuscript is updated.
