'''
The stock_selection module includes modules needed import data and perform analysis to select a basket of stocks using Markowitz's efficient frontier portfolio theory.

Overview
========

This module contains the following classes:
    - Example1
    - Example2

Usage
=====

'''

import yfinance
import pandas as pd
import numpy as np


class Stock:
    '''
    A single stock with the relevant price history. Contains internal message to calculate various statistics related to the stock.
    
    ..  attribute:: ticker

        The ticker symbol of the stock as shown on relevant exchanges.

    .. attribute:: price_history

        Holds Pandas dataframe containing daily, price data for a stock
        
    '''

    def __init__(self, ticker: str, price: pd.DataFrame, mar: float = None):
        self.ticker = ticker
        self.price_history = price.sort_index()
        self.mar = mar

    def getVolatility(self):
        daily_returns = self.price_history['Adj Close'].pct_change().dropna()
        return daily_returns.std()

    def getSharpe(self):
        daily_returns = self.price_history['Adj Close'].pct_change().dropna()
        std = daily_returns.std()
        total_return = (self.price_history['Adj Close'].iloc[-1] - self.price_history['Adj Close'].iloc[0]) / self.price_history['Adj Close'].iloc[0]
        
        return total_return / std

    def getSortino(self):
        daily_returns = self.price_history['Adj Close'].pct_change().dropna()

        if not self.mar:
            self.mar = daily_returns.mean()

        filtered_returns = daily_returns[daily_returns < self.mar].dropna()
        square_difference = np.square(filtered_returns - self.mar)
        downside_std = np.sqrt(square_difference.sum() / len(square_difference))

        total_return = (self.price_history['Adj Close'].iloc[-1] - self.price_history['Adj Close'].iloc[0]) / self.price_history['Adj Close'].iloc[0]

        return total_return / downside_std

class DataBuilder:
    '''
    Builder class. Takes population of stock tickers and the Portfolio object, creates individual Stock objects directly within the portfolio class. Connects with yfinance API to pull pricing data.
    '''

    def __init__(self):
        self.spy_top_holdings = {'MSFT', 'AAPL', 'AMZN', 'FB', 'GOOG', 'JNJ', 'BRK.B', 'V', 'PG'}
        self.spy_holdings = set()

    def getStocks(self):
        pass

class Portfolio:
    '''
    Portfolio class, contains a collection of stock objects representing various securities and their daily, price data. Contains method to calculate portfolio level risk, return, and other metrics.

    ..  attribute:: 
    '''

    def __init__(self):
        self.holdings = set()

    def pickStocks(self):
        pass