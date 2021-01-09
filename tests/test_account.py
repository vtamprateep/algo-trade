from account import AccountClient, Order
from unittest.mock import Mock, call
from tda.orders import equities

import unittest
import pandas as pd
import numpy as np


class TestAccountClient(unittest.TestCase):
    def setUp(self):
        self.client_mock = Mock()
        self.acc_id_mock = Mock()

        self.test_account = AccountClient(
            self.client_mock,
            self.acc_id_mock,
        )

        self.order_book = {
            Order('Ticker1', 1, 'SELL', 'MARKET'),
            Order('Ticker2', 1, 'SELL', 'MARKET'),
            Order('Ticker3', 1, 'SELL', 'MARKET'),
            Order('Ticker4', 1, 'SELL', 'MARKET'),
            Order('Ticker5', 1, 'SELL', 'MARKET'),
            Order('Ticker6', 5, 'BUY', 'MARKET'),
            Order('GOOG', 5, 'BUY', 'LIMIT', 500),
        }

    def test_buildOrder(self):
        pass
    
    def test_placeOrderTDAmeritrade(self):
        pass

class TestOrder(unittest.TestCase):
    def test_order(self):
        order1 = Order('MSFT', 5, 'BUY', 'MARKET')
        order2 = Order('MSFT', 5, 'BUY', 'MARKET')
        order3 = Order('GOOG', 5, 'BUY', 'LIMIT', 500)

        self.assertEqual(order1, order2)
        self.assertNotEqual(order1, order3)
        self.assertNotEqual(order2, order3)

        with self.assertRaises(AssertionError) as err:
            order4 = Order('MSFT', 0, 'BUY', 'MARKET')
            order5 = Order('MSFT', -5, 'SELL', 'MARKET')
            order6 = Order('GOOG', 10, 'BUY', 'LIMIT')