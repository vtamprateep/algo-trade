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

from stock_selection import Stock, DataBuilder, Portfolio, InvalidMetric
from datetime import datetime, timedelta
from pandas._testing import assert_frame_equal

import unittest
import pandas as pd
import numpy as np


class TestDataBuilder(unittest.TestCase):
    def setUp(self):
        self.builder1 = DataBuilder()
        self.builder2 = DataBuilder()
        self.dataset1 = self.builder1.buildFake(0.1, 10, 30)
        self.dataset2 = self.builder2.buildFake(0.1, 20, 60)

        self.portfolio = Portfolio()

    def test_build_fake(self):
        self.assertIsInstance(self.dataset1, pd.DataFrame)
        self.assertEqual(self.dataset1.shape, (30, 1))
        self.assertEqual(self.dataset2.shape, (60, 1))

    def test_build_stocks(self):
        self.builder1.buildStocks(self.portfolio, ['MSFT', 'AAPL', 'AMZN', 'FB', 'GOOG', 'JNJ', 'V', 'PG'])
        self.assertEqual(len(self.portfolio.holdings), 8)

class TestStock(unittest.TestCase):
    def setUp(self):
        self.builder1 = DataBuilder()
        self.builder2 = DataBuilder()
        self.builder1.rng.seed(1)
        self.builder2.rng.seed(1)

        self.dataset1 = self.builder1.buildFake(0.1, 10, 30)
        self.dataset2 = self.builder2.buildFake(0.1, 20, 60)

        self.stock_1 = Stock(
            ticker='Test1',
            price=self.dataset1,
            rf = 0.017,
        )
        self.stock_2 = Stock(
            ticker='Test2',
            price=self.dataset2,
            rf = 0.017,
        )
        self.stock_3 = Stock(
            ticker='Test1',
            price=self.dataset2,
            rf = 0.04,
            mar=0,
        )

    def test_eq(self):
        self.assertEqual(self.stock_1, self.stock_3)
        self.assertNotEqual(self.stock_1, self.stock_2)
        self.assertEqual(len(set([self.stock_1, self.stock_3])), 1)

    def test_attributes(self):
        self.assertEqual(round(self.stock_1.sharpe, 5), 4.05163)
        self.assertEqual(round(self.stock_2.sharpe, 5), 1.47985)
        self.assertEqual(round(self.stock_3.sharpe, 5), 1.45442)
        self.assertEqual(round(self.stock_1.sortino, 5), 5.89172)
        self.assertEqual(round(self.stock_2.sortino, 5), 2.12125)
        self.assertEqual(round(self.stock_3.sortino, 5), 2.26207)
        self.assertIsInstance(self.stock_1.price_history.index, pd.DatetimeIndex)

class TestPortfolio(unittest.TestCase):
    def setUp(self):
        self.portfolio = Portfolio()
        self.builder1 = DataBuilder()
        self.builder2 = DataBuilder()
        self.builder1.rng.seed(1)
        self.builder2.rng.seed(1)

        self.dataset1 = self.builder1.buildFake(0.1, 10, 30)
        self.dataset2 = self.builder2.buildFake(0.1, 20, 60)

        self.stock_1 = Stock(
            ticker='Test1',
            price=self.dataset1,
            rf=0.017,
        )
        self.stock_2 = Stock(
            ticker='Test2',
            price=self.dataset2,
            rf=0.017,
        )

        self.portfolio.addStock(self.stock_1)
        self.portfolio.addStock(self.stock_2)

    def test_make_portfolio(self):
        self.assertEqual(len(self.portfolio.holdings), 2)
        
        assert_frame_equal(
            self.portfolio.makePortfolio('sharpe'),
            pd.DataFrame({
                'ticker':['Test1', 'Test2'],
                'sharpe_ratio':[4.05163, 1.47985],
            })
        )
        
        assert_frame_equal(
            self.portfolio.makePortfolio('sortino'),
            pd.DataFrame({
                'ticker':['Test1', 'Test2'],
                'sortino_ratio':[5.89172, 2.12125],
            })
        )

        with self.assertRaises(InvalidMetric, msg='invalid method') as cm:
            self.portfolio.makePortfolio('invalid method')