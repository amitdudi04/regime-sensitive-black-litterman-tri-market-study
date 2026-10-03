import unittest
import numpy as np
import pandas as pd

from models.black_litterman_model import (
    compute_implied_equilibrium_returns,
    compute_black_litterman_posterior,
)


class TestBlackLitterman(unittest.TestCase):
    def setUp(self):
        self.cov = pd.DataFrame(
            [[0.04, 0.01], [0.01, 0.09]],
            index=["A", "B"],
            columns=["A", "B"],
        )
        self.weights = np.array([0.6, 0.4])
        self.risk_aversion = 2.5

    def test_equilibrium_returns_match_formula(self):
        pi = compute_implied_equilibrium_returns(
            self.cov, self.weights, self.risk_aversion
        )
        expected = self.risk_aversion * self.cov.values.dot(self.weights)
        np.testing.assert_allclose(pi.values, expected)

    def test_no_views_returns_prior(self):
        pi = compute_implied_equilibrium_returns(
            self.cov, self.weights, self.risk_aversion
        )
        posterior = compute_black_litterman_posterior(
            pi, self.cov, P=None, Q=None, Omega=None, tau=0.05
        )
        np.testing.assert_allclose(posterior.values, pi.values)

    def test_views_produce_finite_posterior(self):
        pi = compute_implied_equilibrium_returns(
            self.cov, self.weights, self.risk_aversion
        )
        p = np.eye(2)
        q = np.array([0.08, 0.05])
        omega = np.diag([0.01, 0.01])
        posterior = compute_black_litterman_posterior(
            pi, self.cov, P=p, Q=q, Omega=omega, tau=0.05
        )
        self.assertTrue(np.isfinite(posterior.values).all())
        self.assertEqual(list(posterior.index), ["A", "B"])


if __name__ == "__main__":
    unittest.main()
