'''
The test_stock_selection module includes unit tests for the following classes in the stock_selection module.

Overview
========

This module tests the following classes:
    - Stock

Stock Tests
-----------

..  autoclass:: TestStock

Usage
=====

This module uses the standard text runner, so it can be executed from the command line as follows:: python test_stock_selection.py
'''

from portfolio import Stock, DataBuilder, Portfolio, InvalidMetric
from datetime import datetime, timedelta
from pandas._testing import assert_frame_equal
from unittest.mock import Mock, patch

import unittest
import pandas as pd
import numpy as np


class TestStock(unittest.TestCase):
    def setUp(self):
        self.dataset1 = pd.DataFrame(
            data={
                'datetime': pd.date_range(start='1/1/2018', periods=5),
                'open': [0,1,2,3,4],
                'high': [0,1,2,3,4],
                'low': [0,1,2,3,4],
                'close': [0,1,2,3,4],
            }
        )

        self.dataset2 = pd.DataFrame(
            data={
                'datetime': pd.date_range(start='1/1/2018', periods=5),
                'open': [1,2,3,4,5],
                'high': [1,2,3,4,5],
                'low': [1,2,3,4,5],
                'close': [1,2,3,4,5],
            }
        )

        self.stock_1 = Stock(
            ticker='Test1',
            price_history=self.dataset1,
        )
        self.stock_2 = Stock(
            ticker='Test2',
            price_history=self.dataset2,
        )
        self.stock_3 = Stock(
            ticker='Test1',
            price_history=self.dataset2,
        )

    def test_eq(self):
        self.assertEqual(self.stock_1, self.stock_3)
        self.assertNotEqual(self.stock_1, self.stock_2)
        self.assertEqual(len(set([self.stock_1, self.stock_3])), 1)

class TestDataBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = DataBuilder()
        self.mock_portfolio = Mock()
        self.mock_stock = Mock()
        self.mock_client = Mock()
        self.mock_client.get_price_history = Mock(
            name='response',
            return_value=Mock(
                name='json',
                json=Mock(
                    return_value={'candles': None}
                )
                
            )
        )

    def test_yahoofinance(self):
        with patch('portfolio.Stock', new=self.mock_stock):
            self.builder.YahooFinance(self.mock_portfolio, ['MSFT', 'AAPL', 'AMZN', 'FB', 'GOOG', 'JNJ', 'V', 'PG'])
        self.assertEqual(self.mock_portfolio.addStock.call_count, 8)
        self.assertEqual(self.mock_stock.call_count, 8)

    def test_tdameritrade(self):
        with patch('portfolio.Stock', new=self.mock_stock):
            self.builder.TDAmeritrade(self.mock_client, self.mock_portfolio, ['MSFT', 'AAPL', 'AMZN', 'FB', 'GOOG', 'JNJ', 'V', 'PG'])
        self.mock_client.set_enforce_enums.assert_called_with(enforce_enums=True)
        self.assertEqual(self.mock_client.set_enforce_enums.call_count, 2)
        self.assertEqual(self.mock_portfolio.addStock.call_count, 8)
        self.assertEqual(self.mock_stock.call_count, 8)
        self.assertEqual(self.mock_client.get_price_history.call_count, 8)

class TestPortfolio(unittest.TestCase):
    def setUp(self):
        self.portfolio = Portfolio()

        self.dataset1 = pd.DataFrame(
            data={
                'datetime': pd.date_range(start='1/1/2018', periods=5),
                'open': [0,1,2,3,4],
                'high': [0,1,2,3,4],
                'low': [0,1,2,3,4],
                'close': [0,1,2,3,4],
            }
        )

        self.dataset2 = pd.DataFrame(
            data={
                'datetime': pd.date_range(start='1/1/2018', periods=5),
                'open': [1,2,3,4,5],
                'high': [1,2,3,4,5],
                'low': [1,2,3,4,5],
                'close': [1,2,3,4,5],
            }
        )

        self.stock_1 = Stock(
            ticker='Test1',
            price_history=self.dataset1,
        )
        self.stock_2 = Stock(
            ticker='Test2',
            price_history=self.dataset2,
        )
        self.stock_3 = Stock(
            ticker='Test1',
            price_history=self.dataset2,
        )

    def test_portfolio(self):
        for stock in [self.stock_1, self.stock_2, self.stock_3]:
            self.portfolio.add_stock(stock)

        self.assertEqual(len(self.portfolio.holdings), 2)
        self.assertIn(self.stock_1, self.portfolio.holdings)
        self.assertIn(self.stock_2, self.portfolio.holdings)