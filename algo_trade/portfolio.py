'''
The portfolio module includes modules needed import data and perform analysis to select a basket of stocks using Markowitz's efficient frontier portfolio theory.

This module contains the following classes:
    - Portfolio

Portfolio
---------

..  autoclass:: Portfolio
    :members:

'''

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
from tda import client

import json
import math
import numpy as np
import pandas as pd
import yfinance as yf


@dataclass
class Portfolio:
    '''
    Portfolio class, contains a collection of stock objects representing various securities and their price data at different resolutions.
    '''

    population: Iterable = None
    holdings: Iterable = field(default=dict)
    rf: float = yf.Ticker("SHY").info['yield']

    def strategy(self):
        # Base class, override strategy when defining trading algorithms, should return dataframe with holdings and weight of each
        pass

    # Run strategy and create optimal holdings to pass to orderbuilder
    def run(self, test: bool = False):
        return self.strategy()

def get_data_YahooFinance(stocks: list, period: str = '1y', interval: str = '1d'):
    result_dict = dict()

    data = yf.download(
        tickers = ' '.join(stocks),
        period = period,
        interval = interval,
        group_by = 'ticker',
    )
    data.dropna(inplace=True)

    if len(stocks) == 1:
        result_dict[stocks[0]] = data.drop(['Adj Close', 'Volume'], axis=1)
    else:
        for ticker in stocks:
            result_dict[ticker] = data[ticker].drop(['Adj Close', 'Volume'], axis=1)

    return result_dict

# In Development
def get_data_TDAmeritrade(client, stocks: list, period: str = '1y', interval: str = '1d'):
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
    result_dict = dict()

    for ticker in stocks:
        response = client.get_price_history(
            ticker,
            period_type='year',
            period=1,
            frequency_type='daily',
            frequeny=1,
        ).json()

        price_history = pd.DataFrame(
            data=response['candles'],
            columns=['Date', 'Open', 'High', 'Low', 'Close'],
        )
        price_history['Date'] = price_history['Date'].dt.date

        result_dict[ticker] = price_history.set_index('Date')

    return result_dict

def rebalance(tar: pd.DataFrame, cur: pd.DataFrame = None):
    assert 0 <= tar['weight'].sum() <= 1, Exception('Invalid portfolio weights')

    if cur is None:
        tar['weight'] = tar['weight'] * -1
        return tar
    else:
        assert 0 <= cur['weight'].sum() <= 1, Exception('Invalid portfolio weights')

        join_df = cur.merge(
            tar,
            how='outer',
            on='ticker',
            suffixes=('_cur', '_tar'),
        ).fillna(0)

        join_df['weight'] = (join_df['weight_tar'] - join_df['weight_cur']) * -1
        rebalance_df = join_df[['ticker', 'weight']]

        try:
            rebalance_df = rebalance_df[rebalance_df['ticker'] != 'MMDA1']
        except:
            pass

        print(rebalance_df.sort_values(by=['ticker']).reset_index(drop=True))
        return rebalance_df.sort_values(by=['ticker']).reset_index(drop=True)