from order import Order
from unittest.mock import Mock, patch
from tda.orders import equities

import account
import unittest
import pandas as pd
import numpy as np


class TestAccountClient(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()
        self.mock_acc = Mock()
        
        self.order_sell_market = Order('SPY', 10, 'SELL', 'MARKET')
        self.order_sell_limit = Order('SPY', 10, 'SELL', 'LIMIT', 200)
        self.order_buy_market = Order('SPY', 10, 'BUY', 'MARKET')
        self.order_buy_limit = Order('SPY', 10, 'BUY', 'LIMIT', 200)

    def test_place_order_TDAmeritrade(self):
        self.test_account = account.AccountClient(
            self.mock_acc,
            self.mock_client,
        )

        with patch.object(self.test_account, '_AccountClient__submitBuy') as buy_method:
            self.test_account.place_order_TDAmeritrade([
                self.order_buy_limit,
                self.order_buy_market,
            ])
            assert buy_method.call_count == 2

        with patch.object(self.test_account, '_AccountClient__submitSell') as sell_method:
            self.test_account.place_order_TDAmeritrade([
                self.order_sell_limit,
                self.order_sell_market,
            ])
            assert sell_method.call_count == 2