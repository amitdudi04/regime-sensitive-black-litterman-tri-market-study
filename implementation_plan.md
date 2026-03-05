# Portfolio Optimization Web GUI

The user requested a massive UI/UX overhaul, migrating away from the PyQt5 desktop GUI because it felt "made by an ai agent". The new goal is to implement a stunning, modern, fully animated landing page and application interface with a dark/light mode toggle.

## Proposed Changes

We will build a high-performance, beautiful localized web application using **FastAPI** for the backend engine and pure Vanilla HTML/CSS/JS for the frontend.

### Web Server Component Architecture
#### [NEW] [app.py](file:///g:/stock%20portfolio/app.py)
A lightweight FastAPI server that mounts the static directory and exposes a `/api/optimize` endpoint. This endpoint receives the JSON parameters (start date, end date, tickers, investor views), dynamically invokes the `BlackLittermanOptimizer` from our existing solid python logic, and returns the result math array calculations back to the frontend.

### Frontend Aesthetics & Layouts
#### [NEW] [index.html](file:///g:/stock%20portfolio/frontend/index.html)
The structure of our stunning application. 
- It will feature a massive, beautifully animated **Landing Page Hero** welcoming the user to the "Black-Litterman Portfolio Intelligence" engine.
- Scrolling down will reveal beautiful glassmorphism configuration cards for entering dates, tickers, and view arrays.
- It will include a fixed header bar with a sun/moon icon toggle.

#### [NEW] [style.css](file:///g:/stock%20portfolio/frontend/style.css)
The Vanilla CSS styling block directly responsible for fulfilling the system's "Rich Aesthetics" directive:
- CSS Custom Properties (Variables) enabling instant dynamic switching between a curated Light Theme and a deep, slick Dark Theme.
- Fluid gradients, smooth box-shadows, rounded borders, and dynamic layout constraints.
- Keyframe animations and transitions enabling hover-effects over table rows and buttons.

#### [NEW] [script.js](file:///g:/stock%20portfolio/frontend/script.js)
The interactive Vanilla JavaScript logic responsible for capturing user forms, sending `fetch` API requests to FastAPI, and rendering dynamic, responsive animations:
- It will dynamically initialize and populate `Chart.js` graphs to replace the static Matplotlib charts.
- Dark/Light Theme toggle class logic mapped directly to the root element (`data-theme="dark"`).

## Verification Plan
1. Stand up the `app.py` FastAPI server backend locally via `uvicorn`.
2. Browse to `localhost:8000` to verify the CSS structure, rendering layouts, dark mode toggle, and hover animations strictly execute exactly as intended.
3. Submit a payload across the engine from the UI and map the returned backend calculation objects directly to the interactive Chart.js elements.

---

# Benchmark Backtesting Enhancements

The user requested robust comparative analysis capabilities in the backtesting module, bridging the theoretical optimized portfolio returns against real-world passive market benchmarks (S&P 500 and CSI 300).

## Proposed Changes

We will refactor the existing `backtesting.py` logic to upgrade its time-series aggregation to true out-of-sample daily trajectories and align them with independent `yfinance` benchmark calls.

### Backtesting Core Logic
#### [MODIFY] [backtesting.py](file:///g:/stock%20portfolio/backtesting.py)
- Refactor `PortfolioBacktester.run_backtest` to store the *daily* out-of-sample returns internally across the rolling windows, rather than strictly aggregating the mathematical mean.
- Using `yfinance.download()`, fetch daily closing prices for `^GSPC` (S&P 500) and `000300.SS` (CSI 300) matching the exact overall simulation timestamps spanning the backtest dates.
- Align the benchmark tracking exactly to the out-of-sample daily testing window dates.
- Implement strict performance metric calculating properties for Maximum Drawdown, Sharpe Ratios natively off of the daily array objects, properly scaled annualized Returns and Volatility.
- Build a continuous compounding cumulative return generation logic (`(1 + R_daily).cumprod() - 1`) for the tested Models + Benchmarks.
- Implement `matplotlib` logic to export the resulting cumulative trajectory graph safely out to `results/benchmark_comparison.png`.

