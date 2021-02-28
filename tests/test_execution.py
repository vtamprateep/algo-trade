from unittest.mock import Mock
from queue import Queue

import unittest
import datetime

from algo_trade.execution import TDAExecutionHandler, SimulatedExecutionHandler
from algo_trade.event import FillEvent, OrderEvent


class TestSimulatedExecutionHandler(unittest.TestCase):
    def setUp(self):
        self.test_queue = Queue()
        self.test_handler = SimulatedExecutionHandler(self.test_queue)
        self.test_order = OrderEvent('SPY', 10, 'BUY', 'MARKET')
        self.test_fill = FillEvent(
            timeindex=datetime.datetime.utcnow(),
            ticker='SPY',
            exchange='ARCA',
            quantity=10,
            direction='BUY',
            fill_cost=None,
        )

    def test_execute_order(self):
        self.test_handler.execute_order(self.test_order)
        output_fill = self.test_queue.get()

        self.assertEqual(output_fill.ticker, self.test_fill.ticker)
        self.assertEqual(output_fill.exchange, self.test_fill.exchange)
        self.assertEqual(output_fill.quantity, self.test_fill.quantity)
        self.assertEqual(output_fill.direction, self.test_fill.direction)
        self.assertEqual(output_fill.fill_cost, self.test_fill.fill_cost)

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