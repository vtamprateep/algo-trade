from account import Order, OrderBuilder

import unittest
import pandas as pd
import numpy as np


class TestOrder(unittest.TestCase):
    def test_attributes(self):
        # Test input checking
        with self.assertRaises(AssertionError):
            Order('MSFT', 5, 'Error', 'MARKET')
            Order('TEST', 5, 'BUY', 'Option')

        order1 = Order('msft', 5, 'Buy', 'Market')
        order2 = Order('GOOG', 0, 'sell', 'limit')

        self.assertEqual(order1.ticker, 'MSFT')
        self.assertEqual(order1.action, 'BUY')
        self.assertEqual(order1.order_type, 'MARKET')

        self.assertEqual(order2.ticker, 'GOOG')
        self.assertEqual(order2.action, 'SELL')
        self.assertEqual(order2.order_type, 'LIMIT')
        