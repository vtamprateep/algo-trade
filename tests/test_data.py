from datetime import datetime
from queue import Queue

import unittest
import numpy as np
import pandas as pd

from algo_trade.data import HistoricCSVDataHandler


class TestHistoricCSVDataHandler(unittest.TestCase):
    def setUp(self):
        data = pd.DataFrame(
            {
                'datetime':['1/3/94', '1/4/94', '1/5/94', '1/6/94', '1/7/94', '1/10/94', '1/11/94', '1/12/94'],
                'adj_close': [28.154894, 28.268501, 28.325314, 28.325314, 28.495695, 28.836512, 28.779718, 28.685057],
            }
        )
        data['datetime'] = pd.to_datetime(data['datetime'], infer_datetime_format=True)
        data.set_index('datetime', inplace=True)

        self.test_csv_handler = HistoricCSVDataHandler(Queue(), None, ['SPY'], test=True)
        self.test_csv_handler.ticker_data['SPY'] = data
        self.test_csv_handler.ticker_generator['SPY'] = data.iterrows()
        self.test_csv_handler.latest_ticker_data['SPY'] = list()

        for _ in range(4):
            self.test_csv_handler.update_bars()
            bar = next(self.test_csv_handler.ticker_data['SPY'].iterrows())

    def test_update_bars(self):
        self.assertEqual(len(self.test_csv_handler.latest_ticker_data['SPY']), 4)
        print(self.test_csv_handler.latest_ticker_data)

    def test_get_latest_bar(self):
        latest_bar = self.test_csv_handler.get_latest_bar('SPY')
        self.assertEqual(latest_bar[0].to_pydatetime(), datetime(1994,1,6))

    def test_get_latest_bars(self):
        latest_bar1 = self.test_csv_handler.get_latest_bars('SPY')
        latest_bar3 = self.test_csv_handler.get_latest_bars('SPY', 3)
        latest_bar6 = self.test_csv_handler.get_latest_bars('SPY', 6)

        self.assertEqual(len(latest_bar1), 1)
        self.assertEqual(latest_bar1[0][0].to_pydatetime(), datetime(1994,1,6))

        self.assertEqual(len(latest_bar3), 3)
        self.assertEqual(latest_bar3[0][0].to_pydatetime(), datetime(1994, 1, 4))
        self.assertEqual(len(latest_bar6), 4)

    def test_get_latest_bar_datetime(self):
        self.assertEqual(self.test_csv_handler.get_latest_bar_datetime('SPY'), datetime(1994,1,6))

    def test_get_latest_bar_value(self):
        self.assertEqual(self.test_csv_handler.get_latest_bar_value('SPY', 'adj_close'), 28.325314)

    def test_get_latest_bars_values(self):
        self.assertTrue(
            np.array_equal(
                self.test_csv_handler.get_latest_bars_values('SPY', 'adj_close', 2), 
                [28.325314, 28.325314],
            )
        )
        self.assertTrue(
            np.array_equal(
                self.test_csv_handler.get_latest_bars_values('SPY', 'adj_close', 5), 
                [28.154894, 28.268501, 28.325314, 28.325314],
            )
        )