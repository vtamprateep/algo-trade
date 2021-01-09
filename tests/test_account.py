from account import AccountClient, Order
from unittest.mock import Mock, call
from tda.orders import equities

import unittest
import pandas as pd
import numpy as np


class TestAccountClient(unittest.TestCase):
    def setUp(self):
        self.test_account = AccountClient(
            Mock(),
            Mock(),
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

        # Error portfolio
        self.tar_state_er = pd.DataFrame(
            data={
                'ticker': ['SPY', 'IWM'],
                'weight': [0.75, 0.25],
            }
        )
        self.cur_state_er = pd.DataFrame(
            data={
                'ticker': ['SPY', 'IWM'],
                'weight': [0.9, 0.9],
            }
        )

        # Valid portfolio
        self.tar_state1 = pd.DataFrame(
            data={
                'ticker': ['SPY'],
                'weight': [0.75],
            }
        )
        self.tar_state2 = pd.DataFrame(
            data={
                'ticker': ['IWM'],
                'weight': [1],
            }
        )
        self.tar_state3 = pd.DataFrame(
            data={
                'ticker': ['SPY', 'IWM'],
                'weight': [0.5, 0.5],
            }
        )
        self.cur_state1 = pd.DataFrame(
            data={
                'ticker': ['MMDA1'],
                'weight': [1],
            }
        )
        self.cur_state2 = pd.DataFrame(
            data={
                'ticker': ['SPY', 'IWO'],
                'weight': [0.5, 0.5],
            }
        )
        
        self.test_price = {
            'SPY': 300,
            'IWM': 100,
            'IWO': 200,
        }

    def test_buildOrder(self):
        with self.assertRaises(Exception) as em:
            self.test_account.buildOrder(
                self.tar_state_er,
                self.cur_state1,
            )
            self.test_account.buildOrder(
                self.tar_state1,
                self.cur_state_er,
            )
            self.test_account.buildOrder(
                self.tar_state_er,
                self.cur_state_er,
            )
            self.test_account.buildOrder(self.tar_state1, self.cur_state1,self.test_price, 0)

        # Current State 1
        self.test_account.buildOrder(self.tar_state1, self.cur_state1,self.test_price, 10000)
        self.assertIn(Order('SPY', 25, 'BUY', 'MARKET'), self.test_account.order_book)

        self.test_account.buildOrder(self.tar_state2, self.cur_state1,self.test_price, 10000)
        self.assertIn(Order('IWM', 100, 'BUY', 'MARKET'), self.test_account.order_book)

        self.test_account.buildOrder(self.tar_state2, self.cur_state1,self.test_price, 10000)
        self.assertIn(Order('SPY', 16, 'BUY', 'MARKET'), self.test_account.order_book)
        self.assertIn(Order('IWM', 50, 'BUY', 'MARKET'), self.test_account.order_book)

        # Current State 2
        self.test_account.buildOrder(self.tar_state1, self.cur_state2,self.test_price, 10000)
        self.assertIn(Order('SPY', 8, 'BUY', 'MARKET'), self.test_account.order_book)
        self.assertIn(Order('IWO', 25, 'SELL', 'MARKET'), self.test_account.order_book)

        self.test_account.buildOrder(self.tar_state2, self.cur_state2,self.test_price, 10000)
        self.assertIn(Order('SPY', 16, 'SELL', 'MARKET'), self.test_account.order_book)
        self.assertIn(Order('IWO', 25, 'SELL', 'MARKET'), self.test_account.order_book)
        self.assertIn(Order('IWM', 50, 'BUY', 'MARKET'), self.test_account.order_book)

        self.test_account.buildOrder(self.tar_state2, self.cur_state2,self.test_price, 10000)
        self.assertIn(Order('IWO', 25, 'SELL', 'MARKET'), self.test_account.order_book)
        self.assertIn(Order('IWM', 50, 'BUY', 'MARKET'), self.test_account.order_book)
        
    
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