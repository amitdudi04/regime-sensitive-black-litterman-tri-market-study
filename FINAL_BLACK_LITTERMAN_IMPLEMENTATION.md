# Professional Black–Litterman Empirical Study & Quantitative Research Platform

This document serves as the final architecture, implementation, and technical reference for the **Tri-Market Black-Litterman Portfolio Optimization System**. The project has evolved from a monolithic empirical script into a robust, object-oriented Quantitative Research Application featuring a dynamic PyQt6 Graphical User Interface, resilient data-fetching pipelines, and accurate decadal stress-testing modules.

---

## 1. Modular Architecture Overview

The system has been completely refactored into separated **Core Engine** and **User Interface** directories for enterprise-level maintainability.

### Project Structure
```text
stock portfolio/
│
├── main.py                          # The primary application entry point. Launches the PyQt6 Dashboard.
│
├── core/                            # The Quantitative Analysis Engine
│   ├── dual_market.py               # Top-level orchestration of US, China and India universe configurations.
│   ├── optimizer.py                 # Core Black-Litterman math, Covariance matrices, and Bayesian updates.
│   ├── backtester.py                # Out-of-Sample Historical Simulation, Information Ratio, Rebalancing.
│   └── stress_testing.py            # Static historical crisis event simulations (2008 Crash, 2015 Burst).
│
└── ui/                              # The Frontend Graphical Interface
    ├── desktop_gui.py               # The main PyQt6 Dashboard, Control Panels, and dynamic layout.
    └── plot_utils.py                # Matplotlib themes, dark-mode styling, and palette configurations.
```

---

## 2. Core Engine Robustness & Upgrades

The quantitative engine has undergone significant hardening to securely process over 20 years of dynamic historical price data.

### 2.1 Multi-Index API Translation
Modern equity data APIs (like `yfinance`) dynamically change their returned DataFrame structures based on the count of requested tickers (returning either single-level Flat Columns or MultiIndex DataFrames).
- The `optimizer.py`, `backtester.py`, and `stress_testing.py` extraction blocks were completely rewritten to robustly inspect `pd.MultiIndex` boundaries.
- Resolves implicit `KeyError` crashes that occurred when `Adj Close` metrics were dropped by the API during single-ticker benchmark fetching.

### 2.2 Deep Historical Availability (Ticker Universe Swap)
The system calculates Covariance Matrices using continuous data arrays. If a recently-IPO'd stock (e.g., CATL in 2018) is included in an analysis requesting data from `2005`, the `dropna()` methodology correctly—but aggressively—truncates the whole array to the newest IPO date to avoid `NaN` matrix corruption.
- To natively support 20-Year deep historical backtests, modern late-IPO components were swapped for **Venerable Pre-2005 Blue Chips**, providing uninterrupted price histories:
  - **Replaced** *Contemporary Amperex Technology (CATL)* with **Gree Electric Appliances (1996)**.
  - **Replaced** *Ping An Insurance* with **China Vanke (1991)**.
  - **Replaced** *ICBC* with **Shanghai Pudong Development Bank (1999)**.

### 2.3 Static Structural Stress Testing
Crisis Stress Tests conceptually evaluate *fixed boundaries in time* (the 2008 Lehman Collapse and the 2015 Chinese Market Bubble). 
- The Backtest Dates defined dynamically by the GUI no longer improperly clamp the Stress Tests, ensuring zero-day horizon bugs do not corrupt the historical data fetching.

### 2.4 Frictional Implementation (Transaction Costs)
Gross theoretical returns have been superseded by Realized Net Returns. 
- The `transaction_cost_rate` and `rebalance_freq` parameters are now passed directly from the GUI into the `core.backtester` simulations.
- Portfolio turnover calculations are executed linearly against absolute weight differentials at rebalancing checkpoints.

---

## 3. The Professional PyQt6 Interface

The User Interface (`desktop_gui.py`) was engineered to escape the limitations of native Operating System UI rendering bugs while offering a premium aesthetic.

### 3.1 Dark Mode Design Aesthetics
- Customized `#1E1E2E` Deep Space background.
- Neon syntax highlighting for specific components (US Market vs China Market curves).
- Fully responsive `QSplitter` layouts dynamically scaling matplotlib canvases alongside configuration panels.

### 3.2 Engineered Parameter Controls
Standard `QSpinBox` up/down arrows exhibit severe CSS rendering bugs natively on Windows Qt6. 
- **Custom Increment/Decrement Wrappers**: Every numerical metric (Tau, Lambda, Friction) has been manually wrapped into a bespoke row flanked by enlarged, custom-rendered `[-]` and `[+]` `QPushButton` actuators for flawless interaction.
- **Dropdown Date Selectors**: The buggy native Calendar widget was replaced with absolute, explicit **[Year]**, **[Month]**, and **[Day]** Dropdown `QComboBox` selectors that intelligently read the exact day counts of leap-years.

### 3.3 Seamless Multithreading Calculation
The GUI no longer locks up during complex matrix operations:
- A `QThread` `AnalysisWorker` handles the data fetching and matrix multiplications in the background.
- Upon completion, the master thread signals the Matplotlib canvasses to `draw_idle()`, achieving fluid asynchronous updates.

---

## 4. Execution Protocol

To launch the Professional Tri-Market Analytical Platform:

1. Guarantee pip environment satisfies: `pip install pandas numpy scipy PyQt6 matplotlib yfinance seaborn`
2. Launch the dashboard:
   ```bash
   python main.py
   ```
3. Use the **Date Selectors** and **Friction Panels** to design your scenario.
4. Click **Run Empirical Analysis** to stream the outputs directly to the visualization pane and the `Export to CSV` modules.
