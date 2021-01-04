'''
The account module contains classes and packages to handle order creation and submission to brokers via API.

This module contains the following classes:
    - AccountClient
    - OrderBuilder
    - Order
'''

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
class AccountClient:

    ACC_ID: str
    client: object
    order_book: set = field(default_factory=set)

    def __post_init__(self):
        self.client.set_enforce_enums(enforce_enums=False)

    def __getPrice(self, symbol: list):
        response = self.client.get_quotes(symbol).json()
        entries = list()
        for sym in symbol:
            entries.append(
                [sym, response[sym]['lastPrice']]
            )
            
        return pd.DataFrame(data = entries, columns=['ticker', 'price'])

    @property
    def balance(self):
        response = self.client.get_account(self.ACC_ID).json()
        return response['securitiesAccount']['initialBalances']['liquidationValue']

    @property
    def cash(self):
        response = self.client.get_account(self.ACC_ID).json()
        return response['securitiesAccount']['initialBalances']['cashAvailableForTrading']

    @property
    def order(self):
        response = self.client.get_account(self.ACC_ID, fields=['orders']).json()
        book = response['securitiesAccount']['orderStrategies']
        entries = list()

        for order in book:
            entries.append([
                order['orderLegCollection'][0]['instrument']['symbol'],
                order['quantity'],
                order['orderLegCollection'][0]['instruction'],
                order['orderType'],
                order['price'],
                order['status'],
            ])

        return pd.DataFrame(data = entries, columns = ['ticker', 'quantity', 'action', 'order_type', 'limit', 'status'])
    
    @property
    def position(self):
        response = self.client.get_account(self.ACC_ID, fields=['positions']).json()
        positions = response['securitiesAccount']['positions']
        entries = list()

        for instr in positions:
            entries.append(
                [instr['instrument']['symbol'], instr['marketValue']]
            )

        position_df = pd.DataFrame(data = entries, columns = ['ticker', 'weight'])
        position_df['weight'] = position_df['weight'] / self.balance

        return position_df    

    def buildOrder(self, target_state: pd.DataFrame, dca: bool = False):
        '''
        Dataframe structure:
        ticker: str
        weight: float
        '''

        self.order_book.clear()
        
        if dca:
            current_balance = self.cash
            diff_df = target_state
            diff_df['weight'] = diff_df['weight'] * -1
        else:
            current_balance = self.balance
            current_state = self.position

            join_df = current_state.merge(
                target_state,
                how='outer',
                on='ticker',
                suffixes=('_current', '_target'),
            ).fillna(0)
            join_df['weight'] = (join_df['weight_target'] - join_df['weight_current']) * -1
            
            diff_df = join_df[['ticker', 'weight']]

        price_df = self.__getPrice(diff_df['ticker'].tolist())
        for _, row in diff_df.iterrows():
            quantity = int(row['weight'] * current_balance / price_df[price_df['ticker'] == row['ticker']]['price'])

            if row['ticker'] == 'MMDA1':
                continue
            elif quantity > 0:
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
        return

    def placeOrderTDAmeritrade(self):
        order_queue = list()
        for order in self.order_book:
            if order.action == 'SELL' and order.order_type == 'MARKET':
                self.client.place_order(
                    self.ACC_ID,
                    equities.equity_sell_market(
                        order.ticker,
                        order.quantity,
                    ),
                )
            elif order.action == 'SELL' and order.order_type == 'LIMIT':
                self.client.place_order(
                    self.ACC_ID,
                    equities.equity_sell_limit(
                        order.ticker,
                        order.quantity, 
                        order.limit,
                    ),
                )
            else:
                order_queue.append(order)

        for order in order_queue:
            if order.action == 'BUY' and order.order_type == 'MARKET':
                self.client.place_order(
                    self.ACC_ID,
                    equities.equity_buy_market(
                        order.ticker,
                        order.quantity,
                    ),
                )
            elif order.action == 'BUY' and order.order_type == 'LIMIT':
                self.client.place_order(
                    self.ACC_ID,
                    equities.equity_buy_limit(
                        order.ticker,
                        order.quantity,
                        order.limit
                    ),
                )