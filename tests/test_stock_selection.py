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
from datetime import datetime, timedelta

import unittest
import pandas as pd
import numpy as np


class TestStock(unittest.TestCase):
    def setUp(self):
        self.stock_1 = Stock(
            ticker='Test1',
            price=pd.DataFrame(
                data={
                    'date': np.arange(datetime(2020, 1, 1), datetime(2020, 1, 30), timedelta(days=1)).astype(datetime),
                    'price': None}
            ),
        )
        self.stock_2 = Stock()
        self.stock_3 = Stock()

    def test_getSharpe(self):
        pass

    def test_getSortino(self):
        pass