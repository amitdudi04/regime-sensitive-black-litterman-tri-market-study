# FULL FORENSIC REPOSITORY AUDIT: Regime-Sensitive Black-Litterman

## 1. FULL FILE INVENTORY
- .gitignore (263 bytes)
- Academic_Paper_TriMarket_BL.docx (43726 bytes)
- Academic_Paper_TriMarket_BL_Formatted.docx (43964 bytes)
- align_md.py (5591 bytes)
- Amit_Kumar_Dudi_Abstract_ZJU.docx (37639 bytes)
- append_regime_doc.py (1692 bytes)
- append_results.py (4135 bytes)
- audit_and_repair_manuscript.py (8136 bytes)
- Black_Litterman_Academic_Paper_Updated_2026.docx (45402 bytes)
- build_architecture_doc.py (10654 bytes)
- build_implementation_doc.py (7269 bytes)
- build_monolith.py (7710 bytes)
- chart_output.txt (190 bytes)
- CIEMC_2.0_Research_Paper.docx (33029 bytes)
- clear_all_yf_cache.py (776 bytes)
- clear_cache_test.py (690 bytes)
- clear_yf_cache.py (434 bytes)
- COMPLETION_SUMMARY.md (11038 bytes)
- config.py (3859 bytes)
- convert_to_docx.py (335 bytes)
- correlation_matrix.png (159463 bytes)
- create_paper.py (22828 bytes)
- create_updated_paper.py (28988 bytes)
- cumulative_returns.png (375959 bytes)
- debug_all.py (760 bytes)
- debug_india.py (1072 bytes)
- debug_out.txt (26658 bytes)
- debug_pipeline.py (567 bytes)
- debug_runner.py (194 bytes)
- DEPLOYMENT.md (11363 bytes)
- DESKTOP_GUI_COMPLETE.md (9391 bytes)
- DESKTOP_GUI_SUMMARY.md (14220 bytes)
- DESKTOP_GUI_USER_GUIDE.md (10398 bytes)
- DEVELOPMENT_ROADMAP.md (11372 bytes)
- drawdown.png (696960 bytes)
- efficient_frontier.png (232544 bytes)
- ENHANCEMENT_ROADMAP.md (0 bytes)
- err.txt (3792 bytes)
- error.txt (2974 bytes)
- error_log.txt (6192 bytes)
- expand_compendium.py (6475 bytes)
- expand_compendium2.py (11095 bytes)
- export_final_pdf.py (864 bytes)
- FEATURE_CHECKLIST.md (10416 bytes)
- FINAL_BLACK_LITTERMAN_IMPLEMENTATION.md (5931 bytes)
- FINAL_PROJECT_IMPLEMENTATION.docx (82127 bytes)
- FINAL_PROJECT_IMPLEMENTATION.md (18978 bytes)
- final_refinement.py (4278 bytes)
- FINAL_RESEARCH_RESULTS_COMPENDIUM.docx (36412 bytes)
- final_test.log (1186 bytes)
- find_yf_cache.py (686 bytes)
- fix_compendium.py (1983 bytes)
- format_pipeline_diagram.py (1961 bytes)
- generate_academic_d
(...truncated for length, total files: 312)

## 2. DEPENDENCY GRAPH
```text
pipelines.dual_market
├── analysis.factor_regression
│   ├── pandas
│   ├── statsmodels.api
│   ├── numpy
│   ├── pandas_datareader.data
├── yfinance
├── legacy.core_legacy.backtester
│   ├── yfinance
│   ├── scipy.optimize
│   ├── warnings
│   ├── pandas
│   ├── numpy
│   ├── os
│   ├── typing
│   ├── logging
├── legacy.core_legacy.soe_private_analysis
│   ├── legacy.core_legacy.export_utils
│   ├── legacy.core_legacy.backtester
│   ├── scipy
│   ├── legacy.core_legacy.optimizer
│   ├── legacy.core_legacy.regime_detection
│   ├── pandas
│   ├── numpy
│   ├── legacy.core_legacy.visualization
│   ├── legacy.core_legacy.ownership_classification
│   ├── typing
│   ├── legacy.core_legacy.statistical_tests
├── legacy.core_legacy.ownership_classification
│   ├── typing
├── warnings
├── pandas
├── legacy.core_legacy.robustness
│   ├── yfinance
│   ├── warnings
│   ├── pandas
│   ├── tempfile
│   ├── numpy
│   ├── legacy.core_legacy.optimizer
│   ├── os
│   ├── logging
├── numpy
├── legacy.core_legacy.optimizer
│   ├── yfinance
│   ├── scipy.stats
│   ├── scipy.optimize
│   ├── sklearn.covariance
│   ├── matplotlib.pyplot
│   ├── warnings
│   ├── pandas
│   ├── time
│   ├── tempfile
│   ├── numpy
│   ├── os
│   ├── typing
│   ├── logging
├── os
├── typing
├── legacy.core_legacy.stress_testing
│   ├── yfinance
│   ├── pandas
│   ├── tempfile
│   ├── numpy
│   ├── legacy.core_legacy.optimizer
│   ├── os
│   ├── logging
├── legacy.core_legacy.statistical_tests
│   ├── pandas
│   ├── scipy
│   ├── numpy
├── logging

```

