from unittest.mock import Mock

import unittest
import queue

from algo_trade.execution import TDAExecutionHandler
from algo_trade.event import OrderEvent


class TestTDAExecutionHandler(unittest.TestCase):
    def setUp(self):
        self.test_handler = TDAExecutionHandler(None, None, None)

        # Test asset allocations
        self.state1 = { 'IWM': 1.0 }
        self.state2 = { 'SPY': 0.75, 'IWM': 0.25, }
        self.state3 = { 'MMDA1': 1.0 }

        # Price dictionary
        self.price = {'SPY': 300, 'IWO': 200, 'IWM': 100}

    def test_build_order(self):
        order_book = self.test_handler.rebalance(10000, self.price, self.state2)
        self.assertIn(OrderEvent('SPY', 25, 'BUY', 'MARKET'), order_book)
        self.assertIn(OrderEvent('IWM', 25, 'BUY', 'MARKET'), order_book)

        order_book = self.test_handler.rebalance(10000, self.price, self.state1, self.state2)
        self.assertIn(OrderEvent('SPY', 25, 'SELL', 'MARKET'), order_book)
        self.assertIn(OrderEvent('IWM', 75, 'BUY', 'MARKET'), order_book)

        order_book = self.test_handler.rebalance(10000, self.price, self.state1, self.state3)
        self.assertIn(OrderEvent('IWM', 100, 'BUY', 'MARKET'), order_book)

        order_book = self.test_handler.rebalance(10000, self.price, self.state3, self.state1)
        self.assertIn(OrderEvent('IWM', 100, 'SELL', 'MARKET'), order_book)