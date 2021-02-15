from dataclasses import dataclass, field
from tda.orders import equities

import pandas as pd
import json


class Event(object):
    '''
    Base class providing interface for all inherited events.
    '''
    pass

class FillEvent(Event):
    '''
    Encapsulates notion of a filled order, as returned from a brokerage. Stores quantity of an instrument actually filled and at what price. In addition, stores the commission of the trade from the brokerage.

    :param timeindex: Bar-resolution when order was filled
    :param ticker: Instrument filled
    :param exchange: Exchange where order was filled
    :param quantity: Filled quantity
    :param direction: Direction of fill ("BUY" or "SELL")
    :param fill_cost: Holdings value in dollars
    :param commission: Optional commission sent from broker
    '''
    def __init__(self, timeindex, ticker, exchange, quantity, direction, fill_cost, commission=None):
        self.type = 'FILL'
        self.timeindex = timeindex
        self.ticker = ticker
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost

class MarketEvent(Event):
    '''
    Handles the event of receiving a new market update with corresponding bars.
    '''
    def __init__(self):
        self.type = 'MARKET'

@dataclass(frozen=True)
class OrderEvent(Event):
    '''
    Handles the event of sending an Order to an execution system.
    Order contains a ticker, type (MARKET or LIMIT), quantity, and direction (BUY or SELL)

    :param ticker: Stock symbol
    :param quantity: Number of stocks to buy/sell
    :param action: BUY or SELL
    :param order_type: MARKET or LIMIT
    :param limit: Limit price
    '''
    ticker: str
    quantity: int
    action: str
    order_type: str
    limit: float = None

    def print_order(self):
        print(
            'Order: Ticker=%s, Type=%s, Quantity=%s, Action=%s, Limit=%s' % (self.ticker, self.order_type, self.quantity, self.action, self.limit)
        )

class SignalEvent(Event):
    '''
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.

    :param strategy_id: Unique identifier for the strategy that generated the signal.
    :param ticker: Ticker symbol.
    :param datetime: Timestamp which signal was generated
    :param signal_type: 'LONG' or 'SHORT'
    :param strength: Adjustment factor "suggestion" used to scale quantity at the portfolio level
    '''
    def __init__(self, strategy_id, ticker, datetime, signal_type, strength):
        self.type = 'SIGNAL'
        self.strategy_id = strategy_id
        self.ticker = ticker
        self.datetime = datetime
        self.signal_type = signal_type
        self.strength = strength

class OrderBuilder:
    def __init__(self):
        self.order_book = set()

    def _create_order(self, ticker, quantity, action, order_type):
        self.order_book.add(
                    OrderEvent(
                        ticker=ticker,
                        quantity=quantity,
                        action=action,
                        order_type=order_type,
                    )
                )
        return

    def _rebalance(self, tar_state, cur_state):
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
            tar_df = self._rebalance(tar_df, cur_df)

        for _, row in tar_df.iterrows():
            quantity = int(row['weight'] * balance / price[row['ticker']])

            if quantity > 0:
                self._create_order(row['ticker'], quantity, 'BUY', 'MARKET')
            elif quantity < 0:
                self._create_order(row['ticker'], abs(quantity), 'SELL', 'MARKET')

        return self.order_book