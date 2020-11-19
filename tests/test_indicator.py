from indicator import Indicator
from portfolio import DataBuilder

import unittest


class TestIndicator(unittest.TestCase):
    def setUp(self):
        self.indicator = Indicator()
        self.builder = DataBuilder()
        self.builder.rng.seed(1)
        self.dataset = self.builder.buildFake(0.1, 20, 60)

    def test_get_volatility(self):
        self.assertEqual(round(self.indicator.calcVolatility(self.dataset)['Adj Close'], 5), 0.05696)

    def test_get_sharpe(self):
        self.assertEqual(round(self.indicator.calcSharpe(self.dataset, 0.017)['Adj Close'], 5), 1.47985)