## Verification Plan
1. Ensure `import matplotlib.pyplot as plt` and other data science dependencies exist.
2. Build a local runner script `test_backtest.py` that utilizes an active `BlackLittermanOptimizer` and throws it into the upgraded `run_comprehensive_backtest` flow.
3. Verify that the terminal dumps out the accurate Comparative Matrix with the new metrics.
4. Verify that `results/benchmark_comparison.png` is generated flawlessly plotting the 4 lines.

---

# Realistic Transaction Costs Modeling

The user requested the inclusion of realistic transaction costs to ensure the backtest accounts for portfolio turnover and slippage, making the results practically actionable.

## Proposed Changes

We will modify `PortfolioBacktester` to track previous weights, compute turnover upon rebalancing, and accurately deduct fees from the theoretical gross returns to surface net returns.

### Core Modifications
#### [MODIFY] [backtesting.py](file:///g:/stock%20portfolio/backtesting.py)
- **Initialization**: Introduce `transaction_cost_rate=0.001` (10 bps) and `slippage_rate=0.0005` (5 bps) directly into the `PortfolioBacktester` constructor.
- **Turnover Tracking**: In the rolling window loop, compare `new_weights` against the `previous_weights_at_end_of_period` (which may have drifted due to asset returns, or simply the last target weights assuming rebalancing to target) to compute turnover: `sum(abs(new_weights - previous_weights))`. For simplicity and standard practice, we will use the difference in target weights, or assume cash-to-initial-weights on the first step.
- **Cost Deduction**: Calculate `total_cost = turnover * (cost_rate + slippage)`. Deduct this cost mathematically from the *first day* of the new out-of-sample testing window.
- **Return Dual-Tracking**: Separate the Daily Return arrays into `gross_returns` (current state) and `net_returns` (after costs).
- **Visualization Enhancements**: 
  - Add `plot_turnover_history()` mapping the rebalance dates against the calculated turnover percentages.
  - Modify existing plots to optionally show Gross vs Net cumulative returns.
- **Summary Updates**: Enhance the terminal printout to summarize the overall cost drag and the Net Annualized Returns.

---

# Tau Sensitivity Robustness Analysis

The user requested a dedicated robustness analysis function to track the sensitivity of the Black-Litterman model's optimized outputs against varying values of the `tau` (uncertainty scalar) parameter.

## Proposed Changes

We will introduce `run_tau_sensitivity` directly into the mathematical core of the `BlackLittermanOptimizer` class.

### Core Modifications
#### [MODIFY] [portfolio_optimization/models/black_litterman.py](file:///g:/stock%20portfolio/portfolio_optimization/models/black_litterman.py)
- **New Method**: Implement `run_tau_sensitivity(self, views_dict, confidence_levels=None, tau_values=[0.01, 0.03, 0.05, 0.1, 0.2], max_weight=None, min_weight=0.05, save_dir="results")`.
- **Iterative Override**: The function will iterate through the provided `tau_values`. For each value, it will uniquely override `self.tau`, calculate the resulting posterior returns via `apply_black_litterman`, and process the optimal layout through `optimize_portfolio`.
- **Data Capture**: Within the iteration loop, the function will call `get_portfolio_metrics` to record Expected Return, Volatility, Sharpe Ratio, and the resulting Weight Matrix into a structured dictionary.
- **DataFrame Construction**: Convert the analytical capture dictionaries into a continuous `pandas.DataFrame` where rows represent varying `tau` scalars.
- **Matplotlib Visualization**: Build a comprehensive 3-part graphic plotting `Tau vs Sharpe Ratio`, `Tau vs Volatility`, and a dynamically stacked area chart mapping the actual resulting `Portfolio Weights Across Taus`. 
- **Export**: Render the graphic cleanly and save it natively to `results/tau_sensitivity.png`, returning the active dataframe natively for any terminal outputs or further scripting.

---

# Lambda Sensitivity Robustness Analysis

The user requested an analogous analytical pipeline to measure the portfolio's response to changes in Risk Aversion (`lambda_risk`).

