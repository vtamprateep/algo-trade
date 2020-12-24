'''
The account module contains classes and packages to handle order creation and submission to brokers via API.

This module contains the following classes:
    - AccountClient
    - OrderBuilder
    - Order
'''

from dataclasses import dataclass
from tda.orders import equities
from tda import auth, client
from pathlib import Path

import pandas as pd
import dotenv
import os, json


class AccountClient:
    def __init__(self, client, ACC_ID: str = None):
        self.client = client
        self.ACC_ID = ACC_ID

        self.client.set_enforce_enums(enforce_enums=False)

    def getPosition(self):
        response = self.client.get_account(self.ACC_ID, fields=['positions']).json()
        positions = response['securitiesAccount']['positions']
        position_dict = {
            'ticker': list(),
            'value': list()
        }

        for instr in positions:
            position_dict['ticker'].append(instr['instrument']['symbol'])
            position_dict['value'].append(instr['marketValue'])

        return pd.DataFrame(data = position_dict)

    def getOrder(self):
        '''
        ticker: Stock symbol
        quantity: Number of stocks to buy/sell
        action: BUY or SELL
        order_type: MARKET or LIMIT
        limit: Limit price
        stats: Order status
        '''
        response = self.client.get_account(self.ACC_ID, fields=['orders']).json()
        book = response['securitiesAccount']['orderStrategies']
        order_dict = {
            'ticker': list(),
            'quantity': list(),
            'action': list(),
            'order_type': list(),
            'limit': list(),
            'status': list(),
        }

        for order in book:
            order_dict['ticker'].append(order['orderLegCollection'][0]['instrument']['symbol'])
            order_dict['quantity'].append(order['quantity'])
            order_dict['action'].append(order['orderLegCollection'][0]['instruction'])
            order_dict['order_type'].append(order['orderType'])
            order_dict['limit'].append(order['price'])
            order_dict['status'].append(order['status'])

        return pd.DataFrame(data = order_dict)

    def placeOrderTDAmeritrade(self, client, account_id, order_book):
        order_queue = list()
        for order in order_book:
            if order.action == 'SELL' and order.order_type == 'MARKET':
                client.place_order(
                    account_id,
                    equities.equity_sell_market(
                        order.ticker,
                        order.quantity,
                    ),
                )
            elif order.action == 'SELL' and order.order_type == 'LIMIT':
                client.place_order(
                    account_id,
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
                client.place_order(
                    account_id,
                    equities.equity_buy_market(
                        order.ticker,
                        order.quantity,
                    ),
                )
            elif order.action == 'BUY' and order.order_type == 'LIMIT':
                client.place_order(
                    account_id,
                    equities.equity_buy_limit(
                        order.ticker,
                        order.quantity,
                        order.limit
                    ),
                )

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
        #self.__portfolioCheck(cur_state, fut_state)

        left_cur_join = cur_state.merge(fut_state, how='outer', on='ticker', suffixes=('_cur', '_fut')).fillna(0)
        #print(left_cur_join)
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

if __name__ == '__main__':
    dotenv.load_dotenv()

    TD_KEY = os.getenv('CONSUMER_KEY')
    ACC_NUMBER = os.getenv('ACC_NUMBER')
    REDIRECT_URI = os.getenv('REDIRECT_URI')
    FOLDER_PATH = os.path.join(Path(__file__).resolve().parents[0].absolute(), 'temp_token')
    TOKEN_PATH = os.path.join(FOLDER_PATH, 'token.pickle')
    API_KEY = TD_KEY + '@AMER.OAUTHAP'
    
    client = auth.easy_client(
        api_key = API_KEY, 
        redirect_uri = REDIRECT_URI,
        token_path = TOKEN_PATH,
    )
    client.set_enforce_enums(enforce_enums=False)
    account_client = AccountClient(client, ACC_NUMBER)
    print(account_client.getOrder())
    print(account_client.getPosition())