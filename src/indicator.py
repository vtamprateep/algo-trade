'''
The indicator module includes classes and functions designed to operate on a time-series to produce signals or other calculations used to determine a buy/sell decision within a strategy object.

Overview
========

This module contains the following classes
    - Indicator

Usage
=====

The indicator class serves as a library of calculations, either by industry standard or user-made, to be performed on a set of time-series price information. This class should be instantiated within a strategy object and used on the time-series information which is then used to create buy/sell decisions.
'''

from datetime import datetime, timedelta

import yfinance as yf
import pandas as pd
import numpy as np
import scipy
import math


def mean(data: pd.DataFrame, pct: bool = False):
    if pct:
        data = data.pct_change().dropna()
    return data.mean()

def geometric_mean(data: pd.DataFrame, pct: bool = False):
    if pct:
        data = data.pct_change().dropna()
    return scipy.stats.gmean(data)

def volatility(data: pd.DataFrame, pct: bool = False):
    if pct:
        data = data.pct_change().dropna()
    return data.std()

def sharpe(data: pd.DataFrame, rf: float):
    daily_returns = data.pct_change().dropna() - rf / 252
    return daily_returns.mean() / daily_returns.std() * math.sqrt(252)

def sortino(data: pd.DataFrame, rf: float):
    pass

class Indicator:
    '''
    Feature requirements:
        - Needs to be able to work on DataFrames and Lists
        - Needs to be able to work on a list of lists
        - Needs to be able to work on DataFrames with multiple columns
    '''

    def calcVolatility(self, data: pd.DataFrame):
        daily_returns = data.pct_change().dropna()
        return daily_returns.std()
    
    def calcSharpe(self, data: pd.DataFrame, rf: float):
        daily_returns = data.pct_change().dropna() - rf / 252
        return daily_returns.mean() / daily_returns.std() * math.sqrt(252)

    def getSortino(self):
        pass

    