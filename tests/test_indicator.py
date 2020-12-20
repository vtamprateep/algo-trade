from portfolio import DataBuilder

import pandas as pd
import numpy as np
import unittest
import indicator


class TestIndicator(unittest.TestCase):
    def setUp(self):
        self.df1 = pd.DataFrame(
            data = [1]
        )

        self.df2 = pd.DataFrame(
            data = [1, 1, 1, 1, 1]
        )

        self.df3 = pd.DataFrame(
            data = [1, 2, 3, 4, 5]
        )
        self.df5 = pd.DataFrame(
            data={
                'open': [1,2,3,4,5],
                'high': [1,2,3,4,5],
                'low': [1,2,3,4,5],
                'close': [1,2,3,4,5],
            },
            index = pd.date_range(start='1/1/2018', periods=5)
        )

    def test_volatility(self):
        self.assertTrue(
            pd.Series.equals(
                indicator.volatility(self.df1),
                pd.Series(data=np.nan),
            )
        )
        self.assertTrue(
            pd.Series.equals(
                indicator.volatility(self.df2),
                pd.Series(data=[0.0])
            )
        )
        self.assertTrue(
            pd.Series.equals(
                indicator.volatility(self.df3).round(3),
                pd.Series(data=[1.581])
            )
        )