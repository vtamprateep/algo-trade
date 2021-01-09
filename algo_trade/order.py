from dataclasses import dataclass, field
from tda.orders import equities
from tda import auth, client
from pathlib import Path

import pandas as pd
import dotenv
import os, json


@dataclass(frozen=True)
class Order:
    '''
    ticker: Stock symbol
    quantity: Number of stocks to buy/sell
    action: BUY or SELL
    order_type: MARKET or LIMIT
    limit: Limit price
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

@dataclass
class OrderBuilder:

    order_book: Order = field(default_factory=set)

    def __create_order(self, ticker, quantity, action, order_type):
        self.order_book.add(
                    Order(
                        ticker = ticker,
                        quantity = quantity,
                        action = action,
                        order_type = order_type,
                    )
                )
        return

    def build_order(self, balance: int,  rebalance_df: pd.DataFrame, price: dict):
        assert balance > 0, Exception('Invalid balance')
        self.order_book.clear()

        for _, row in rebalance_df.iterrows():
            quantity = int(row['weight'] * balance / price[row['ticker']])

            if quantity > 0:
                self.__create_order(row['ticker'], quantity, 'SELL', 'MARKET')
            elif quantity < 0:
                self.__create_order(row['ticker'], abs(quantity), 'BUY', 'MARKET')

        return self.order_book

    def rebalance(self, tar_state: pd.DataFrame, cur_state: pd.DataFrame = pd.DataFrame(columns=['ticker', 'weight'])):
        assert 0 <= tar_state['weight'].sum() <= 1, Exception('Invalid portfolio weights')

        if cur_state.empty:
            tar_state['weight'] = tar_state['weight'] * -1
            return tar_state
        else:
            assert 0 <= cur_state['weight'].sum() <= 1, Exception('Invalid portfolio weights')

            join_df = cur_state.merge(
                tar_state,
                how='outer',
                on='ticker',
                suffixes=('_current', '_target'),
            ).fillna(0)
            join_df['weight'] = (join_df['weight_target'] - join_df['weight_current']) * -1
            
            rebalance_df = join_df[['ticker', 'weight']]
            
            # Drop cash component
            try:
                rebalance_df = rebalance_df[rebalance_df['ticker'] != 'MMDA1']
            except:
                pass
            print(tar_state, '\n', rebalance_df)
            return rebalance_df.reset_index(drop=True)