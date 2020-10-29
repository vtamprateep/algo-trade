from dataclasses import dataclass

import pandas as pd


class Account:
    def __init__(self):
        pass

class OrderBuilder:
    def __init__(self):
        self.order_queue = set()

    def __portfolioCheck(self, *args):
        for df in args:
            columns = df.columns
            assert len(columns) == 2, 'Error: extra columns'
            assert set(columns) == {'ticker', 'quantity'}, 'Error: column names'

    def portfolioOrder(self, cur_state: pd.DataFrame, fut_state: pd.DataFrame):
        '''
        Dataframe structure:
        ticker: str
        quantity: int
        '''
        self.order_queue.clear()
        self.__portfolioCheck(cur_state, fut_state)

        # Left join
        left_cur_join = cur_state.merge(fut_state, how='outer', on='ticker', suffixes=('_cur', '_fut')).fillna(0)
        print(left_cur_join)
        for _, row in left_cur_join.iterrows():
            quantity = row['quantity_cur'] - row['quantity_fut']
            if quantity > 0:
                self.order_queue.add(
                    Order(
                        ticker = row['ticker'],
                        quantity = quantity,
                        action = 'SELL',
                        order_type = 'MARKET',
                    )
                )
            elif quantity < 0:
                self.order_queue.add(
                    Order(
                        ticker = row['ticker'],
                        quantity = abs(quantity),
                        action = 'BUY',
                        order_type = 'MARKET',
                    )
                )

        return self.order_queue

    # TODO: Create indicatory order builder after I make an indicator strategy
    def indicatorOrder(self):
        pass

# TODO: Consider using @property decorator for getter/setter
@dataclass(frozen=True)
class Order:
    ticker: str
    quantity: int
    action: str
    order_type: str