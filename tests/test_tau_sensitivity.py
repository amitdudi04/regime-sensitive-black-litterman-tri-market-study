import unittest

import numpy as np
import pandas as pd

from analysis.tau_sensitivity import run_tau_sensitivity
from backtesting.paper_backtest import BacktestConfig


class TestTauSensitivity(unittest.TestCase):
    def test_all_tau_values_use_the_same_out_of_sample_window(self):
        rng = np.random.default_rng(73)
        index = pd.bdate_range("2020-01-01", periods=340)
        returns = pd.DataFrame(
            rng.normal(0.0003, 0.01, size=(len(index), 3)),
            index=index,
            columns=["A", "B", "C"],
        )
        config = BacktestConfig(window_size=252, rebalance_freq=63)
        result = run_tau_sensitivity(returns, config, [0.01, 0.05], market="US")

        self.assertEqual(result["Tau"].tolist(), [0.01, 0.05])
        self.assertEqual(result["OOS Start"].nunique(), 1)
        self.assertEqual(result["OOS End"].nunique(), 1)
        self.assertEqual(result["OOS Observations"].nunique(), 1)
        self.assertTrue(result["Sharpe Ratio"].map(np.isfinite).all())
        self.assertTrue(result["Tau Rule"].str.contains("fixed").all())

    def test_rejects_non_positive_or_duplicate_tau_values(self):
        index = pd.bdate_range("2020-01-01", periods=260)
        returns = pd.DataFrame(
            {"A": np.linspace(-0.01, 0.01, len(index)), "B": np.linspace(0.01, -0.01, len(index))},
            index=index,
        )
        config = BacktestConfig(window_size=252, rebalance_freq=4)
        with self.assertRaisesRegex(ValueError, "finite, positive"):
            run_tau_sensitivity(returns, config, [0.0])
        with self.assertRaisesRegex(ValueError, "unique"):
            run_tau_sensitivity(returns, config, [0.01, 0.01])


if __name__ == "__main__":
    unittest.main()
