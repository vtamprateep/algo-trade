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
from typing import Iterable


import json
import os
import pandas as pd
import selenium


@dataclass
class AccountClient:

    ACC_ID: str
    client: object
    order_book: set = field(default_factory=set)

    def __post_init__(self):
        self.client.set_enforce_enums(enforce_enums=False)    

    def __submitBuy(self, order):
        if order.action == 'BUY' and order.order_type == 'MARKET':
                self.client.place_order(
                    self.ACC_ID,
                    equities.equity_buy_market(
                        order.ticker,
                        order.quantity,
                    ),
                )
        elif order.action == 'BUY' and order.order_type == 'LIMIT' and order.limit:
            self.client.place_order(
                self.ACC_ID,
                equities.equity_buy_limit(
                    order.ticker,
                    order.quantity,
                    order.limit
                ),
            )
        else:
            raise Exception('Invalid BUY order.')

    def __submitSell(self, order):
        if order.action == 'SELL' and order.order_type == 'MARKET':
                self.client.place_order(
                    self.ACC_ID,
                    equities.equity_sell_market(
                        order.ticker,
                        order.quantity,
                    ),
                )
        elif order.action == 'SELL' and order.order_type == 'LIMIT' and order.limit:
            self.client.place_order(
                self.ACC_ID,
                equities.equity_sell_limit(
                    order.ticker,
                    order.quantity, 
                    order.limit,
                ),
            )
        else:
            raise Exception('Invalid SELL order.')

    @property
    def balance(self):
        response = self.client.get_account(self.ACC_ID).json()
        return response['securitiesAccount']['currentBalances']['liquidationValue']

    @property
    def cash(self):
        response = self.client.get_account(self.ACC_ID).json()
        return response['securitiesAccount']['currentBalances']['cashAvailableForTrading']

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

    def get_price(self, symbol):
        response = self.client.get_quotes(symbol).json()
        entries = dict()

        if type(symbol) is str:
            return {symbol:response[symbol]['lastPrice']}
        
        for sym in symbol:
            entries[sym] = response[sym]['lastPrice']
            
        return entries

    def place_order_TDAmeritrade(self, book):
        order_queue = list()

        for order in book:
            if order.action == 'SELL':
                self.__submitSell(order)
            else:
                order_queue.append(order)

        for order in order_queue:
            self.__submitBuy(order)

def refresh_token(webdriver_func, api_key, redirect_uri, token_path=None):
    auth.client_from_login_flow(
        webdriver=webdriver_func,
        api_key=api_key,
        redirect_url=redirect_uri,
        token_path=token_path,
    )

    return