## 3. DATA FLOW MAP
1. **Raw Data Source**: `yfinance` & `pandas_datareader` (Kenneth French) [core/data_loader.py implicitly mapped]
2. **Returns Calculation**: `legacy/core_legacy/return_calculators.py`
3. **Covariance**: `legacy/core_legacy/covariance_estimators.py`
4. **Black-Litterman**: `legacy/core_legacy/models.py`
5. **Optimization**: `legacy/core_legacy/models.py`
6. **Backtest**: `legacy/core_legacy/backtester.py`
7. **ASI**: Handled within backtest logic looping weight L1-norms
8. **Crisis**: `legacy/core_legacy/stress_testing.py`
9. **Factor Regression**: `legacy/core_legacy/factor_models.py`
10. **Export**: `pipelines/run_tri_market_pipeline.py` / `pipelines/run_crisis_analysis.py` $\rightarrow$ `results/tables/`
11. **GUI Rendering**: `ui/desktop_gui.py` consuming CSVs and computing dynamically.

## 4. FILE CLASSIFICATION TABLE
| File | Category | Reason | Used By |
| --- | --- | --- | --- |
| .gitignore | [REVIEW] | Undetermined | - |
| Academic_Paper_TriMarket_BL.docx | [DOCUMENTATION] | Text/Document | - |
| Academic_Paper_TriMarket_BL_Formatted.docx | [DOCUMENTATION] | Text/Document | - |
| align_md.py | [SUPPORT] | Audit/Maintenance scripting | None |
| Amit_Kumar_Dudi_Abstract_ZJU.docx | [DOCUMENTATION] | Text/Document | - |
| append_regime_doc.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| append_results.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| audit_and_repair_manuscript.py | [SUPPORT] | Audit/Maintenance scripting | None |
| Black_Litterman_Academic_Paper_Updated_2026.docx | [DOCUMENTATION] | Text/Document | - |
| build_architecture_doc.py | [CORE] | GUI Rendering | None |
| build_implementation_doc.py | [CORE] | GUI Rendering | None |
| build_monolith.py | [CORE] | GUI Rendering | None |
| chart_output.txt | [SUPPORT] | Config/Requirement/Log | - |
| CIEMC_2.0_Research_Paper.docx | [DOCUMENTATION] | Text/Document | - |
| clear_all_yf_cache.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| clear_cache_test.py | [SUPPORT] | Testing framework | None |
| clear_yf_cache.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| COMPLETION_SUMMARY.md | [DOCUMENTATION] | Text/Document | - |
| config.py | [SUPPORT] | Imported utility | server.py, dashboard.py |
| convert_to_docx.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| correlation_matrix.png | [REVIEW] | Undetermined | - |
| create_paper.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| create_updated_paper.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| cumulative_returns.png | [REVIEW] | Undetermined | - |
| debug_all.py | [SUPPORT] | Audit/Maintenance scripting | None |
| debug_india.py | [SUPPORT] | Audit/Maintenance scripting | None |
| debug_out.txt | [SUPPORT] | Config/Requirement/Log | - |
| debug_pipeline.py | [CORE] | Pipeline / Execution | None |
| debug_runner.py | [SUPPORT] | Audit/Maintenance scripting | None |
| DEPLOYMENT.md | [DOCUMENTATION] | Text/Document | - |
| DESKTOP_GUI_COMPLETE.md | [DOCUMENTATION] | Text/Document | - |
| DESKTOP_GUI_SUMMARY.md | [DOCUMENTATION] | Text/Document | - |
| DESKTOP_GUI_USER_GUIDE.md | [DOCUMENTATION] | Text/Document | - |
| DEVELOPMENT_ROADMAP.md | [DOCUMENTATION] | Text/Document | - |
| drawdown.png | [REVIEW] | Undetermined | - |
| efficient_frontier.png | [REVIEW] | Undetermined | - |
| ENHANCEMENT_ROADMAP.md | [DOCUMENTATION] | Text/Document | - |
| err.txt | [SUPPORT] | Config/Requirement/Log | - |
| error.txt | [SUPPORT] | Config/Requirement/Log | - |
| error_log.txt | [SUPPORT] | Config/Requirement/Log | - |
| expand_compendium.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| expand_compendium2.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| export_final_pdf.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| FEATURE_CHECKLIST.md | [DOCUMENTATION] | Text/Document | - |
| FINAL_BLACK_LITTERMAN_IMPLEMENTATION.md | [DOCUMENTATION] | Text/Document | - |
| FINAL_PROJECT_IMPLEMENTATION.docx | [DOCUMENTATION] | Text/Document | - |
| FINAL_PROJECT_IMPLEMENTATION.md | [DOCUMENTATION] | Text/Document | - |
| final_refinement.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| FINAL_RESEARCH_RESULTS_COMPENDIUM.docx | [DOCUMENTATION] | Text/Document | - |
| final_test.log | [REVIEW] | Undetermined | - |
| find_yf_cache.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| fix_compendium.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| format_pipeline_diagram.py | [CORE] | Pipeline / Execution | None |
| generate_academic_docs.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| generate_academic_paper.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| generate_docx_compendium.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| generate_markdown.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| generate_paper.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| generate_research_figures.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| generate_robustness_report.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| get_india_metrics.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| get_india_oos.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| GUI_QUICK_REFERENCE.md | [DOCUMENTATION] | Text/Document | - |
| implementation_plan.md | [DOCUMENTATION] | Text/Document | - |
| IMPLEMENTATION_SUMMARY.md | [DOCUMENTATION] | Text/Document | - |
| inject_markdown.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| INSTALLATION_COMPLETE.md | [DOCUMENTATION] | Text/Document | - |
| LICENSE | [REVIEW] | Undetermined | - |
| main.py | [CORE] | Pipeline / Execution | None |
| main_out.log | [REVIEW] | Undetermined | - |
| metrics_out.json | [SUPPORT] | Config/Requirement/Log | - |
| nuke_db.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| out.txt | [SUPPORT] | Config/Requirement/Log | - |
| pandoc-3.9-windows-x86_64.msi | [REVIEW] | Undetermined | - |
| pipeline_error.txt | [SUPPORT] | Config/Requirement/Log | - |
| PROJECT_STRUCTURE.md | [DOCUMENTATION] | Text/Document | - |
| QUICK_START.md | [DOCUMENTATION] | Text/Document | - |
| README.md | [DOCUMENTATION] | Text/Document | - |
| README_INDEX.md | [DOCUMENTATION] | Text/Document | - |
| README_MASTER.md | [DOCUMENTATION] | Text/Document | - |
| REORGANIZATION_SUMMARY.md | [DOCUMENTATION] | Text/Document | - |
| repo_scanner.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| requirements.txt | [SUPPORT] | Config/Requirement/Log | - |
| Research_Pipeline_Architecture_Documentation.docx | [DOCUMENTATION] | Text/Document | - |
| revise_manuscript.py | [SUPPORT] | Audit/Maintenance scripting | None |
| risk_metrics.png | [REVIEW] | Undetermined | - |
| run_debug.py | [SUPPORT] | Audit/Maintenance scripting | None |
| run_debug_asi.py | [SUPPORT] | Audit/Maintenance scripting | None |
| run_debug_asi2.py | [SUPPORT] | Audit/Maintenance scripting | None |
| run_debug_backtest.py | [SUPPORT] | Testing framework | None |
| run_debug_column_asi.py | [SUPPORT] | Audit/Maintenance scripting | None |
| run_india_covid.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| run_soe_pipeline.py | [CORE] | Pipeline / Execution | debug_runner.py |
| SETUP.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| stacktrace.txt | [SUPPORT] | Config/Requirement/Log | - |
| State_Ownership_Research_Paper.docx | [DOCUMENTATION] | Text/Document | - |
| study_error.txt | [SUPPORT] | Config/Requirement/Log | - |
| study_error_utf8.txt | [SUPPORT] | Config/Requirement/Log | - |
| sync_docs.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| test_backtest_benchmarks.py | [SUPPORT] | Testing framework | None |
| test_chart_json.py | [SUPPORT] | Testing framework | None |
| test_chart_metrics.py | [SUPPORT] | Testing framework | None |
| test_chart_numbers.py | [SUPPORT] | Testing framework | None |
| test_lambda_sensitivity.py | [SUPPORT] | Testing framework | None |
| test_min_weight.py | [SUPPORT] | Testing framework | None |
| test_nvda_2.py | [SUPPORT] | Testing framework | None |
| test_nvda_issue.py | [SUPPORT] | Testing framework | None |
| test_optimization.py | [SUPPORT] | Testing framework | None |
| test_optimizer.py | [SUPPORT] | Testing framework | None |
| test_out.txt | [SUPPORT] | Config/Requirement/Log | - |
| test_run.py | [SUPPORT] | Testing framework | None |
| test_scale.py | [SUPPORT] | Testing framework | None |
| test_tau_sensitivity.py | [SUPPORT] | Testing framework | None |
| test_trimarket.py | [SUPPORT] | Testing framework | None |
| test_yf.py | [SUPPORT] | Testing framework | None |
| test_yf_custom_cache.py | [SUPPORT] | Testing framework | None |
| test_yf_detailed.py | [SUPPORT] | Testing framework | None |
| test_yf_session.py | [SUPPORT] | Testing framework | None |
| test_yf_traceback.py | [SUPPORT] | Testing framework | None |
| valid_test.log | [REVIEW] | Undetermined | - |
| verify_crisis_recovery.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| verify_gui.py | [CORE] | GUI Rendering | None |
| verify_installation.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| verify_pyqt.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| weight_comparison.png | [REVIEW] | Undetermined | - |
| yf_error.log | [REVIEW] | Undetermined | - |
| __main__.py | [CORE] | Pipeline / Execution | None |
| ~$ate_Ownership_Research_Paper.docx | [DOCUMENTATION] | Text/Document | - |
| ~$NAL_RESEARCH_RESULTS_COMPENDIUM.docx | [DOCUMENTATION] | Text/Document | - |
| analysis\factor_regression.py | [SUPPORT] | Imported utility | dual_market.py, run_tri_market_pipeline.py |
| analysis\regime_detection.py | [SUPPORT] | Imported utility | run_tri_market_pipeline.py |
| analysis\soe_private_analysis.py | [SUPPORT] | Imported utility | run_soe_pipeline.py |
| analysis\statistical_tests.py | [SUPPORT] | Testing framework | run_soe_pipeline.py |
| backtesting\allocation_stability_index.py | [SUPPORT] | Testing framework | run_debug_column_asi.py, run_soe_pipeline.py, run_tri_market_pipeline.py |
| backtesting\crisis_freeze.py | [SUPPORT] | Testing framework | None |
| backtesting\rolling_backtest.py | [SUPPORT] | Testing framework | run_tau_sensitivity.py, __init__.py, run_tri_market_pipeline.py, test_backtest.py |
| backtesting\transaction_costs.py | [SUPPORT] | Testing framework | run_tri_market_pipeline.py |
| config\project_config.yaml | [SUPPORT] | Config/Requirement/Log | - |
| core\covariance_estimators.py | [SUPPORT] | Imported utility | run_debug_asi2.py, rolling_backtest.py, run_tau_sensitivity.py, run_tri_market_pipeline.py |
| core\data_loader.py | [SUPPORT] | Imported utility | run_debug_asi.py, run_debug_asi2.py, run_debug_backtest.py, run_debug_column_asi.py, run_tau_sensitivity.py, run_soe_pipeline.py, run_tri_market_pipeline.py, test_data_loader.py |
| core\return_calculations.py | [SUPPORT] | Imported utility | run_debug_asi.py, run_debug_asi2.py, run_debug_backtest.py, run_debug_column_asi.py, run_tau_sensitivity.py, run_soe_pipeline.py, run_tri_market_pipeline.py |
| core\__init__.py | [CORE] | Execution Endpoint / Init | None |
| docs\FINAL_PROJECT_IMPLEMENTATION.md | [DOCUMENTATION] | Text/Document | - |
| docs\FINAL_RESEARCH_RESULTS_COMPENDIUM_REVISED.docx | [DOCUMENTATION] | Text/Document | - |
| docs\MASTER_RESEARCH_REFERENCE.md | [DOCUMENTATION] | Text/Document | - |
| docs\Project_Architecture_Refactoring_Plan.md | [DOCUMENTATION] | Text/Document | - |
| docs\Project_Architecture_Refactoring_Plan_REVISED.docx | [DOCUMENTATION] | Text/Document | - |
| docs\README.md | [DOCUMENTATION] | Text/Document | - |
| docs\Regime_Sensitive_Black_Litterman_Study_FINAL.docx | [DOCUMENTATION] | Text/Document | - |
| docs\Research_Pipeline_Architecture_Documentation_REVISED.docx | [DOCUMENTATION] | Text/Document | - |
| docs\research_pipeline_diagram.md | [DOCUMENTATION] | Text/Document | - |
| docs\audit\ASI_DEBUGGING_REPORT.md | [DOCUMENTATION] | Text/Document | - |
| docs\audit\ASI_FINAL_VALIDATION.md | [DOCUMENTATION] | Text/Document | - |
| docs\audit\ASI_MARKET_VALIDATION.md | [DOCUMENTATION] | Text/Document | - |
| docs\audit\ASI_SYNC_REPORT.md | [DOCUMENTATION] | Text/Document | - |
| docs\audit\FINAL_DOCUMENTATION_POLISH.md | [DOCUMENTATION] | Text/Document | - |
| docs\audit\FINAL_VALIDATION_REPORT.md | [DOCUMENTATION] | Text/Document | - |
| experiments\run_tau_sensitivity.py | [REMOVE_CANDIDATE] | Not imported, not pipeline, not main | None |
| experiments\run_2026_03_11_0107\config.yaml | [SUPPORT] | Config/Requirement/Log | - |
| experiments\run_2026_03_11_0107\metrics.json | [SUPPORT] | Config/Requirement/Log | - |
| experiments\run_2026_03_11_0107\results_tables\factor_regression_results.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_0107\results_tables\model_comparison_summary.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_0107\results_tables\regime_performance_summary.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_0107\results_tables\tri_market_summary.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1327\config.yaml | [SUPPORT] | Config/Requirement/Log | - |
| experiments\run_2026_03_11_1327\metrics.json | [SUPPORT] | Config/Requirement/Log | - |
| experiments\run_2026_03_11_1327\results_tables\factor_regression_results.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1327\results_tables\model_comparison_summary.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1327\results_tables\regime_performance_summary.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1327\results_tables\tri_market_summary.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1343\config.yaml | [SUPPORT] | Config/Requirement/Log | - |
| experiments\run_2026_03_11_1343\metrics.json | [SUPPORT] | Config/Requirement/Log | - |
| experiments\run_2026_03_11_1343\results_tables\factor_regression_results.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1343\results_tables\model_comparison_summary.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1343\results_tables\regime_performance_summary.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1343\results_tables\tri_market_summary.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1346\config.yaml | [SUPPORT] | Config/Requirement/Log | - |
| experiments\run_2026_03_11_1346\metrics.json | [SUPPORT] | Config/Requirement/Log | - |
| experiments\run_2026_03_11_1346\results_tables\factor_regression_results.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1346\results_tables\model_comparison_summary.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1346\results_tables\regime_performance_summary.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1346\results_tables\tri_market_summary.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1347\config.yaml | [SUPPORT] | Config/Requirement/Log | - |
| experiments\run_2026_03_11_1347\metrics.json | [SUPPORT] | Config/Requirement/Log | - |
| experiments\run_2026_03_11_1347\results_tables\factor_regression_results.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1347\results_tables\model_comparison_summary.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1347\results_tables\regime_performance_summary.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1347\results_tables\tri_market_summary.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1417\config.yaml | [SUPPORT] | Config/Requirement/Log | - |
| experiments\run_2026_03_11_1417\metrics.json | [SUPPORT] | Config/Requirement/Log | - |
| experiments\run_2026_03_11_1417\figures\asi_stability.png | [REVIEW] | Undetermined | - |
| experiments\run_2026_03_11_1417\figures\drawdown_comparison.png | [REVIEW] | Undetermined | - |
| experiments\run_2026_03_11_1417\figures\regime_performance_comparison.png | [REVIEW] | Undetermined | - |
| experiments\run_2026_03_11_1417\figures\regime_probabilities.png | [REVIEW] | Undetermined | - |
| experiments\run_2026_03_11_1417\figures\rolling_sharpe.png | [REVIEW] | Undetermined | - |
| experiments\run_2026_03_11_1417\tables\factor_regression_results.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1417\tables\model_comparison_summary.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1417\tables\regime_performance_summary.csv | [DATA] | Input/Output tabular data | - |
| experiments\run_2026_03_11_1417\tables\tri_market_summary.csv | [DATA] | Input/Output tabular data | - |
| legacy\advanced_metrics.py | [REMOVE_CANDIDATE] | Legacy module unused | None |
| legacy\backtesting.py | [REMOVE_CANDIDATE] | Legacy module unused | None |
| legacy\empirical_study.py | [REMOVE_CANDIDATE] | Legacy module unused | None |
| legacy\main_black_litterman.py | [CORE] | Pipeline / Execution | None |
| legacy\robustness.py | [CORE] | Pipeline / Execution | dual_market.py |
| legacy\run_analysis.py | [REMOVE_CANDIDATE] | Legacy module unused | None |
| legacy\stress_testing.py | [CORE] | Pipeline / Execution | debug_india.py, verify_crisis_recovery.py, dual_market.py, run_tri_market_pipeline.py |
| legacy\visualizations.py | [REMOVE_CANDIDATE] | Legacy module unused | None |
| legacy\core_legacy\backtester.py | [CORE] | Pipeline / Execution | soe_analysis.py, soe_private_analysis.py, dual_market.py |
| legacy\core_legacy\export_utils.py | [CORE] | Pipeline / Execution | soe_private_analysis.py |
| legacy\core_legacy\optimizer.py | [CORE] | Pipeline / Execution | debug_india.py, verify_crisis_recovery.py, robustness.py, soe_analysis.py, soe_private_analysis.py, stress_testing.py, dual_market.py |
| legacy\core_legacy\ownership_classification.py | [CORE] | Pipeline / Execution | soe_private_analysis.py, dual_market.py |
| legacy\core_legacy\regime_detection.py | [CORE] | Pipeline / Execution | soe_private_analysis.py |
| legacy\core_legacy\robustness.py | [CORE] | Pipeline / Execution | dual_market.py |
| legacy\core_legacy\soe_analysis.py | [REMOVE_CANDIDATE] | Legacy module unused | None |
| legacy\core_legacy\soe_private_analysis.py | [CORE] | Pipeline / Execution | dual_market.py |
| legacy\core_legacy\statistical_tests.py | [CORE] | Pipeline / Execution | soe_analysis.py, soe_private_analysis.py, dual_market.py |
| legacy\core_legacy\stress_testing.py | [CORE] | Pipeline / Execution | debug_india.py, verify_crisis_recovery.py, dual_market.py, run_tri_market_pipeline.py |
| legacy\core_legacy\visualization.py | [CORE] | Pipeline / Execution | soe_private_analysis.py |
| legacy\portfolio_optimization\__init__.py | [CORE] | Execution Endpoint / Init | None |
| legacy\portfolio_optimization\api\server.py | [REMOVE_CANDIDATE] | Legacy module unused | None |
| legacy\portfolio_optimization\api\__init__.py | [CORE] | Execution Endpoint / Init | None |
| legacy\portfolio_optimization\backtesting\rolling_backtest.py | [REMOVE_CANDIDATE] | Legacy module unused | None |
| legacy\portfolio_optimization\backtesting\__init__.py | [CORE] | Execution Endpoint / Init | None |
| legacy\portfolio_optimization\config\settings.py | [REMOVE_CANDIDATE] | Legacy module unused | None |
| legacy\portfolio_optimization\config\__init__.py | [CORE] | Execution Endpoint / Init | None |
| legacy\portfolio_optimization\frontend\dashboard.py | [REMOVE_CANDIDATE] | Legacy module unused | None |
| legacy\portfolio_optimization\frontend\__init__.py | [CORE] | Execution Endpoint / Init | None |
| legacy\portfolio_optimization\models\advanced_metrics.py | [REMOVE_CANDIDATE] | Legacy module unused | None |
| legacy\portfolio_optimization\models\black_litterman.py | [REMOVE_CANDIDATE] | Legacy module unused | None |
| legacy\portfolio_optimization\models\visualizations.py | [REMOVE_CANDIDATE] | Legacy module unused | None |
| legacy\portfolio_optimization\models\__init__.py | [CORE] | Execution Endpoint / Init | None |
| legacy\portfolio_optimization\tests\__init__.py | [CORE] | Execution Endpoint / Init | None |
| legacy\portfolio_optimization\utils\installation_verify.py | [REMOVE_CANDIDATE] | Legacy module unused | None |
| legacy\portfolio_optimization\utils\__init__.py | [CORE] | Execution Endpoint / Init | None |
| models\black_litterman_model.py | [CORE] | Pipeline / Execution | run_debug_asi2.py, rolling_backtest.py, run_tau_sensitivity.py, run_tri_market_pipeline.py, test_black_litterman.py |
| models\optimizer.py | [CORE] | Pipeline / Execution | run_debug_asi2.py, rolling_backtest.py, run_tau_sensitivity.py, run_tri_market_pipeline.py, test_optimizer.py |
| my_yf_cache\cookies.db | [REVIEW] | Undetermined | - |
| my_yf_cache\tkr-tz.db | [REVIEW] | Undetermined | - |
| pipelines\dual_market.py | [CORE] | Pipeline / Execution | debug_all.py, debug_india.py, debug_pipeline.py, get_india_metrics.py, get_india_oos.py, run_india_covid.py, test_run.py, test_trimarket.py, verify_crisis_recovery.py, run_crisis_analysis.py, desktop_gui.py |
| pipelines\run_crisis_analysis.py | [CORE] | Pipeline / Execution | None |
| pipelines\run_soe_pipeline.py | [CORE] | Pipeline / Execution | None |
| pipelines\run_tri_market_pipeline.py | [CORE] | Pipeline / Execution | run_debug_asi.py, run_debug_asi2.py, run_debug_backtest.py, run_debug_column_asi.py |
| results\asi_metrics.csv | [DATA] | Input/Output tabular data | - |
| results\export_utils.py | [SUPPORT] | Imported utility | run_soe_pipeline.py, run_tri_market_pipeline.py |
| results\turnover_metrics.csv | [DATA] | Input/Output tabular data | - |
| results\weight_history_black_litterman.csv | [DATA] | Input/Output tabular data | - |
| results\weight_history_equal_weight.csv | [DATA] | Input/Output tabular data | - |
| results\weight_history_markowitz.csv | [DATA] | Input/Output tabular data | - |
| results\debug\asi_metrics.csv | [DATA] | Input/Output tabular data | - |
| results\debug\benchmark_comparison.png | [REVIEW] | Undetermined | - |
| results\debug\china_asset_universe.csv | [DATA] | Input/Output tabular data | - |
| results\debug\china_performance_summary.csv | [DATA] | Input/Output tabular data | - |
| results\debug\china_robustness_summary.csv | [DATA] | Input/Output tabular data | - |
| results\debug\correlation_matrix.png | [REVIEW] | Undetermined | - |
| results\debug\crisis_comparison_tables.csv | [DATA] | Input/Output tabular data | - |
| results\debug\cross_market_comparison.csv | [DATA] | Input/Output tabular data | - |
| results\debug\cross_market_structural_analysis.csv | [DATA] | Input/Output tabular data | - |
| results\debug\cumulative_returns.png | [REVIEW] | Undetermined | - |
| results\debug\drawdown.png | [REVIEW] | Undetermined | - |
| results\debug\efficient_frontier.png | [REVIEW] | Undetermined | - |
| results\debug\final_performance_summary.csv | [DATA] | Input/Output tabular data | - |
| results\debug\final_research_dashboard.png | [REVIEW] | Undetermined | - |
| results\debug\india_crisis.txt | [SUPPORT] | Config/Requirement/Log | - |
| results\debug\lambda_sensitivity.png | [REVIEW] | Undetermined | - |
| results\debug\latex_tables_output.tex | [REVIEW] | Undetermined | - |
| results\debug\risk_metrics.png | [REVIEW] | Undetermined | - |
| results\debug\robustness_summary.csv | [DATA] | Input/Output tabular data | - |
| results\debug\soe_vs_private.xlsx | [REVIEW] | Undetermined | - |
| results\debug\soe_vs_private_china_ownership_summary_china_ownership_summary.csv | [DATA] | Input/Output tabular data | - |
| results\debug\statistical_test_output.json | [SUPPORT] | Config/Requirement/Log | - |
| results\debug\stress_test_2008.png | [REVIEW] | Undetermined | - |
| results\debug\structural_interpretation_output.txt | [SUPPORT] | Config/Requirement/Log | - |
| results\debug\tau_sensitivity.png | [REVIEW] | Undetermined | - |
| results\debug\trace.txt | [SUPPORT] | Config/Requirement/Log | - |
| results\debug\tri_market_dashboard.png | [REVIEW] | Undetermined | - |
| results\debug\turnover_history.png | [REVIEW] | Undetermined | - |
| results\debug\turnover_metrics.csv | [DATA] | Input/Output tabular data | - |
| results\debug\weight_comparison.png | [REVIEW] | Undetermined | - |
| results\debug\weight_history_black_litterman.csv | [DATA] | Input/Output tabular data | - |
| results\debug\weight_history_equal_weight.csv | [DATA] | Input/Output tabular data | - |
| results\debug\weight_history_markowitz.csv | [DATA] | Input/Output tabular data | - |
| results\figures\asi_dynamics.png | [REVIEW] | Undetermined | - |
| results\figures\crisis_stress_tests.png | [REVIEW] | Undetermined | - |
| results\figures\cumulative_returns.png | [REVIEW] | Undetermined | - |
| results\figures\drawdown_comparison.png | [REVIEW] | Undetermined | - |
| results\figures\factor_exposure_plot.png | [REVIEW] | Undetermined | - |
| results\figures\regime_probabilities.png | [REVIEW] | Undetermined | - |
| results\figures\rolling_sharpe_analysis.png | [REVIEW] | Undetermined | - |
| results\figures\soe_vs_private_china.png | [REVIEW] | Undetermined | - |
| results\figures\tau_sensitivity_results.png | [REVIEW] | Undetermined | - |
| results\figures\transaction_cost_impact.png | [REVIEW] | Undetermined | - |
| results\tables\table_crisis_testing.csv | [DATA] | Input/Output tabular data | - |
| results\v1_final_results\crisis_comparison_tables.csv | [DATA] | Legacy Data | - |
| results\v1_final_results\factor_regression_results.csv | [DATA] | Legacy Data | - |
| results\v1_final_results\model_comparison_summary.csv | [DATA] | Legacy Data | - |
| results\v1_final_results\regime_performance_summary.csv | [DATA] | Legacy Data | - |
| results\v1_final_results\soe_vs_private_china_ownership_summary.csv | [DATA] | Legacy Data | - |
| results\v1_final_results\tau_sensitivity_results.csv | [DATA] | Legacy Data | - |
| results\v1_final_results\tri_market_summary.csv | [DATA] | Legacy Data | - |
| tests\test_backtest.py | [SUPPORT] | Testing framework | None |
| tests\test_black_litterman.py | [SUPPORT] | Testing framework | None |
| tests\test_data_loader.py | [SUPPORT] | Testing framework | None |
| tests\test_optimizer.py | [SUPPORT] | Testing framework | None |
| ui\desktop_gui.py | [CORE] | GUI Rendering | main.py, __main__.py |
| ui\plot_utils.py | [CORE] | GUI Rendering | desktop_gui.py |
| ui\__init__.py | [CORE] | GUI Rendering | None |
| visualization\asi_stability.png | [REVIEW] | Undetermined | - |
| visualization\drawdown_comparison.png | [REVIEW] | Undetermined | - |
| visualization\plotting_tools.py | [SUPPORT] | Imported utility | run_tri_market_pipeline.py |
| visualization\regime_performance_comparison.png | [REVIEW] | Undetermined | - |
| visualization\regime_probabilities.png | [REVIEW] | Undetermined | - |
| visualization\rolling_sharpe.png | [REVIEW] | Undetermined | - |


