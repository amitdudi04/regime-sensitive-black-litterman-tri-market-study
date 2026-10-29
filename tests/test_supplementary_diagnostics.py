import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd

from analysis.supplementary_diagnostics import run_supplementary_diagnostics


class TestSupplementaryDiagnostics(unittest.TestCase):
    def test_regime_partition_and_bootstrap_metadata(self):
        dates = pd.bdate_range("2020-01-01", periods=120)
        rng = np.random.default_rng(12)
        benchmark = pd.Series(rng.normal(0, 0.01, len(dates)), index=dates)
        bl = pd.Series(rng.normal(0.0001, 0.012, len(dates)), index=dates)
        mv = pd.Series(rng.normal(0.0002, 0.015, len(dates)), index=dates)
        labels = pd.DataFrame({
            "Prob_Low_Vol": [0.9] * 60 + [0.1] * 60,
            "Prob_High_Vol": [0.1] * 60 + [0.9] * 60,
            "Regime": ["Low_Vol"] * 60 + ["High_Vol"] * 60,
        }, index=dates)
        with patch(
            "analysis.supplementary_diagnostics.fit_markov_regime_model",
            return_value=(labels, None),
        ):
            perf, states, test = run_supplementary_diagnostics(
                "US", benchmark, bl, mv,
                bootstrap_iterations=100, block_size=10, seed=8,
            )
        self.assertEqual(int(perf["Observations"].sum()), 120)
        self.assertEqual(len(states), 120)
        self.assertEqual(int(test.loc[0, "Paired Observations"]), 120)
        self.assertEqual(int(test.loc[0, "Iterations"]), 100)
        self.assertFalse(bool(test.loc[0, "Historical Paper Test Reproduction"]))

    def test_missing_or_insufficient_data_fail_closed(self):
        dates = pd.bdate_range("2020-01-01", periods=40)
        data = pd.Series(np.arange(40, dtype=float) / 100000, index=dates)
        with self.assertRaises(ValueError):
            run_supplementary_diagnostics("US", data, data, data)
