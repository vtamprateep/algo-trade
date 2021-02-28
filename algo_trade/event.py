from dataclasses import dataclass


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
    :param type: MARKET or LIMIT
    :param limit: Limit price
    '''
    ticker: str
    quantity: int
    action: str
    type: str
    limit: float = None

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