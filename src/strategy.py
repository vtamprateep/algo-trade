'''
The strategy module includes various portfolio strategies instantiated into classes.

This module contains the following classes:
    - SpyIwoStrategy
    - Fortune50Strategy

Fortune50Strategy
-----------------

..  autoclass:: Fortune50Strategy
    :members:

'''

from dataclasses import dataclass
from collections.abc import Callable, Iterable

import portfolio
import pandas as pd
import yfinance as yf

@dataclass
class BaseStrategy:
    population: Iterable
    rf: float = None
    resolution: str = None
    min_period: int = None
    indicator: dict = dict()

    def addIndicator(self, indicator: Callable):
        if indicator.__name__ not in self.indicator:
            self.indicator[indicator.__name__] = indicator

class SpyIwoStrategy(BaseStrategy):
    '''
    Sweeps remaining portfolio cash balance into 75% SPY and 25% IWO
    '''

    def __init__(self):
        self.population = ['SPY', 'IWO']

    def compute(self, cash: float):
        return pd.DataFrame(
            data={
                'ticker':['SPY', 'IWO'],
                'holding':[0.75, 0.25],
            }
        )

class Fortune50Strategy(BaseStrategy):
    '''
    Applies modern portfolio theory on population of Fortune 50 stocks, selecting top 20 with highest Sharpe ratio and allocating accordingly.
    '''

    def __init__(self):
        self.population = ['AAPL','MSFT','AMZN','FB','GOOGL','GOOG','BRK-B','JNJ','PG','NVDA','V','HD','UNH','JPM','MA','ADBE','PYPL','VZ','CRM','NFLX','INTC','DIS','PFE','CMCSA','WMT','MRK','KO','PEP','ABT','T','BAC','TMO','MCD','COST','CSCO','NKE','AVGO','ABBV','NEE','MDT','ACN','QCOM','DHR','XOM','UNP','TXN','CVX','BMY','AMGN','LOW']
        self.rf = yf.Ticker("SHY").info['yield']
        self.resolution = 'year'
        self.min_period = 1

    # Finish strategy logic
    def compute(self, data: pd.DataFrame):
        sharpe_array = self.indicator(data, self.rf)

if __name__ == '__main__':
    pass