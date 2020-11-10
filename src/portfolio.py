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

import yfinance as yf
import pandas as pd
import numpy as np
import math
import random


class InvalidMetric(Exception):
    pass

class Stock:
    '''
    A single stock with the relevant price history. Contains internal message to calculate various statistics related to the stock.
    
    ..  attribute:: ticker

        The ticker symbol of the stock as shown on relevant exchanges.

    ..  attribute:: price_history

        Holds Pandas dataframe containing daily, price data for a stock
    '''

    def __init__(self, ticker: str, price: pd.DataFrame, rf: float, mar: float = None):
        self.ticker = ticker
        self.price_history = price.sort_index()
        self.rf = rf
        self.mar = mar

        self.volatility = self.__getVolatility()
        self.sharpe = self.__getSharpe()
        # self.sortino = self.__getSortino()

    def __eq__(self, other):
        return self.ticker == other.ticker

    def __ne__(self, other):
        return self.ticker != other.ticker

    def __hash__(self):
        return id(self.ticker)

    def __getVolatility(self):
        daily_returns = self.price_history['Adj Close'].pct_change().dropna()
        return daily_returns.std()

    def __getSharpe(self):
        daily_returns = self.price_history['Adj Close'].pct_change().dropna() - self.rf / 252
        return daily_returns.mean() / self.volatility * math.sqrt(252)

    # TODO: Check __getSortino method
    def __getSortino(self):
        daily_returns = self.price_history['Adj Close'].pct_change().dropna() - self.rf / 252

        if self.mar == None:
            self.mar = daily_returns.mean()

        filtered_returns = (daily_returns[daily_returns < self.mar] - self.mar) ** 2
        downside_std = np.sqrt(filtered_returns.fillna(0).sum() / len(daily_returns))

        return daily_returns.mean() / downside_std * math.sqrt(252)

class Portfolio:
    '''
    Portfolio class, contains a collection of stock objects representing various securities and their daily, price data. Contains method to calculate portfolio level risk, return, and other metrics.
    '''

    def __init__(self):
        self.holdings = set()

    def addStock(self, stock: Stock):
        self.holdings.add(stock)

    def makePortfolio(self, method: str):
        '''
        Rank set of stocks by method indicated.

        :param str method: Method to perform selection - Sharpe or Sortino
        :param return: Pandas DataFrame
        '''

        if method.upper() == 'SORTINO':
            temp_list = list()

            for stock in self.holdings:
                temp_list.append((stock.ticker, stock.sortino))

            temp_df = pd.DataFrame(data = temp_list, columns=['ticker', 'sortino_ratio'])
            return temp_df.sort_values('sortino_ratio', ascending=False)

        elif method.upper() == 'SHARPE':
            temp_list = list()
            
            for stock in self.holdings:
                temp_list.append((stock.ticker, stock.sharpe))

            temp_df = pd.DataFrame(data = temp_list, columns=['ticker', 'sharpe_ratio'])
            return temp_df.sort_values('sharpe_ratio', ascending=False)

        else:
            raise InvalidMetric(method)

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