import unittest
import numpy as np
import pandas as pd

from analysis.ownership_research import evaluate_dated_ownership


class TestDatedOwnership(unittest.TestCase):
    def setUp(self):
        self.dates = pd.bdate_range("2022-01-01", periods=35)
        self.returns = pd.DataFrame(
            {"SOE_1": np.repeat(0.001, 35), "PRIVATE_1": np.repeat(0.002, 35)},
            index=self.dates,
        )
        self.evidence = pd.DataFrame({
            "security_id": ["SOE_1", "PRIVATE_1"],
            "available_at": [self.dates[0], self.dates[0]],
            "group": ["SOE", "Private"],
        })

    def test_explicit_ownership_evidence_yields_descriptive_gross_metrics(self):
        summary, daily = evaluate_dated_ownership(self.returns, self.evidence)
        self.assertEqual(len(summary), 2)
        self.assertEqual(len(daily), 35)
        self.assertTrue((summary["Published Paper Table 6 Reproduced"] == False).all())
        self.assertAlmostEqual(float(daily["SOE"].iloc[0]), 0.001)
        self.assertAlmostEqual(float(daily["Private"].iloc[0]), 0.002)

    def test_future_only_classifications_cannot_backfill(self):
        late = self.evidence.copy()
        late["available_at"] = self.dates[-4]
        with self.assertRaises(ValueError):
            evaluate_dated_ownership(self.returns, late)

    def test_missing_original_group_evidence_fails_closed(self):
        with self.assertRaises(ValueError):
            evaluate_dated_ownership(self.returns, self.evidence.iloc[:1])

    def test_invalid_observed_value_in_partly_missing_row_is_rejected(self):
        # A NaN in a different security must not hide this observed invalid return.
        for invalid in (np.inf, -1.0, -2.0):
            returns = self.returns.copy()
            returns.iloc[0] = [invalid, np.nan]
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                evaluate_dated_ownership(returns, self.evidence)
