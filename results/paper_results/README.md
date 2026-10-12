# Paper Results

The CSV files in this directory preserve numerical tables from the earlier manuscript snapshot. They are not generated or overwritten by `python -m pipelines.run_tri_market_pipeline`; that command writes a new run to `results/generated/`.

The current correction branch changes the one-way-turnover convention, charges initial portfolio deployment, and uses adjusted-close ETF benchmark proxies. The saved `tri_market_summary.csv` therefore needs a fresh run before its performance values can be treated as current. The saved `crisis_summary.csv` and `tau_sensitivity.csv` are historical supplementary tables for which the documented pipeline does not currently provide a generator. In particular, the 2008 crisis is outside the main requested sample, and the crisis helper alone does not calculate drawdown or recovery statistics.

Preserve these files as historical evidence; do not silently overwrite them or describe them as verified outputs of the corrected pipeline.