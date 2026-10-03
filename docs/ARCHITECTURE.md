# Research Architecture

The project is organized around a single end-to-end tri-market pipeline.

## Data flow

```text
ETF prices
   ↓
common-date alignment
   ↓
simple daily returns
   ↓
252-day rolling estimation window
   ↓
Ledoit-Wolf covariance
   ↓
┌───────────────────────────────┐
│ Markowitz: historical means   │
│ Black-Litterman: posterior    │
└───────────────────────────────┘
   ↓
same long-only optimizer
   ↓
63-day out-of-sample holding period
   ↓
drift-adjusted turnover and transaction costs
   ↓
portfolio returns and weight histories
   ↓
performance, ASI and US factor analysis
```

## Main modules

- `core/data_loader.py` — market-data download and alignment.
- `core/return_calculations.py` — daily return calculations.
- `core/covariance_estimators.py` — Ledoit-Wolf covariance estimation.
- `models/black_litterman_model.py` — equilibrium returns and posterior calculation.
- `models/optimizer.py` — common long-only portfolio optimizer.
- `backtesting/paper_backtest.py` — rolling out-of-sample comparison.
- `analysis/factor_regression.py` — US four-factor regression with HAC standard errors.
- `analysis/regime_detection.py` — two-state Markov-switching analysis.
- `backtesting/crisis_freeze.py` — fixed-weight crisis-window helper.
- `pipelines/tri_market_pipeline.py` — end-to-end study runner.

## Results

Tables reported in the research paper are stored in `results/paper_results/`.

Running the pipeline produces a separate local directory, `results/generated/`, containing the latest output tables, daily returns, weights and figures. The generated directory is excluded from version control.
