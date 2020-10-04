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

from stock_selection import Stock
from model import PriceBuilder
from datetime import datetime, timedelta

import unittest
import pandas as pd
import numpy as np


class TestPriceBuilder(unittest.TestCase):
    def setUp(self):
        self.builder1 = PriceBuilder(0.1, 10, 30)
        self.builder2 = PriceBuilder(0.1, 20, 60)
        self.dataset1 = self.builder1.build()
        self.dataset2 = self.builder2.build()

    def test_build(self):
        self.assertIsInstance(self.dataset1, pd.DataFrame)
        self.assertEqual(self.dataset1.shape, (30, 2))
        self.assertEqual(self.dataset2.shape, (60, 2))


class TestStock(unittest.TestCase):
    def setUp(self):
        self.builder1 = PriceBuilder(0.1, 10, 30)
        self.builder2 = PriceBuilder(0.1, 20, 60)
        self.builder1.rng.seed(1)
        self.builder2.rng.seed(1)

        self.dataset1 = self.builder1.build()
        self.dataset2 = self.builder2.build()

        self.stock_1 = Stock(
            ticker='Test1',
            price=self.dataset1,
        )
        self.stock_2 = Stock(
            ticker='Test2',
            price=self.dataset2,
        )

    def test_getSharpe(self):
        self.assertEqual(round(self.stock_1.getSharpe(), 5), 8.00329)
        self.assertEqual(round(self.stock_2.getSharpe(), 5), 4.38710)

    def test_getSortino(self):
        self.assertEqual(round(self.stock_1.getSortino(), 5), 8.64454)
        self.assertEqual(round(self.stock_2.getSortino(), 5), 4.48422)