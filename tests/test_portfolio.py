from datetime import datetime, date
from unittest.mock import Mock
from queue import Queue

import numpy as np
import pandas as pd
import unittest

from algo_trade.portfolio import Portfolio
from algo_trade.event import FillEvent, OrderEvent, SignalEvent


class TestModuleFunction(unittest.TestCase):
    def setUp(self):
        test_bar = Mock(ticker_list=['SPY'])
        test_bar.get_latest_bar_value = Mock(return_value=200)
        test_bar.get_latest_bar_datetime = Mock(return_value=datetime(2000,1,2))
        test_queue = Queue()

        self.test_portfolio = Portfolio(
            bars=test_bar,
            events=test_queue,
            start_date=datetime(2000,1,1)
        )

        self.all_positions = self.test_portfolio.all_positions
        self.current_positions = self.test_portfolio.current_positions
        self.all_holdings = self.test_portfolio.all_holdings
        self.current_holdings = self.test_portfolio.current_holdings

    def test_initialization(self):
        expected_all_positions = { 'datetime': datetime(2000,1,1), 'SPY': 0 }
        expected_current_positions = { 'SPY': 0 }
        expected_all_holdings = { 'datetime': datetime(2000,1,1), 'cash': 100000.0, 'commission': 0.0, 'total': 100000.0, 'SPY': 0 }
        expected_current_holdings = { 'cash': 100000.0, 'commission': 0.0, 'total': 100000.0, 'SPY': 0 }

        self.assertDictEqual(self.all_positions[-1], expected_all_positions)
        self.assertDictEqual(self.current_positions, expected_current_positions)
        self.assertDictEqual(self.all_holdings[-1], expected_all_holdings)
        self.assertDictEqual(self.current_holdings, expected_current_holdings)

    def test_update_timeindex(self):
        self.test_portfolio.update_timeindex(None)
        expected_entry_positions = { 'datetime': datetime(2000,1,2), 'SPY': 0 }
        expected_entry_holdings = { 'datetime': datetime(2000,1,2), 'cash': 100000.0, 'commission': 0.0, 'total': 100000.0, 'SPY': 0.0 }

        self.assertDictEqual(self.all_positions[-1], expected_entry_positions)
        self.assertDictEqual(self.all_holdings[-1], expected_entry_holdings)

    def test_update_fill(self):
        test_fill = FillEvent(datetime.utcnow(), 'SPY', 'ARCA', 10, 'BUY', None)
        self.test_portfolio.update_fill(test_fill)

        self.assertEqual(self.test_portfolio.current_positions['SPY'], 10)
        self.assertEqual(self.test_portfolio.current_holdings['SPY'], 2000)
        self.assertEqual(self.test_portfolio.current_holdings['SPY'], 2000)
        self.assertEqual(self.test_portfolio.current_holdings['cash'], 98000.0)
        self.assertEqual(self.test_portfolio.current_holdings['total'], 100000.0)

    def test_update_signal(self):
        

        test_signal_long = SignalEvent(0, 'SPY', datetime.utcnow(), 'LONG', 1)
        test_signal_short = SignalEvent(0, 'SPY', datetime.utcnow(), 'SHORT', 1)
        test_signal_exit = SignalEvent(0, 'SPY', datetime.utcnow(), 'EXIT', 1)

        self.test_portfolio.update_signal(test_signal_long)
        output_order_long = self.test_portfolio.events.get()
        expected_order_long = OrderEvent('SPY', 100, 'BUY', 'MARKET')
        
        self.test_portfolio.update_signal(test_signal_short)
        output_order_short = self.test_portfolio.events.get()
        expected_order_short = OrderEvent('SPY', 100, 'SELL', 'MARKET')

        # Create non-zero SPY holding to test EXIT signal
        test_fill = FillEvent(datetime.utcnow(), 'SPY', 'ARCA', 10, 'BUY', None)
        self.test_portfolio.update_fill(test_fill)
        
        self.test_portfolio.update_signal(test_signal_exit)
        output_order_exit = self.test_portfolio.events.get()
        expected_order_exit = OrderEvent('SPY', 10, 'SELL', 'MARKET')

        self.assertEqual(output_order_long, expected_order_long)
        self.assertEqual(output_order_short, expected_order_short)
        self.assertEqual(output_order_exit, expected_order_exit)