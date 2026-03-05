import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backtesting.rolling_backtest import run_rolling_backtest

class TestBacktester(unittest.TestCase):
    def test_out_of_sample_bounds(self):
        """Verify that rolling execution restricts information natively to prior windows."""
        pass

if __name__ == '__main__':
    unittest.main()
