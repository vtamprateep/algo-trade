import unittest
import pandas as pd

from algo_trade.event import OrderEvent


class TestOrderEvent(unittest.TestCase):
    def setUp(self):
        self.order1 = OrderEvent('MSFT', 5, 'BUY', 'MARKET')
        self.order2 = OrderEvent('MSFT', 5, 'BUY', 'MARKET')
        self.order3 = OrderEvent('GOOG', 5, 'BUY', 'LIMIT', 500)

    def test_order(self):
        self.assertEqual(self.order1, self.order2)
        self.assertNotEqual(self.order1, self.order3)
        self.assertNotEqual(self.order2, self.order3)