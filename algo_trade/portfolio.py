from __future__ import print_function

import numpy as np
import pandas as pd

from algo_trade.event import OrderEvent
from algo_trade.utilities import create_drawdowns, create_sharpe_ratio


class Portfolio:
    '''
    Handles positions and market value of all instruments at a resolution of a "bar." The positions DataFrame stores a time-index of the quantity of positions held.

    The holdings DataFrame stores the cash and total market holdings value of each symbol for a particular time-index, as well as the percentage change in portfolio total across bars.

    :param bars: The DataHandler object with current market data
    :param events: The Event queue object
    :param start_date: The start date (bar) of the portfolio
    :param initial_capital: The starting capital in USD
    '''
    def __init__(self, bars, events, start_date, initial_capital=100000.0):
        '''
        Initialises portfolio with bars and an event queue. Also includes starting datetime index and initial capital.
        '''
        self.bars = bars
        self.events = events
        self.ticker_list = self.bars.ticker_list
        self.start_date = start_date
        self.initial_capital = initial_capital

        self.all_positions = self._construct_all_positions()
        self.current_positions = self._construct_current_positions()
        self.all_holdings = self._construct_all_holdings()
        self.current_holdings = self._construct_current_holdings()

    ##################################################
    # Initialization methods

    def _construct_all_positions(self):
        '''
        Constructs the positions list using the start_date to determine when the time index will begin
        '''
        d = dict( (k,v) for k, v in [(t,0) for t in self.ticker_list] )
        d['datetime'] = self.start_date
        return [d]

    def _construct_all_holdings(self):
        '''
        Constructs the holdings list using the start_date to determine when the time index will begin
        '''
        d = dict( (k,v) for k, v in [ (t, 0.0) for t in self.ticker_list] )
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return [d]

    def _construct_current_positions(self):
        '''
        Constructs the dictionary which will hold the instantaneous positions of the portfolio across all symbols
        '''
        d = dict( (k,v) for k, v in [(t,0) for t in self.ticker_list] )
        return d

    def _construct_current_holdings(self):
        '''
        Constructs the dictionary which will hold the instantaneous value of the portfolio across all symbols
        '''
        d = dict( (k,v) for k, v in [(t, 0.0) for t in self.ticker_list] )
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return d

    ##################################################
    # Pre-open preparation for trading session

    def update_timeindex(self, event):
        '''
        Adds a new record to the positions matrix for the current market data bar. Reflects the PREVIOUS bar, i.e. all current market data at this stage is known (OHLCV).

        Makes use of MarketEvent from the events queue.
        '''
        latest_datetime = self.bars.get_latest_bar_datetime(self.ticker_list[0])

        # Update positions
        dp = dict( (k,v) for k, v in [(t,0) for t in self.ticker_list] )
        dp['datetime'] = latest_datetime

        for t in self.ticker_list:
            dp[t] = self.current_positions[t]

        # Append the current positions
        self.all_positions.append(dp)

        # Update Holdings
        dh = dict( (k,v) for k, v in [(t,0) for t in self.ticker_list] )
        dh['datetime'] = latest_datetime
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']

        for t in self.ticker_list:
            # Approximate to the real value
            market_value = self.current_positions[t] * self.bars.get_latest_bar_value(t, 'adj_close')
            dh[t] = market_value
            dh['total'] += market_value

        # Append current holdings
        self.all_holdings.append(dh)

    ##################################################
    # Update holdings/positions from FillEvent methods

    def _update_positions_from_fill(self, fill):
        '''
        Takes a FillEvent object and updates position matrix to reflect the new position.
        '''
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        self.current_positions[fill.ticker] += fill_dir * fill.quantity

    def _update_holdings_from_fill(self, fill):
        '''
        Takes a FillEvent object and updates holdings matrix to reflect the new holdings value.
        '''
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        fill_cost = self.bars.get_latest_bar_value(fill.ticker, 'adj_close')
        cost = fill_dir * fill_cost * fill.quantity
        self.current_holdings[fill.ticker] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= fill.commission

    def update_fill(self, event):
        '''
        Updates the portfolio current positions and holdings from a FillEvent.
        '''
        if event.type == 'FILL':
            self._update_positions_from_fill(event)
            self._update_holdings_from_fill(event)

    ##################################################
    # Signal Digestion/Order Creation

    def _generate_naive_order(self, signal):
        '''
        Files an Order object as a constant quantity sizing of the signal object, without risk management or position sizing considerations.
        '''
        order = None

        ticker = signal.ticker
        direction = signal.signal_type
        strength = signal.strength

        print(ticker, direction, strength)

        mkt_quantity = 100
        cur_quantity = self.current_positions[ticker]
        order_type = 'MARKET'

        if direction == 'LONG' and cur_quantity == 0:
            order = OrderEvent(ticker, mkt_quantity, 'BUY', order_type)
        if direction == 'SHORT' and cur_quantity == 0:
            order = OrderEvent(ticker, mkt_quantity, 'SELL', order_type)

        if direction == 'EXIT' and cur_quantity > 0:
            order = OrderEvent(ticker, abs(cur_quantity), 'SELL', order_type)
        if direction == 'EXIT' and cur_quantity < 0:
            order = OrderEvent(ticker, abs(cur_quantity), 'BUY', order_type)

        return order

    def update_signal(self, event):
        '''
        Acts on a SignalEvent to generate new orders based on the portfolio logic.
        '''
        if event.type == 'SIGNAL':
            order_event = self._generate_naive_order(event)
            self.events.put(order_event)

    ##################################################
    # Output Backtesting results

    def create_equity_curve_dataframe(self):
        '''
        Creates a pandas DataFrame from the all_holdings list of dictionaries.
        '''
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()
        self.equity_curve = curve

    def output_summary_stats(self):
        '''
        Creates a list of summary statistics for the portfolio
        '''
        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']

        sharpe_ratio = create_sharpe_ratio(returns, periods=252*60*6.5)
        drawdown, max_dd, dd_duration = create_drawdowns(pnl)
        self.equity_curve['drawdown'] = drawdown

        stats = [
            ('Total Return', '%0.2f' % ((total_return - 1.0) * 100.0)),
            ('Sharpe Ratio', '%0.2f' % sharpe_ratio),
            ('Max Drawdown', '%0.2f%%' % (max_dd * 100.0)),
            ('Drawdown Duration', '%d' % dd_duration),
        ]
        self.equity_curve.to_csv('equity.csv')
        return stats