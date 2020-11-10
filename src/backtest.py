from datetime import datetime, timedelta, date

import backtrader as bt
import pandas as pd


class PortfolioStrategy:
    def __init__(self, **kwargs):
        self.data_feeds = None
        self.test_period = None

    def __setUp(self):
        # Backtest engine
        self.cerebro = bt.Cerebro()
        
    def __buildDataFeed(self, engine: bt.cerebro, tickers: list):
        date_range = self.__getPeriod()

        for symbol in tickers:    
            data_feed = bt.feeds.YahooFinanceData(
                dataname=symbol,
                name=symbol,
                fromdate=date_range['fromdate'],
                todate=date_range['todate'],
            )
            engine.adddata(data_feed)

    def __getPeriod(self, time_period: int = 365):
        todate = date.today()
        fromdate = todate - timedelta(days=time_period)
        return {
            'todate': todate,
            'fromdate': fromdate
        }

if __name__ == '__main__':
    test_object = PortfolioStrategy()