import unittest
import numpy as np
import pandas as pd

from backtesting.rolling_backtest import run_rolling_backtest


class TestBacktester(unittest.TestCase):
    def _returns(self):
        rng = np.random.default_rng(123)
        idx = pd.bdate_range("2020-01-01", periods=330)
        values = rng.normal(0.0003, 0.01, size=(len(idx), 3))
        return pd.DataFrame(values, index=idx, columns=["A", "B", "C"])

    def test_out_of_sample_starts_after_training_window(self):
        returns = self._returns()
        initial = pd.Series([1 / 3] * 3, index=returns.columns)
        oos, weights = run_rolling_backtest(
            returns,
            initial,
            window_size=252,
            rebalance_freq=63,
            model_type="markowitz",
        )
        self.assertEqual(oos.index[0], returns.index[252])
        self.assertEqual(weights.index[0], returns.index[252])
        self.assertEqual(len(oos), len(returns) - 252)

    def test_future_data_does_not_change_earlier_oos_returns(self):
        returns = self._returns()
        initial = pd.Series([1 / 3] * 3, index=returns.columns)

        base, _ = run_rolling_backtest(
            returns,
            initial,
            window_size=252,
            rebalance_freq=63,
            model_type="markowitz",
        )

        changed = returns.copy()
        changed.iloc[300:] = changed.iloc[300:] * 50.0
        altered, _ = run_rolling_backtest(
            changed,
            initial,
            window_size=252,
            rebalance_freq=63,
            model_type="markowitz",
        )

        pd.testing.assert_series_equal(base.loc[: returns.index[299]], altered.loc[: returns.index[299]])


if __name__ == "__main__":
    unittest.main()
