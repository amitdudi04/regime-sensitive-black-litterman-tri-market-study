import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.verify_paper_results import PAPER_DIR, compare_tables


class TestPaperReconciliation(unittest.TestCase):
    def test_missing_generated_outputs_are_never_claimed_as_reproduced(self):
        with tempfile.TemporaryDirectory() as temp:
            report = compare_tables(PAPER_DIR, Path(temp))
        self.assertGreater(len(report), 0)
        self.assertTrue((report["status"] == "MISSING").all())

    def test_all_identical_numeric_reference_cells_are_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            tri = pd.read_csv(PAPER_DIR / "tri_market_summary.csv")
            tri = tri.rename(columns={"Turnover": "Average Rebalance Turnover"})
            tri.to_csv(out / "tri_market_summary.csv", index=False)
            crises = pd.read_csv(PAPER_DIR / "crisis_summary.csv")
            crises.to_csv(out / "crisis_summary.csv", index=False)
            tau = pd.read_csv(PAPER_DIR / "tau_sensitivity.csv")
            tau = tau.rename(columns={"Reported Black-Litterman Sharpe": "Sharpe Ratio"})
            tau.to_csv(out / "tau_sensitivity.csv", index=False)
            report = compare_tables(PAPER_DIR, out)
            self.assertTrue((report["status"] == "MATCH").all())

            tri.loc[tri["Model"].eq("Black-Litterman") & tri["Market"].eq("US"),
                    "Sharpe Ratio"] = 999.0
            tri.to_csv(out / "tri_market_summary.csv", index=False)
            altered = compare_tables(PAPER_DIR, out)
            self.assertTrue((altered["status"] == "MISMATCH").any())

    def test_ambiguous_generated_keys_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            tri = pd.read_csv(PAPER_DIR / "tri_market_summary.csv")
            pd.concat([tri, tri], ignore_index=True).to_csv(
                out / "tri_market_summary.csv", index=False
            )
            with self.assertRaises(ValueError):
                compare_tables(PAPER_DIR, out)


if __name__ == "__main__":
    unittest.main()
