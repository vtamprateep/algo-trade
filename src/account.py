from dataclasses import dataclass

import pandas as pd


class Account:
    def __init__(self):
        pass

class OrderBuilder:
    def __init__(self):
        self.order_queue = set()

    def portfolioOrder(self, cur_state: pd.DataFrame, fut_state: pd.DataFrame):
        '''
        Dataframe structure:
        ticker: str
        quantity: int
        '''
        self.order_queue.clear()
        # Left join
        left_cur_join = cur_state.merge(fut_state, how='left', on='ticker', suffixes=('_cur', '_fut'))
        for _, row in left_cur_join.iterrows():
            quantity = row['quantity_cur'] - row['quantity_fut']
            if quantity > 0:
                self.order_queue.add(
                    Order(
                        ticker = row['ticker_cur'],
                        quantity = quantity,
                        action = 'SELL',
                        order_type = 'MARKET',
                    )
                )
            elif quantity < 0:
                self.order_queue.add(
                    Order(
                        ticker = row['ticker_cur'],
                        quantity = abs(quantity),
                        action = 'BUY',
                        order_type = 'MARKET',
                    )
                )
            
        return self.order_queue

    # TODO: Create indicatory order builder after I make an indicator strategy
    def indicatorOrder(self):
        pass


class Order:
    def __init__(self, ticker: str, quantity: int, action: str, order_type: str):
        self.__checkArgs(action=action.upper(), order_type=order_type.upper())

        self.ticker = ticker.upper()
        self.quantity = quantity
        self.action = action.upper()
        self.order_type = order_type.upper()

    def __checkArgs(self, **kwargs):
        assert kwargs['action'] in ('BUY', 'SELL'), 'Invalid order action.'
        assert kwargs['order_type'] in ('MARKET', 'LIMIT'), 'Invalid order type.'