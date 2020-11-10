from backtest import PortfolioStrategy, SampleStrategy

import backtrader as bt
import pandas as pd
import unittest


class TestPortfolioStrategy(unittest.TestCase):
    def setUp(self):
        self.test_tickers = ['GOOG', 'MSFT']

        self.bt_portfolio = PortfolioStrategy(
            tickers=self.test_tickers,
            test_period=730,
            min_period=365,
            strategy=SampleStrategy
        )

    def test_datafeeds(self):
        # Get all data feed names
        data_feeds = self.bt_portfolio.cerebro.datas
        added_feeds = [x._name for x in data_feeds]
        
        # Test all feeds are added
        self.assertSetEqual(set(self.test_tickers), set(added_feeds))
        self.assertEqual(len(data_feeds), len(self.test_tickers))

        # Test feeds contain proper period
        '''How can I access the data within the data feeds?'''
    
    def test_strategy(self):
        self.bt_portfolio.run()