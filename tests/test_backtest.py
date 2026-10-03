import unittest

import numpy as np
import pandas as pd

from backtesting.paper_backtest import BacktestConfig, run_paper_backtest


class TestPaperBacktest(unittest.TestCase):
    def _returns(self):
        rng = np.random.default_rng(123)
        idx = pd.bdate_range("2020-01-01", periods=340)
        values = rng.normal(0.0003, 0.01, size=(len(idx), 3))
        return pd.DataFrame(values, index=idx, columns=["A", "B", "C"])

    def _config(self, transaction_cost_rate=0.001):
        return BacktestConfig(
            window_size=252,
            rebalance_freq=63,
            risk_aversion=3.0,
            transaction_cost_rate=transaction_cost_rate,
            view_blend=0.10,
            view_uncertainty_scale=10.0,
        )

    def test_out_of_sample_starts_after_training_window(self):
        returns = self._returns()
        packet = run_paper_backtest(returns, self._config())
        daily = packet["daily_returns"]

        self.assertEqual(daily.index[0], returns.index[252])
        self.assertEqual(len(daily), len(returns) - 252)
        self.assertEqual(packet["turnover"].iloc[0]["Black-Litterman"], 0.0)
        self.assertEqual(packet["turnover"].iloc[0]["Markowitz"], 0.0)

    def test_future_data_does_not_change_earlier_oos_returns(self):
        returns = self._returns()
        base = run_paper_backtest(returns, self._config())["daily_returns"]

        changed = returns.copy()
        changed.iloc[320:] = changed.iloc[320:] * 50.0
        altered = run_paper_backtest(changed, self._config())["daily_returns"]

        cutoff = returns.index[319]
        pd.testing.assert_frame_equal(base.loc[:cutoff], altered.loc[:cutoff])

    def test_weights_are_long_only_and_fully_invested(self):
        packet = run_paper_backtest(self._returns(), self._config())
        for model in ["black_litterman", "markowitz"]:
            weights = packet["weights"][model]
            self.assertTrue((weights >= -1e-10).all().all())
            np.testing.assert_allclose(weights.sum(axis=1).values, 1.0, atol=1e-7)

    def test_transaction_costs_do_not_improve_net_return(self):
        packet = run_paper_backtest(self._returns(), self._config(0.001))
        daily = packet["daily_returns"]
        self.assertLessEqual(
            daily["black_litterman_net"].sum(),
            daily["black_litterman_gross"].sum() + 1e-12,
        )
        self.assertLessEqual(
            daily["markowitz_net"].sum(),
            daily["markowitz_gross"].sum() + 1e-12,
        )


if __name__ == "__main__":
    unittest.main()
