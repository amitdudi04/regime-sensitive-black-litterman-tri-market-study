import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from core.data_loader import download_market_data


class TestDataLoader(unittest.TestCase):
    @patch("core.data_loader.yf.download")
    def test_multiindex_adjusted_close_and_missing_row_policy(self, mock_download):
        idx = pd.bdate_range("2024-01-01", periods=3)
        columns = pd.MultiIndex.from_product(
            [["Adj Close", "Close"], ["AAA", "BBB"]]
        )
        data = pd.DataFrame(
            [
                [100.0, 200.0, 99.0, 199.0],
                [101.0, np.nan, 100.0, 200.0],
                [102.0, 202.0, 101.0, 201.0],
            ],
            index=idx,
            columns=columns,
        )
        mock_download.return_value = data

        result = download_market_data(["AAA", "BBB"], "2024-01-01", "2024-02-01")

        self.assertEqual(list(result.columns), ["AAA", "BBB"])
        self.assertEqual(len(result), 2)
        self.assertNotIn(idx[1], result.index)
        self.assertEqual(result.loc[idx[0], "AAA"], 100.0)
        self.assertEqual(result.loc[idx[2], "BBB"], 202.0)


if __name__ == "__main__":
    unittest.main()
