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

import pandas as pd


@dataclass
class Portfolio:
    '''
    Portfolio class, contains a collection of stock objects representing various securities and their price data at different resolutions.
    '''

    data: object = None
    params: dict = field(default=dict)
    population: Iterable = None

    def __post_init__(self):
        assert self.population != None and len(self.population) != 0, 'Must have at least one symbol'
        assert {'period_type', 'period', 'frequency_type', 'frequency'}.issubset(set(self.params.keys())), 'Missing one or more strategy parameter: period_type, period, frequency_type, frequency'

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