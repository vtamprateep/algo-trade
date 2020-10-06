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

from stock_selection import Stock, DataBuilder, Portfolio
from datetime import datetime, timedelta

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
        )
        self.stock_2 = Stock(
            ticker='Test2',
            price=self.dataset2,
        )
        self.stock_3 = Stock(
            ticker='Test1',
            price=self.dataset2,
        )

    def test_eq(self):
        self.assertEqual(self.stock_1, self.stock_3)
        self.assertNotEqual(self.stock_1, self.stock_2)
        self.assertEqual(len(set([self.stock_1, self.stock_3])), 1)

    def test_attributes(self):
        self.assertEqual(round(self.stock_1.sharpe, 5), 8.00329)
        self.assertEqual(round(self.stock_2.sharpe, 5), 4.38710)
        self.assertEqual(round(self.stock_1.sortino, 5), 8.64454)
        self.assertEqual(round(self.stock_2.sortino, 5), 4.48422)
        self.assertIsInstance(self.stock_1.price_history.index, pd.DatetimeIndex)
        