## Proposed Changes
- **New Method**: Add `run_lambda_sensitivity` to `BlackLittermanOptimizer` adhering strictly to identical iterative parameters as the `tau` map (saving to a dataframe).
- **Iterative Logic**: Map `lambda_values=[1.5, 2.0, 2.5, 3.0, 4.0]`. Inside the loop, replace `self.lambda_risk`, compute new Market-Implied returns, new Black-Litterman Posteriors, new limits, and new Metrics.
- **Visualization Mapping**: A 2-panel chart plotting `Lambda vs Sharpe Ratio` and `Lambda vs Expected Return`, exporting to `results/lambda_sensitivity.png`.

---

# 2008 Financial Crisis Stress Testing

The user requested absolute isolation capabilities simulating exact "buy and hold" performance parameters against the 2008 global financial crisis by executing against pre-crisis data, locking allocation schemas, and marching blindly forward into the chaos of 2008 / 2009.

## Proposed Changes
- **New Module**: Create `stress_testing.py` natively in the top level source holding a `HistoricalStressTester` component, decoupling it to ensure logic constraints don't tangle with standard rolling backtesting methodologies.
- **Time Partitions**: Automatically slice the YFinance historical pulls into a `calibration_window` (e.g., 2005-01-01 -> 2007-12-31) and a `crisis_window` (2008-01-01 -> 2009-12-31).
- **Static Allocations**: Spin up the standard `BlackLittermanOptimizer` explicitly inside the calibration phase. Request pure initial weights. Transfer those exact locked weights into the `crisis_window` loop purely evaluating their vector sums over daily returns.
- **Benchmark Integration**: Actively pull S&P 500 arrays spanning the crisis phase, computing its daily crash vectors against the portfolio.
- **Metric Calculations**: Mathematically structure array searchers calculating:
  - Crisis Return (Total 2008 yield)
  - Max Drawdown (Deepest trough from geometric peak)
  - Volatility Spike (Standard deviation of daily hits during the 2008 plunge vs pre-2008 parameters)
  - Recovery Time (Trading Days until portfolio crosses back above its highest previous 2007 peak).
- **Visuals**: A comprehensive 2-pane 2008 Chart: `Cumulative Crisis Returns (2008-09)` layered directly over the mathematical `Drawdown Depths (%)` showing exactly how rapidly the crash recovered across the simulation. 
- **Exporting**: `results/stress_test_2008.png` and console payload summary matrix.

---

# Final Robustness Summary Report

The user requested absolute synthesis of every distinct analytical module inside the application, mathematically consolidating the boundaries of the Tau tests, Lambda maps, 2008 Stress outputs, and standard rolling benchmark returns into a single unified `csv` evaluation sheet.

## Proposed Changes
We will inject a new parent orchestrator script mapping directly to the underlying systems. 
#### [NEW] [generate_robustness_report.py](file:///g:/stock%20portfolio/generate_robustness_report.py)
- **Unified Target Parameters**: Standardize a baseline test timeline (e.g., 2018-2024 for standard runs, and 2005-2009 specifically constrained for the GFC execution module) using default tech targets (`AAPL`, `MSFT`, etc).
- **Sub-Pipeline Execution**:
  1. Boot the `BlackLittermanOptimizer` and fire `run_tau_sensitivity()`. Calculate and extract the exact Expected Return array boundaries ($\Delta_{Return}$) and Sharpe drop mapping.
  2. Fire `run_lambda_sensitivity()` and compute maximum volatility containment spans.
  3. Load `PortfolioBacktester` dynamically. Run it against the equivalent 2018 timeline arrays. Extract exactly the total `Net Annual Return` and continuous `Cost Drag`.
  4. Load `HistoricalStressTester` explicitly targeting `2008`. Boot the `run_stress_test` function and mathematically lift the precise `% Max Drawdown` scalar along with the pre-crisis `Volatility Spike`.
- **Data Integration Matrix**: Format the deeply detached return variables into a standardized multidimensional `pandas.DataFrame`. The dataframe must cleanly orient `[Category, Metric, Value, Model_Comparison]` labels tracking the Black-Litterman allocations explicitly.
- **CSV Exporter**: Finally run `df.to_csv("results/robustness_summary.csv", index=False)` perfectly bridging the deep python variables into a cleanly formatted external spreadsheet.
