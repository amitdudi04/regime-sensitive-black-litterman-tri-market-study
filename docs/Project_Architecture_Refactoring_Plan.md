# Project Architecture Refactoring Plan

## Goal Description
The objective is to restructure the existing monolithic and disorganized Regime-Sensitive Black–Litterman Tri-Market research project into a clean, reproducible, and highly modular quantitative research pipeline suitable for academic review. The mathematical logic, numerical results, and model implementations **will not be changed**. 

## Proposed Changes
We will reorganize the codebase into a clean directory structure with single-responsibility modules. Old monolithic scripts will be archived, not deleted.

### Directory Structure & New Modules

#### `config/`
*   **[NEW]** `config/project_config.yaml`: Store project parameters like start dates, transaction cost rates, tau parameter, and rebalance windows for full reproducibility.

#### `data/`
*   `raw/` - Raw market data
*   `processed/` - Cleaned datasets

#### `core/`
*   **[NEW]** `core/data_loader.py`: Download market data via yfinance, handle MultiIndex safely, return clean price DataFrames.
*   **[NEW]** `core/return_calculations.py`: Compute log returns, handle missing data/NaNs.
*   **[NEW]** `core/covariance_estimators.py`: Implement Ledoit–Wolf shrinkage and annualized covariance calculations.

#### `models/`
*   **[NEW]** `models/black_litterman_model.py`: Compute equilibrium returns and implement the Bayesian posterior update logic.
*   **[NEW]** `models/optimizer.py`: Compute optimal weight allocations (Mean-Variance and unconstrained optimizers).

#### `backtesting/`
*   **[NEW]** `backtesting/rolling_backtest.py`: Perform rolling out-of-sample testing logic.
*   **[NEW]** `backtesting/transaction_costs.py`: Compute turnover and apply frictional decay penalties to derive net returns.
*   **[NEW]** `backtesting/crisis_freeze.py`: Implement the crisis freeze methodology (e.g., locking weights before 2008/2015/2020 events).
*   **[NEW]** `backtesting/allocation_stability_index.py`: Compute the ASI metric across rolling rebalance blocks.

#### `analysis/`
*   **[NEW]** `analysis/soe_private_analysis.py`: Split Chinese equities into SOE and Private categorizations and compute independent metrics.
*   **[NEW]** `analysis/statistical_tests.py`: Implement Circular Block Bootstrapping, T-tests, and Jobson-Korkie standardizations.

#### `pipelines/` (High-Level Execution)
*   **[NEW]** `pipelines/run_tri_market_pipeline.py`: Loads US/China/India data, runs Black-Litterman vs Markowitz, rolling backtests, transaction costs, and exports full results.
*   **[NEW]** `pipelines/run_soe_pipeline.py`: Loads China data, separates SOE/Private, runs allocations, ASI, stats, and exports comparison tables.
*   **[NEW]** `pipelines/run_crisis_analysis.py`: Extracts pre-crisis weights, simulates crashes, computes drawdowns/vol spikes, and exports tables.

#### `experiments/`
*   **[NEW]** `experiments/run_tau_sensitivity.py`: Robustness testing for the tau parameter.

#### `results/`
*   Outputs: `tri_market_summary.csv`, `soe_vs_private_china_ownership_summary.csv`, `crisis_comparison_tables.csv`, `statistical_test_output.json`
*   **[NEW]** `results/export_utils.py`: Utility functions to export clean `.csv` and `.json` tables matching research paper outputs.

#### `visualization/`
*   **[NEW]** `visualization/plotting_tools.py`: Isolate plotting capabilities.

#### `tests/`
*   **[NEW]** `tests/test_data_loader.py`
*   **[NEW]** `tests/test_black_litterman.py`
*   **[NEW]** `tests/test_backtest.py`
*   **[NEW]** `tests/test_optimizer.py`

#### `legacy/`
*   **[MOVE]** Archive all monolithic scripts here instead of permanently deleting them.

#### `docs/` & Project Root
*   **[MOVE]** Move `FINAL_PROJECT_IMPLEMENTATION.md` and `FINAL_RESEARCH_RESULTS_COMPENDIUM.docx` into `docs/`.
*   **[NEW]** `README.md`: Professional project overview explaining the methodology and exact run commands.
*   **[NEW]** `requirements.txt`: Package dependency mapping.

## Verification Plan

### Automated Tests
1. Execute `python pipelines/run_tri_market_pipeline.py` and verify that the `tri_market_summary.csv` matches the existing results.
2. Execute `python pipelines/run_soe_pipeline.py` and verify `soe_vs_private_china_ownership_summary.csv` accuracy.
3. Execute `python pipelines/run_crisis_analysis.py` and verify the `crisis_comparison_tables.csv`.

### Manual Verification
Review the exported CSV and JSON results against the values defined in `docs/FINAL_PROJECT_IMPLEMENTATION.md` to guarantee structural mathematical preservation.
