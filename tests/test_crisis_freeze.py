import unittest

import pandas as pd

from backtesting.crisis_freeze import execute_crisis_freeze


class TestCrisisFreeze(unittest.TestCase):
    def test_uses_last_weight_strictly_before_crisis_start(self):
        idx = pd.to_datetime(["2019-12-01", "2020-02-15", "2020-03-15"])
        weights = pd.DataFrame(
            [[0.6, 0.4], [0.2, 0.8], [0.1, 0.9]],
            index=idx,
            columns=["A", "B"],
        )

        frozen = execute_crisis_freeze(weights, "2020-02-15", "2020-04-01")

        self.assertEqual(len(frozen), 2)
        self.assertTrue((frozen["A"] == 0.6).all())
        self.assertTrue((frozen["B"] == 0.4).all())


if __name__ == "__main__":
    unittest.main()
