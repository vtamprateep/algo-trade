from unittest.mock import Mock
from queue import Queue
from datetime import datetime

import unittest
import pandas as pd
import numpy as np

from algo_trade.broker import TDABroker, SimulatedBroker
from algo_trade.event import FillEvent, OrderEvent


class TestSimulatedBroker(unittest.TestCase):
    def setUp(self):
        # Create test objects
        self.test_queue = Queue()
        self.test_order = OrderEvent('SPY', 10, 'BUY', 'MARKET')
        self.test_fill = FillEvent(
            timeindex=datetime.utcnow(),
            ticker='SPY',
            exchange='ARCA',
            quantity=10,
            direction='BUY',
            fill_cost=283.25314,
        )

        # Create test data
        test_data = pd.DataFrame(
            {
                'datetime':['1/3/94', '1/4/94', '1/5/94', '1/6/94', '1/7/94', '1/10/94', '1/11/94', '1/12/94'],
                'adj_close': [28.154894, 28.268501, 28.325314, 28.325314, 28.495695, 28.836512, 28.779718, 28.685057],
            }
        )
        test_data['datetime'] = pd.to_datetime(test_data['datetime'], infer_datetime_format=True)
        test_data.set_index('datetime', inplace=True)

        # Instantiate test broker
        self.test_broker = SimulatedBroker(self.test_queue, ['SPY'])
        self.test_broker.ticker_data['SPY'] = test_data
        self.test_broker.ticker_generator['SPY'] = test_data.iterrows()
        self.test_broker.latest_ticker_data['SPY'] = list()

        # Update four bars into visible data
        for _ in range(4):
            self.test_broker.update_bars()

    def test_update_bars(self):
        self.assertEqual(len(self.test_broker.latest_ticker_data['SPY']), 4)
        print(self.test_broker.latest_ticker_data)

    def test_get_latest_bar(self):
        latest_bar = self.test_broker.get_latest_bar('SPY')
        print(latest_bar)
        self.assertEqual(latest_bar[0].to_pydatetime(), datetime(1994,1,6))

    def test_get_latest_bars(self):
        latest_bar1 = self.test_broker.get_latest_bars('SPY')
        latest_bar3 = self.test_broker.get_latest_bars('SPY', 3)
        latest_bar6 = self.test_broker.get_latest_bars('SPY', 6)

        self.assertEqual(len(latest_bar1), 1)
        self.assertEqual(latest_bar1[0][0].to_pydatetime(), datetime(1994,1,6))

        self.assertEqual(len(latest_bar3), 3)
        self.assertEqual(latest_bar3[0][0].to_pydatetime(), datetime(1994, 1, 4))
        
        self.assertEqual(len(latest_bar6), 4)

    def test_get_latest_bar_datetime(self):
        self.assertEqual(self.test_broker.get_latest_bar_datetime('SPY'), datetime(1994,1,6))

    def test_get_latest_bar_value(self):
        self.assertEqual(self.test_broker.get_latest_bar_value('SPY', 'adj_close'), 28.325314)

    def test_get_latest_bars_values(self):
        self.assertTrue(
            np.array_equal(
                self.test_broker.get_latest_bars_values('SPY', 'adj_close', 2), 
                [28.325314, 28.325314],
            )
        )
        self.assertTrue(
            np.array_equal(
                self.test_broker.get_latest_bars_values('SPY', 'adj_close', 5), 
                [28.154894, 28.268501, 28.325314, 28.325314],
            )
        )

    def test_execute_order(self):
        # Empty queue to test MarketEvent placement into queue
        while not self.test_queue.empty():
            self.test_queue.get()

        self.test_broker.execute_order(self.test_order)
        output_fill = self.test_queue.get()

        self.assertEqual(output_fill.ticker, self.test_fill.ticker)
        self.assertEqual(output_fill.exchange, self.test_fill.exchange)
        self.assertEqual(output_fill.quantity, self.test_fill.quantity)
        self.assertEqual(output_fill.direction, self.test_fill.direction)
        self.assertEqual(output_fill.fill_cost, self.test_fill.fill_cost)

class TestTDABroker(unittest.TestCase):
    def setUp(self):
        self.test_queue = Queue()
        self.test_handler = TDABroker(None, None, self.test_queue, None)

        # Test asset allocations
        self.state1 = { 'IWM': 1.0 }
        self.state2 = { 'SPY': 0.75, 'IWM': 0.25, }
        self.state3 = { 'MMDA1': 1.0 }

        # Price dictionary
        self.price = {'SPY': 300, 'IWO': 200, 'IWM': 100}

    def test_rebalance(self):
        self.test_handler.rebalance(10000, self.price, self.state2)
        self.assertEqual(OrderEvent('SPY', 25, 'BUY', 'MARKET'), self.test_queue.get())
        self.assertEqual(OrderEvent('IWM', 25, 'BUY', 'MARKET'), self.test_queue.get())

        self.test_handler.rebalance(10000, self.price, self.state1, self.state2)
        self.assertEqual(OrderEvent('SPY', 25, 'SELL', 'MARKET'), self.test_queue.get())
        self.assertEqual(OrderEvent('IWM', 75, 'BUY', 'MARKET'), self.test_queue.get())

        self.test_handler.rebalance(10000, self.price, self.state1, self.state3)
        self.assertEqual(OrderEvent('IWM', 100, 'BUY', 'MARKET'), self.test_queue.get())

        self.test_handler.rebalance(10000, self.price, self.state3, self.state1)
        self.assertEqual(OrderEvent('IWM', 100, 'SELL', 'MARKET'), self.test_queue.get())