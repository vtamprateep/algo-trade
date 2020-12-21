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

import yfinance as yf
import pandas as pd
import numpy as np
import math


def mean(data: pd.DataFrame, pct: bool = False, geo: bool = False):
    if pct:
        data = data.pct_change().dropna()

    if geo:
        g_mean = stats.mstats.gmean(data)
        return pd.Series(data=g_mean, index=data.columns)
    else:
        return data.mean()

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

    return average / data.std() * math.sqrt(freq_factor[freq])

def sortino(data: pd.DataFrame, rf: float):
    pass