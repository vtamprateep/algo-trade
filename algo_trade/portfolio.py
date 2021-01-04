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

from datetime import datetime, timedelta, date
from dataclasses import dataclass, field
from collections.abc import Callable, Iterable
from tda import client

import yfinance as yf
import pandas as pd
import numpy as np
import math
import random
import json


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

@dataclass
class DataBuilder:
    '''
    Builder class. Takes population of stock tickers and the Portfolio object, creates individual Stock objects directly within the portfolio class. Connects with yfinance API to pull pricing data.

    ..  attribute:: ticker_list

        List of tickers we want to collect into our portfolio for analysis
    '''

    # Use 1 year Treasury yield rate
    rf: float = yf.Ticker("SHY").info['yield']
    client = None

    def YahooFinance(self, portfolio, stocks: list, period: str = '1y', interval: str = '1d'):
        data = yf.download(
            tickers = ' '.join(stocks),
            period = period,
            interval = interval,
            group_by = 'ticker',
        )
        
        for ticker in stocks:
            stock = Stock(
                ticker = ticker,
                price_history = data[ticker],
            )
            portfolio.addStock(stock)

    def TDAmeritrade(self, portfolio, stocks: list, period: str = '1y', interval: str = '1d'):
        '''
        Output from TDA historicals in following format
        {
            'candles': List[{
                'open': float,
                'high': float,
                'low': float,
                'close': float,
                'volume': int (units of millions),
                'datetime': (units of miliseconds)
            }],
            'symbol': str,
            'empty': bool,
        }
        '''
        self.client.set_enforce_enums(enforce_enums=False)

        for ticker in stocks:
            response = self.client.get_price_history(
                ticker,
                period_type='year',
                period=1,
                frequency_type='daily',
                frequeny=1,
            ).json()

            price_history = pd.DataFrame(
                data=response['candles'],
                columns=['datetime', 'open', 'high', 'low', 'close'],
            )
            price_history['datetime'] = pd.to_datetime(price_history['datetime'], unit='ms')

            stock = Stock(
                ticker = ticker,
                price = price_history,
                rf = self.rf,
            )
            portfolio.addStock(stock)

        self.client.set_enforce_enums(enforce_enums=True)

@dataclass
class Portfolio:
    '''
    Portfolio class, contains a collection of stock objects representing various securities and their price data at different resolutions.
    '''

    population: Iterable = None
    holdings: Iterable = field(default_factory=set)
    start: date = None
    rf: float = None

    def add_stock(self, stock: Stock):
        self.holdings.add(stock)

    def strategy(self):
        # Base class, override strategy when defining trading algorithms, should return dataframe with holdings and weight of each
        pass

    # Run strategy and create optimal holdings to pass to orderbuilder
    def run(self, test: bool = False):
        return self.strategy()