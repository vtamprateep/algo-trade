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

    .. attribute:: sharpe_ratio

        Holds ratio of excess returns (Portfolio Return - Risk Free Rate) to portfolio excess return standard deviation.

    .. attribute:: sortino_ratio

        Holds ratio of excess returns (Portfolio Return - Risk Free Rate) to downside return portfolio standard deviation
    '''

    def __init__(self, ticker: str, price: pd.DataFrame, mar: float = None):
        self.ticker = ticker
        self.price_history = price.sort_index()
        self.mar = mar

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
    def __init__(self):
        pass

class MetricBuilder:
    def __init__(self):
        pass

class ModernPortfolio:
    def __init__(self):
        pass

class PostModernPortfolio:
    def __init__(self):
        pass