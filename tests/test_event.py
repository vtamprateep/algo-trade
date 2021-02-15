from tda.orders import equities

import unittest
import pandas as pd
import numpy as np

from event import OrderEvent, OrderBuilder


class TestOrderEvent(unittest.TestCase):
    def setUp(self):
        self.order1 = OrderEvent('MSFT', 5, 'BUY', 'MARKET')
        self.order2 = OrderEvent('MSFT', 5, 'BUY', 'MARKET')
        self.order3 = OrderEvent('GOOG', 5, 'BUY', 'LIMIT', 500)

    def test_order(self):
        self.assertEqual(self.order1, self.order2)
        self.assertNotEqual(self.order1, self.order3)
        self.assertNotEqual(self.order2, self.order3)

class TestOrderBuilder(unittest.TestCase):
    def setUp(self):
        self.test_order_builder = OrderBuilder()

        # Valid
        self.tar_state1 = pd.DataFrame(
            data={'ticker': ['SPY'],'weight': [0.75],}
        )
        self.tar_state2 = pd.DataFrame(
            data={'ticker': ['IWM'],'weight': [1],}
        )
        self.tar_state3 = pd.DataFrame(
            data={'ticker': ['SPY', 'IWM'],'weight': [0.75, 0.25],}
        )
        self.cur_state1 = pd.DataFrame(
            data={'ticker': ['MMDA1'],'weight': [1],}
        )
        self.cur_state2 = pd.DataFrame(
            data={'ticker': ['SPY', 'IWO'],'weight': [0.5, 0.5],}
        )

        # Invalid
        self.tar_state_er = pd.DataFrame(
            data={'ticker': ['SPY', 'IWM'],'weight': [0, -0.1],}
        )
        self.cur_state_er = pd.DataFrame(
            data={'ticker': ['SPY', 'IWM'],'weight': [0.9, 0.9],}
        )

        # Price dictionary
        self.price = {'SPY': 300, 'IWO': 200, 'IWM': 100}

    def test_build_order(self):
        order_book = self.test_order_builder.build_order(10000, self.price, self.tar_state3)
        self.assertIn(OrderEvent('SPY', 25, 'BUY', 'MARKET'), order_book)
        self.assertIn(OrderEvent('IWM', 25, 'BUY', 'MARKET'), order_book)

        self.test_order_builder.build_order(10000, self.price, self.tar_state2, self.tar_state3)
        self.assertIn(OrderEvent('SPY', 25, 'SELL', 'MARKET'), order_book)
        self.assertIn(OrderEvent('IWM', 75, 'BUY', 'MARKET'), order_book)