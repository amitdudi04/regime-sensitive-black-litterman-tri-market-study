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
        self.assertAlmostEqual(packet["turnover"].iloc[0]["Black-Litterman"], 1.0, places=6)
        self.assertAlmostEqual(packet["turnover"].iloc[0]["Markowitz"], 1.0, places=6)
        self.assertAlmostEqual(
            daily["black_litterman_gross"].iloc[0] - daily["black_litterman_net"].iloc[0],
            self._config().transaction_cost_rate,
            places=10,
        )
        self.assertAlmostEqual(
            daily["markowitz_gross"].iloc[0] - daily["markowitz_net"].iloc[0],
            self._config().transaction_cost_rate,
            places=10,
        )

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

    def test_buy_and_hold_returns_drift_weights_without_interim_trades(self):
        from backtesting.paper_backtest import _buy_and_hold_daily_returns, _drifted_weights

        dates = pd.bdate_range("2024-01-01", periods=2)
        assets = pd.DataFrame({"A": [0.20, 0.00], "B": [0.00, 0.20]}, index=dates)
        target = pd.Series({"A": 0.5, "B": 0.5})
        realized = _buy_and_hold_daily_returns(assets, target)
        self.assertAlmostEqual(realized.iloc[0], 0.10)
        self.assertAlmostEqual(realized.iloc[1], 0.20 / 2.20)
        final_weights = _drifted_weights(target, assets)
        self.assertAlmostEqual(final_weights["A"], 0.6 / 1.2)
        self.assertAlmostEqual(final_weights.sum(), 1.0)
        self.assertAlmostEqual(float((1.0 + realized).prod()), 1.21)

    def test_asi_excludes_first_unobserved_difference(self):
        from backtesting.allocation_stability_index import compute_asi

        weights = pd.DataFrame(
            [[0.5, 0.5], [0.7, 0.3], [0.6, 0.4]],
            columns=["A", "B"],
        )
        self.assertAlmostEqual(compute_asi(weights), 0.3)

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
