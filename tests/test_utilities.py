import numpy as np
import pandas as pd
import unittest

import utilities

class TestFunction(unittest.TestCase):
    def setUp(self):
        # 20 daily SPY prices
        self.spy_series = pd.Series([320.632233,321.672821,315.831909,318.178101,323.027496,326.757843,327.85733,326.109955,328.544495,329.113861,331.234283,330.880859,331.41098,330.556915,332.13736,330.772919,327.366516,316.509247,306.918335,305.789459])
        self.spy_return = self.spy_series.pct_change()
        self.spy_pnl = (self.spy_return + 1).cumprod()

    def test_create_sharpe_ratio(self):
        self.assertAlmostEqual(
            utilities.create_sharpe_ratio(self.spy_return), -3.05842361
        )
        self.assertAlmostEqual(
            utilities.create_sharpe_ratio(self.spy_return, rf=0.01), -3.1087377
        )
        self.assertAlmostEqual(
            utilities.create_sharpe_ratio(self.spy_return, periods=12, rf=0.01), -0.897971
        )

    def test_create_drawdowns(self):
        _, test_ddmax, test_duration = utilities.create_drawdowns(self.spy_pnl)

        self.assertAlmostEqual(test_ddmax, 0.08217484)
        self.assertEqual(test_duration, 5)