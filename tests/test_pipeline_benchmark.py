import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

from pipelines.tri_market_pipeline import (
    MARKETS,
    _aligned_benchmark_series,
    _benchmark_returns,
    _load_or_download_prices,
    _performance,
)


class TestPipelineBenchmarkHandling(unittest.TestCase):
    @patch("pipelines.tri_market_pipeline.download_market_data", return_value=pd.DataFrame())
    def test_missing_benchmark_is_reported_as_empty_instead_of_crashing(self, _download):
        target = pd.date_range("2020-01-01", periods=5, freq="B")

        result = _benchmark_returns("^MISSING", "2020-01-01", "2020-02-01", target)

        self.assertTrue(result.empty)
        self.assertEqual(result.name, "^MISSING")

    def test_benchmark_constituent_is_aligned_to_the_strategy_oos_dates(self):
        dates = pd.date_range("2020-01-01", periods=5, freq="B")
        market_returns = pd.DataFrame(
            {"A": [0.01, 0.02, -0.01, 0.00, 0.03], "B": [0.0] * 5},
            index=dates,
        )
        target = dates[[1, 3, 4]]

        result = _aligned_benchmark_series(
            market_returns, "A", "2020-01-01", "2020-02-01", target
        )

        pd.testing.assert_series_equal(result, market_returns.loc[target, "A"].rename("A"))

    def test_current_benchmarks_are_adjusted_close_proxies_inside_each_universe(self):
        for market, spec in MARKETS.items():
            with self.subTest(market=market):
                self.assertIn(spec["benchmark"], spec["tickers"])
                self.assertIn("proxy", spec["benchmark_label"].lower())

    def test_performance_metrics_report_their_actual_sample_window(self):
        dates = pd.date_range("2020-01-02", periods=4, freq="B")
        series = pd.Series([0.01, -0.02, 0.005, 0.01], index=dates)

        result = _performance(series)

        self.assertEqual(result["Metric Sample Start"], dates[0].date().isoformat())
        self.assertEqual(result["Metric Sample End"], dates[-1].date().isoformat())
        self.assertEqual(result["Metric Observations"], 4)
        self.assertTrue(np.isfinite(result["Sharpe Ratio"]))

    def test_price_snapshot_is_verified_and_reused_for_identical_request(self):
        dates = pd.bdate_range("2020-01-01", periods=4)
        prices = pd.DataFrame(
            {"A": [10.0, 10.5, 10.2, 10.8], "B": [20.0, 20.1, 20.4, 20.3]},
            index=dates,
        )
        with tempfile.TemporaryDirectory() as temporary:
            with (
                patch("pipelines.tri_market_pipeline.RESULTS_DIR", Path(temporary)),
                patch("pipelines.tri_market_pipeline.download_market_data", return_value=prices) as download,
            ):
                first, first_meta = _load_or_download_prices(
                    "Test", ["A", "B"], "2020-01-01", "2020-02-01"
                )
                self.assertEqual(download.call_count, 1)
                with patch(
                    "pipelines.tri_market_pipeline.download_market_data",
                    side_effect=AssertionError("verified snapshot should be reused"),
                ):
                    second, second_meta = _load_or_download_prices(
                        "Test", ["A", "B"], "2020-01-01", "2020-02-01"
                    )

        pd.testing.assert_frame_equal(first, second, check_freq=False)
        self.assertEqual(first_meta["sha256"], second_meta["sha256"])
        self.assertEqual(first_meta["observations"], 4)


if __name__ == "__main__":
    unittest.main()
