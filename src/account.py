from dataclasses import dataclass

import pandas as pd


class AccountClient:
    def __init__(self, client):
        self.client = client

    def placeOrderTDAmeritrade(self, client, order_book):
        order_queue = list()
        for order in order_book:
            pass

class OrderBuilder:
    def __init__(self):
        self.order_book = set()

    def __portfolioCheck(self, *args):
        for df in args:
            columns = df.columns
            assert len(columns) == 2, 'Error: extra columns'
            assert set(columns) == {'ticker', 'quantity'}, 'Error: column names'

    def buildOrder(self, cur_state: pd.DataFrame, fut_state: pd.DataFrame):
        '''
        Dataframe structure:
        ticker: str
        quantity: int
        '''
        self.order_book.clear()
        self.__portfolioCheck(cur_state, fut_state)

        left_cur_join = cur_state.merge(fut_state, how='outer', on='ticker', suffixes=('_cur', '_fut')).fillna(0)
        print(left_cur_join)
        for _, row in left_cur_join.iterrows():
            quantity = row['quantity_cur'] - row['quantity_fut']
            if quantity > 0:
                self.order_book.add(
                    Order(
                        ticker = row['ticker'],
                        quantity = quantity,
                        action = 'SELL',
                        order_type = 'MARKET',
                    )
                )
            elif quantity < 0:
                self.order_book.add(
                    Order(
                        ticker = row['ticker'],
                        quantity = abs(quantity),
                        action = 'BUY',
                        order_type = 'MARKET',
                    )
                )

        return self.order_book

@dataclass(frozen=True)
class Order:
    '''
    ticker: Stock symbol
    quantity: Number of stocks to buy/sell
    action: BUY or SELL
    order_type: MARKET or LIMIT
    '''
    ticker: str
    quantity: int
    action: str
    order_type: str
    limit: float = None

    def __post_init__(self):
        assert self.quantity > 0, 'Cannot buy/sell less than one security'
        if self.order_type.upper() == 'LIMIT':
            assert self.limit and self.limit > 0, 'Missing limit on limit order'