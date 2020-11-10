'''
The strategy module includes various portfolio strategies instantiated into classes.

This module contains the following classes:
    - Fortune50Strategy

Fortune50Strategy
-----------------

..  autoclass:: Fortune50Strategy
    :members:

'''

#import portfolio
import pandas as pd


class Fortune50Strategy:
    '''
    Applies modern portfolio theory on population of Fortune 50 stocks, selecting top 20 with highest Sharpe ratio and allocating accordingly.
    '''

    def __init__(self):
        self.population = ['AAPL','MSFT','AMZN','FB','GOOGL','GOOG','BRK-B','JNJ','PG','NVDA','V','HD','UNH','JPM','MA','ADBE','PYPL','VZ','CRM','NFLX','INTC','DIS','PFE','CMCSA','WMT','MRK','KO','PEP','ABT','T','BAC','TMO','MCD','COST','CSCO','NKE','AVGO','ABBV','NEE','MDT','ACN','QCOM','DHR','XOM','UNP','TXN','CVX','BMY','AMGN','LOW']
        self.portfolio = portfolio.Portfolio()
        self.builder = portfolio.DataBuilder()

        self.builder.buildStocks(self.portfolio, self.population)

    def makeHoldings(self):
        self.allocation = pd.DataFrame(columns=['ticker','sharpe'])

        for stock in self.portfolio.holdings:
            self.allocation = self.allocation.append({
                    'ticker': stock.ticker,
                    'sharpe': stock.sharpe,
                },
                ignore_index=True,
            )

        self.top_20 = self.allocation.sort_values('sharpe', ascending=False).head(20)
        self.top_20['percent'] = self.top_20['sharpe'] / self.top_20['sharpe'].sum()
        self.top_20.drop(['sharpe'], axis=1, inplace=True)
        
        return self.top_20


if __name__ == '__main__':
    strategy = Fortune50Strategy()
    print(strategy.makeHoldings())