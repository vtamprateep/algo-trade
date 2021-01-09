from order import Order, OrderBuilder
from unittest.mock import Mock, call
from tda.orders import equities

import unittest
import pandas as pd
import numpy as np


class TestOrder(unittest.TestCase):
    def test_order(self):
        order1 = Order('MSFT', 5, 'BUY', 'MARKET')
        order2 = Order('MSFT', 5, 'BUY', 'MARKET')
        order3 = Order('GOOG', 5, 'BUY', 'LIMIT', 500)

        self.assertEqual(order1, order2)
        self.assertNotEqual(order1, order3)
        self.assertNotEqual(order2, order3)

        with self.assertRaises(AssertionError) as err:
            Order('MSFT', 0, 'BUY', 'MARKET')
            Order('MSFT', -5, 'SELL', 'MARKET')
            Order('GOOG', 10, 'BUY', 'LIMIT')

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
        self.rebalance1 = pd.DataFrame(data={'ticker': ['SPY', 'IWO'], 'weight': [-0.25, 0.5]})
        self.rebalance2 = pd.DataFrame(data={'ticker': ['SPY', 'IWM'], 'weight': [1, -1]})

    def test_build_order(self):
        with self.assertRaises(Exception) as cm:
            self.test_order_builder.build_order(0, self.rebalance1, self.price)
            self.test_order_builder.build_order(-100, self.rebalance1, self.price)

        order_book = self.test_order_builder.build_order(10000, self.rebalance1, self.price)
        self.assertIn(Order('SPY', 8, 'BUY', 'MARKET'), order_book)
        self.assertIn(Order('IWO', 25, 'SELL', 'MARKET'), order_book)

        self.test_order_builder.build_order(10000, self.rebalance2, self.price)
        self.assertIn(Order('SPY', 33, 'SELL', 'MARKET'), order_book)
        self.assertIn(Order('IWM', 100, 'BUY', 'MARKET'), order_book)

    def test_rebalance(self):
        with self.assertRaises(Exception) as cm:
            self.test_order_builder.rebalance(self.tar_state_er)
            self.test_order_builder.rebalance(self.tar_state1, self.cur_state_er)

        self.assertTrue(
            pd.DataFrame.equals(
                self.test_order_builder.rebalance(self.tar_state1, self.cur_state1),
                pd.DataFrame(data={'ticker':['SPY'], 'weight':[-0.75]})
            )
        )
        self.assertTrue(
            pd.DataFrame.equals(
                self.test_order_builder.rebalance(self.tar_state1),
                pd.DataFrame(data={'ticker':['SPY'], 'weight':[-0.75]})
            )
        )
        self.assertTrue(
            pd.DataFrame.equals(
                self.test_order_builder.rebalance(self.tar_state2, self.cur_state2),
                pd.DataFrame(data={'ticker':['SPY', 'IWO', 'IWM'], 'weight':[0.5, 0.5, -1]})
            )
        )
        self.assertTrue(
            pd.DataFrame.equals(
                self.test_order_builder.rebalance(self.tar_state3, self.cur_state2),
                pd.DataFrame(data={'ticker':['SPY', 'IWO', 'IWM'], 'weight':[-0.25, 0.5, -0.25]})
            )
        )