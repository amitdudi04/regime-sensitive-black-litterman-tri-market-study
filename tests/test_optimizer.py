import unittest
import numpy as np
import pandas as pd

from models.optimizer import compute_mean_variance_weights


class TestOptimizer(unittest.TestCase):
    def test_long_only_fully_invested_constraints(self):
        expected = pd.Series([0.08, 0.11, 0.06], index=["A", "B", "C"])
        cov = pd.DataFrame(
            [
                [0.040, 0.010, 0.005],
                [0.010, 0.050, 0.008],
                [0.005, 0.008, 0.030],
            ],
            index=expected.index,
            columns=expected.index,
        )
        weights = compute_mean_variance_weights(expected, cov, risk_aversion=3.0)

        self.assertAlmostEqual(float(weights.sum()), 1.0, places=7)
        self.assertTrue((weights >= -1e-10).all())
        self.assertTrue((weights <= 1.0 + 1e-10).all())
        self.assertTrue(np.isfinite(weights.values).all())


if __name__ == "__main__":
    unittest.main()
