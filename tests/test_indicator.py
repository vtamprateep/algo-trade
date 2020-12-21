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
        self.df4 = pd.DataFrame(
            data={
                'open': [1,2,3,4,5],
                'high': [1,2,3,4,5],
                'low': [1,2,3,4,5],
                'close': [1,2,3,4,5],
            },
            index = pd.date_range(start='1/1/2018', periods=5)
        )

    def test_mean(self):
        print(indicator.mean(self.df1))
        self.assertTrue(
            pd.Series.equals(
                indicator.mean(self.df1),
                pd.Series(data=1.0),
            )
        )
        self.assertTrue(
            pd.Series.equals(
                indicator.mean(self.df2),
                pd.Series(data=1.0)
            )
        )
        self.assertTrue(
            pd.Series.equals(
                indicator.mean(self.df3).round(1),
                pd.Series(data=3.0)
            )
        )
        self.assertTrue(
            pd.Series.equals(
                indicator.mean(self.df4),
                pd.Series(data=[3.0, 3.0, 3.0, 3.0], index=['open', 'high', 'low', 'close'])
            )
        )
        self.assertTrue(
            pd.Series.equals(
                indicator.mean(self.df4, geo=True).round(3),
                pd.Series(data=[2.605, 2.605, 2.605, 2.605], index=['open', 'high', 'low', 'close'])
            )
        )
        self.assertTrue(
            pd.Series.equals(
                indicator.mean(self.df4, pct=True).round(3),
                pd.Series(data=[0.521, 0.521, 0.521, 0.521], index=['open', 'high', 'low', 'close'])
            )
        )
        self.assertTrue(
            pd.Series.equals(
                indicator.mean(self.df4, pct=True, geo=True).round(3),
                pd.Series(data=[0.452, 0.452, 0.452, 0.452], index=['open', 'high', 'low', 'close'])
            )
        )

    def test_volatility(self):
        self.assertTrue(
            pd.Series.equals(indicator.volatility(self.df1), pd.Series(data=np.nan))
        )
        self.assertTrue(
            pd.Series.equals(indicator.volatility(self.df2), pd.Series(data=[0.0]))
        )
        self.assertTrue(
            pd.Series.equals(indicator.volatility(self.df3).round(3), pd.Series(data=[1.581]))
        )
        self.assertTrue(
            pd.Series.equals(indicator.volatility(self.df4).round(3), pd.Series(data=[1.581, 1.581, 1.581, 1.581], index=['open', 'high', 'low', 'close']))
        )
        self.assertTrue(
            pd.Series.equals(indicator.volatility(self.df4, True).round(3), pd.Series(data=[0.336, 0.336, 0.336, 0.336], index=['open', 'high', 'low', 'close']))
        )

    def test_sharpe(self):
        self.assertTrue(
            pd.Series.equals(
                indicator.sharpe(self.df1),
                pd.Series(data=np.nan),
            )
        )
        self.assertTrue(
            pd.Series.equals(
                indicator.sharpe(self.df2),
                pd.Series(data=np.nan),
            )
        )
        self.assertTrue(
            pd.Series.equals(
                indicator.sharpe(self.df3).round(3),
                pd.Series(data=1.550)
            )
        )
        self.assertTrue(
            pd.Series.equals(
                indicator.sharpe(self.df4).round(3),
                pd.Series(data=[1.55, 1.55, 1.55, 1.55], index=['open', 'high', 'low', 'close'])
            )
        )
        self.assertTrue(
            pd.Series.equals(
                indicator.sharpe(self.df3, rf=0.017).round(3),
                pd.Series(data=1.500)
            )
        )
        self.assertTrue(
            pd.Series.equals(
                indicator.sharpe(self.df3, rf=0.017, freq='daily').round(3),
                pd.Series(data=24.609)
            )
        )
        self.assertTrue(
            pd.Series.equals(
                indicator.sharpe(self.df3, rf=0.017, geo=True).round(3),
                pd.Series(data=1.288)
            )
        )