'''
The portfolio module includes modules needed import data and perform analysis to select a basket of stocks using Markowitz's efficient frontier portfolio theory.

This module contains the following classes:
    - Stock
    - Portfolio
    - DataBuilder

Stock
-----

..  autoclass:: Stock
    :members:

Portfolio
---------

..  autoclass:: Portfolio
    :members:

DataBuilder
-----------

..  autoclass:: DataBuilder
    :members:

'''

from datetime import datetime, timedelta
from dataclasses import dataclass

import yfinance as yf
import pandas as pd
import numpy as np
import math
import random


class InvalidMetric(Exception):
    pass

@dataclass
class Stock:
    '''
    A single stock with the relevant price history. Contains internal message to calculate various statistics related to the stock.
    
    ..  attribute:: ticker

        The ticker symbol of the stock as shown on relevant exchanges.

    ..  attribute:: price_history

        Holds Pandas dataframe containing daily, price data for a stock
    '''

    ticker: str
    price_history: pd.DataFrame

    def __eq__(self, other):
        return self.ticker == other.ticker

    def __ne__(self, other):
        return self.ticker != other.ticker

    def __hash__(self):
        return id(self.ticker)

class Portfolio:
    '''
    Portfolio class, contains a collection of stock objects representing various securities and their daily, price data. Contains method to calculate portfolio level risk, return, and other metrics.
    '''

    def __init__(self):
        self.holdings = set()

    def addStock(self, stock: Stock):
        self.holdings.add(stock)

    def addStrategy(self, strategy):
        self.strategy = strategy

    # Run strategy and create optimal holdings to pass to orderbuilder
    def runStrategy(self):
        pass

class DataBuilder:
    '''
    Builder class. Takes population of stock tickers and the Portfolio object, creates individual Stock objects directly within the portfolio class. Connects with yfinance API to pull pricing data.

    ..  attribute:: ticker_list

        List of tickers we want to collect into our portfolio for analysis
    '''

    def __init__(self):
        self.rng = random.Random()
        self.rf = yf.Ticker("SHY").info['yield']

    def buildFake(self, volatility: float, average: float, size: int, start: datetime = datetime(2000,1,1)):
        self.volatility = volatility
        self.average = average
        self.size = size
        self.start = start

        date_array = np.arange(start=self.start,stop=self.start + timedelta(days=self.size), step=timedelta(days=1))
        price_array = [self.average]

        for _ in range(self.size - 1):
            rand_num = self.rng.random()
            change_factor = 2 * rand_num * self.volatility

            if change_factor > self.volatility:
                change_factor -= 2 * self.volatility

            price_array.append(price_array[-1] + price_array[-1] * change_factor)

        return pd.DataFrame(
            data = {
                'Adj Close': price_array
            }, 
            index = date_array,
        )

    def buildStocks(self, portfolio, stocks: list, period: str = '1y', interval: str = '1d'):
        data = yf.download(
            tickers = ' '.join(stocks),
            period = period,
            interval = interval,
            group_by = 'ticker',
        )
        
        for ticker in stocks:
            stock = Stock(
                ticker = ticker,
                price = data[ticker],
                rf = self.rf
            )
            portfolio.addStock(stock)