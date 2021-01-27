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

    def __rebalance(self, tar_state, cur_state):
        assert 0 <= tar_state['weight'].sum() <= 1, Exception('Invalid portfolio weights')
        assert 0 <= cur_state['weight'].sum() <= 1, Exception('Invalid portfolio weights')

        join_df = cur_state.merge(
            tar_state,
            how='outer',
            on='ticker',
            suffixes=('_current', '_target'),
        ).fillna(0)

        join_df['weight'] = (join_df['weight_target'] - join_df['weight_current'])
        rebalance_df = join_df[['ticker', 'weight']]
        
        # Drop cash component
        try:
            rebalance_df = rebalance_df[rebalance_df['ticker'] != 'MMDA1']
        except:
            pass

        return rebalance_df.reset_index(drop=True)

    def build_order(self, balance: int, price: dict, tar_df, cur_df = None):
        assert balance > 0, Exception('Invalid balance')
        self.order_book.clear()

        if cur_df is not None:
            tar_df = self.__rebalance(tar_df, cur_df)

        for _, row in tar_df.iterrows():
            quantity = int(row['weight'] * balance / price[row['ticker']])

            if quantity > 0:
                self.__create_order(row['ticker'], quantity, 'BUY', 'MARKET')
            elif quantity < 0:
                self.__create_order(row['ticker'], abs(quantity), 'SELL', 'MARKET')

        return self.order_book