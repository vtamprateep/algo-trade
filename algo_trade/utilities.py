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
from scipy import stats
from math import *

import pandas as pd
import numpy as np


def volatility(data: pd.DataFrame, pct: bool = False):
    if pct:
        data = data.pct_change().dropna()
    return data.std()

def sharpe(data: pd.DataFrame, rf: float = 0, freq: str = 'year', geo = False):
    freq_factor = {
        'daily': 252,
        'week': 52,
        'month': 12,
        'year': 1,
    }

    data = data.pct_change().dropna() - rf / freq_factor[freq]

    if geo:
        temp_arr = stats.mstats.gmean(data)
        average = pd.Series(data=temp_arr, index = data.columns)
    else:
        average = data.mean()

    return average / data.std() * sqrt(freq_factor[freq])

def sortino(data: pd.DataFrame, rf: float):
    pass

def black_scholes(stock_price, strike_price, time, rf, div, volatility, option_type):
    d1 = (log(float(stock_price)/strike_price) + ((rf - div) + volatility * volatility / 2) * time) / (volatility*sqrt(time))
    d2 = d1 - volatility * sqrt(time)
    if option_type == 'call':
        return stock_price * exp(-div * time) * stats.norm.cdf(d1) - strike_price*exp(-rf * time) * stats.norm.cdf(d2)
    else:
        return strike_price * exp(-rf * time) * stats.norm.cdf(-d2) - stock_price*exp(-div * time) * stats.norm.cdf(-d1)