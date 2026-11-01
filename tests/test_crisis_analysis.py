import unittest

import numpy as np
import pandas as pd

from analysis.crisis_analysis import calculate_crisis_metrics


class TestCrisisAnalysis(unittest.TestCase):
    def test_crisis_metrics_use_frozen_weights_and_recover_to_crisis_start_value(self):
        dates = pd.bdate_range("2020-01-01", periods=100)
        values_a = np.array([0.001 * ((i % 5) - 2) for i in range(len(dates))], dtype=float)
        values_b = np.array([0.0015 * ((i % 4) - 1.5) for i in range(len(dates))], dtype=float)
        crisis_returns = np.array([-0.08, -0.10, -0.12, -0.08, -0.06])
        values_a[20:25] = crisis_returns
        values_b[20:25] = crisis_returns
        values_a[25:] = 0.20
        values_b[25:] = 0.20
        assets = pd.DataFrame({"A": values_a, "B": values_b}, index=dates)
        weights = pd.DataFrame(
            [[0.7, 0.3], [0.6, 0.4], [0.2, 0.8]],
            index=[dates[5], dates[19], dates[30]],
            columns=["A", "B"],
        )

        metrics = calculate_crisis_metrics(
            assets,
            weights,
            dates[20].date().isoformat(),
            dates[24].date().isoformat(),
            pre_crisis_window=20,
        )

        self.assertLess(float(metrics["Max Drawdown"]), -0.30)
        self.assertGreater(float(metrics["Volatility Spike"]), 0.0)
        self.assertEqual(metrics["Pre-Crisis Observations"], 20)
        self.assertEqual(metrics["Crisis Observations"], 5)
        self.assertEqual(metrics["Recovery Trading Days"], 3)
        self.assertEqual(metrics["Crisis First Trading Day"], dates[20].date().isoformat())
        self.assertEqual(metrics["Crisis Last Trading Day"], dates[24].date().isoformat())
        self.assertEqual(metrics["Frozen Weights"], {"A": 0.6, "B": 0.4})

    def test_self_financing_buy_hold_crisis_reports_initial_loss(self):
        dates = pd.bdate_range("2024-01-01", periods=14)
        a = np.array([0.001, -0.001] * 6 + [-0.5, 1.0], dtype=float)
        b = np.array([0.0] * 14, dtype=float)
        assets = pd.DataFrame({"A": a, "B": b}, index=dates)
        weights = pd.DataFrame(
            [[0.5, 0.5]],
            index=[dates[11]],
            columns=["A", "B"],
        )
        record = calculate_crisis_metrics(
            assets,
            weights,
            dates[12].date().isoformat(),
            dates[13].date().isoformat(),
            pre_crisis_window=10,
        )
        self.assertAlmostEqual(record["Buy-Hold Max Drawdown"], -0.25)
        self.assertEqual(record["Buy-Hold Recovery Trading Days"], 1)
        self.assertEqual(record["Buy-Hold Trough Date"], dates[12].date().isoformat())
        self.assertEqual(record["Buy-Hold Recovery Date"], dates[13].date().isoformat())


if __name__ == "__main__":
    unittest.main()
