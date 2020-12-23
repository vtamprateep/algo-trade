from account import Order, OrderBuilder, AccountClient
from unittest.mock import Mock

import unittest
import pandas as pd
import numpy as np


class TestAccountClient(unittest.TestCase):
    def setUp(self):
        self.client_mock = Mock()

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

        
class TestOrderBuilder(unittest.TestCase):
    def setUp(self):
        self.order_builder = OrderBuilder()

        self.cur_port = pd.DataFrame(
            data={
                'ticker': ['Ticker1', 'Ticker2', 'Ticker3', 'Ticker4', 'Ticker5'],
                'quantity': [1, 2, 3, 4, 5],
            }
        )

        self.fut_port1 = pd.DataFrame(
            data={
                'ticker': ['Ticker1', 'Ticker2', 'Ticker3', 'Ticker4', 'Ticker5'],
                'quantity': [5, 4, 3, 2, 1],
            }
        )
        self.fut_port2 = pd.DataFrame(
            data={
                'ticker': ['Ticker2', 'Ticker3', 'Ticker4', 'Ticker5', 'Ticker6'],
                'quantity': [1, 2, 3, 4, 5],
            }
        )

        self.err_port1 = pd.DataFrame(
            data={
                'symbol': ['Ticker1', 'Ticker2', 'Ticker3', 'Ticker4', 'Ticker5'],
                'quantity': [1, 2, 3, 4, 5],
            }
        )
        self.err_port2 = pd.DataFrame(
            data={
                'symbol': ['Ticker1', 'Ticker2', 'Ticker3', 'Ticker4', 'Ticker5'],
                'number': [1, 2, 3, 4, 5],
            }
        )

    def test_portfolioOrder(self):

        # Check error catching
        with self.assertRaises(AssertionError) as _:
            self.order_builder.buildOrder(self.cur_port, self.err_port1)
            self.order_builder.buildOrder(self.err_port2, self.cur_port)
        
        # Check order creation
        self.assertSetEqual(
            self.order_builder.buildOrder(self.cur_port, self.fut_port1),
            {
                Order('Ticker1', 4, 'BUY', 'MARKET'),
                Order('Ticker2', 2, 'BUY', 'MARKET'),
                Order('Ticker4', 2, 'SELL', 'MARKET'),
                Order('Ticker5', 4, 'SELL', 'MARKET'),
            },
        )

        self.assertSetEqual(
            self.order_builder.buildOrder(self.cur_port, self.fut_port2),
            {
                Order('Ticker1', 1, 'SELL', 'MARKET'),
                Order('Ticker2', 1, 'SELL', 'MARKET'),
                Order('Ticker3', 1, 'SELL', 'MARKET'),
                Order('Ticker4', 1, 'SELL', 'MARKET'),
                Order('Ticker5', 1, 'SELL', 'MARKET'),
                Order('Ticker6', 5, 'BUY', 'MARKET'),
            },
        )