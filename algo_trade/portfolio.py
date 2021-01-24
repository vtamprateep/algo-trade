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