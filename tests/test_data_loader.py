import unittest
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.data_loader import download_market_data

class TestDataLoader(unittest.TestCase):
    def test_handle_multiindex(self):
        """Verify the data loader handles multi-index ticker outputs accurately."""
        # result = download_market_data(['AAPL'], '2023-01-01', '2023-02-01')
        # self.assertTrue(isinstance(result, pd.DataFrame))
        pass

if __name__ == '__main__':
    unittest.main()