## 5. REMOVE_CANDIDATE LIST
The following files exhibit ZERO inbound imports, are not execution targets, and do not contribute to empirical outputs or the final paper:
- append_regime_doc.py
- append_results.py
- clear_all_yf_cache.py
- clear_yf_cache.py
- convert_to_docx.py
- create_paper.py
- create_updated_paper.py
- expand_compendium.py
- expand_compendium2.py
- export_final_pdf.py
- final_refinement.py
- find_yf_cache.py
- fix_compendium.py
- generate_academic_docs.py
- generate_academic_paper.py
- generate_docx_compendium.py
- generate_markdown.py
- generate_paper.py
- generate_research_figures.py
- generate_robustness_report.py
- get_india_metrics.py
- get_india_oos.py
- inject_markdown.py
- nuke_db.py
- repo_scanner.py
- run_india_covid.py
- SETUP.py
- sync_docs.py
- verify_crisis_recovery.py
- verify_installation.py
- verify_pyqt.py
- experiments\run_tau_sensitivity.py
- legacy\advanced_metrics.py
- legacy\backtesting.py
- legacy\empirical_study.py
- legacy\run_analysis.py
- legacy\visualizations.py
- legacy\core_legacy\soe_analysis.py
- legacy\portfolio_optimization\api\server.py
- legacy\portfolio_optimization\backtesting\rolling_backtest.py
- legacy\portfolio_optimization\config\settings.py
- legacy\portfolio_optimization\frontend\dashboard.py
- legacy\portfolio_optimization\models\advanced_metrics.py
- legacy\portfolio_optimization\models\black_litterman.py
- legacy\portfolio_optimization\models\visualizations.py
- legacy\portfolio_optimization\utils\installation_verify.py

## 6. REVIEW_REQUIRED LIST
- `experiments/` scripts (Check if tau sensitivity requires them or if it's dead code)
- Legacy test logs (e.g. `audit/` folder temporary markdown files)

## 7. IDENTIFIED RISKS & SOURCE VALIDATION
* **Data Sources**: ETF data mapped to Yahoo Finance. Factor data explicitly confirmed from Kenneth French Data Library. No manual CSV intervention identified affecting the final results.
* **Hardcoded Values**: `pipelines/run_tri_market_pipeline.py` hardcodes transaction costs (`0.0010`) and $\tau$ (`0.05`). `ui/desktop_gui.py` contains some hardcoded rendering logic but does not overwrite empirical source data.
* **Redundant Files**: Identified potential duplicate execution scripts and `legacy/` structural archives that are no longer strictly utilized but historically preserved.
* **Potential Breakpoints**: Deleting `legacy/` will instantly break the pipeline, as it relies on `legacy.core_legacy`. The refactoring plan was drafted but seemingly NOT executed; the system still uses the legacy module tree. DO NOT DELETE `legacy/`.
