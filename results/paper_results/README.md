# Paper Results

The CSV files in this directory preserve numerical tables from the earlier manuscript snapshot. They are not generated or overwritten by `python -m pipelines.run_tri_market_pipeline`; that command writes a new run to `results/generated/`.

The current correction branch changes the one-way-turnover convention, charges initial portfolio deployment, and uses adjusted-close ETF benchmark proxies. The saved `tri_market_summary.csv` therefore needs a fresh run before its performance values can be treated as current. The saved `crisis_summary.csv` and `tau_sensitivity.csv` are historical supplementary tables for which the documented pipeline does not currently provide a generator. In particular, the 2008 crisis is outside the main requested sample, and the crisis helper alone does not calculate drawdown or recovery statistics.

The manuscript also reports regime-conditioned performance, cross-market factor-regression inference, an SOE/private comparison and volatility/ASI significance tests. The documented end-to-end command does not persist all of those tables. In particular, the factor-regression helper loads U.S. factors, while the SOE/private helper requires an external ownership mapping and returns descriptive statistics rather than a hypothesis test. Those manuscript claims need dedicated, tested generators and appropriately scoped interpretations before they are presented as reproducible findings.

Preserve these files as historical evidence; do not silently overwrite them or describe them as verified outputs of the corrected pipeline.