from __future__ import print_function

import datetime
import pprint
import queue
import time


class Backtest(object):
    '''
    Encapsulates the settings and components for carrying out an event-driven backtest.

    :param csv_dir: Hard root to CSV data directory
    :param ticker_list: List of ticker strings
    :param initial_capital: Starting capital for portfolio
    :param heartbeat: Backtest "heartbeat" in seconds
    :param start_date: Start datetime of the strategy
    :param data_handler: (Class) Handles market datafeed
    :param execution_handler: (Class) Handles the orders/fills for trades
    :param portfolio: (Class) Keeps track of portfolio current and prior positions
    :param strategy: (Class) Generates signals based on market data
    '''
    def __init__(self, ticker_list, start_date, strategy_class, broker_class, portfolio_class, data=None, csv_dir=None, initial_capital=100000.0, heartbeat=0.0):
        # Assign state class variables
        self.ticker_list = ticker_list
        self.initial_capital = initial_capital
        self.start_date = start_date
        self.data = data
        self.csv_dir = csv_dir
        self.heartbeat = heartbeat
        

        # Instance classes
        self.strategy_class = strategy_class
        self.broker_class = broker_class
        self.portfolio_class = portfolio_class

        # Create event queue that all Event objects are queued into
        self.events = queue.Queue()

        # Backtest metrics
        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1

        self._generate_trading_instances()

    def _generate_trading_instances(self):
        '''
        Generates trading instance objects from their class types.
        '''
        print('Creating DataHandler, Strategy, Broker, and Portfolio objects...')
        self.broker = self.broker_class(self.events, self.ticker_list, self.data, self.csv_dir)
        self.strategy = self.strategy_class(self.broker, self.events)
        self.portfolio = self.portfolio_class(self.broker, self.events, self.start_date, self.initial_capital)

    def _run_backtest(self):
        '''
        Executes the backtest.
        '''
        i = 0
        while True:
            i += 1
            print(i)

            if self.data_handler.continue_backtest == True:
                self.data_handler.update_bars()
            else:
                break

            # Handle events queue
            while True:
                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.type == 'MARKET':
                            self.strategy.calculate_signals(event)
                            self.portfolio.update_timeindex(event)
                        elif event.type == 'SIGNAL':
                            self.signals += 1
                            self.portfolio.update_signal(event)
                        elif event.type == 'ORDER':
                            self.orders += 1
                            self.broker.execute_order(event)
                        elif event.type == 'FILL':
                            self.fills += 1
                            self.portfolio.update_fill(event)

            time.sleep(self.heartbeat)

    def _output_performance(self):
        '''
        Outputs the strategy performance from the backtest
        '''
        self.portfolio.create_equity_curve_dataframe()

        print('Creating summary stats...')
        stats = self.portfolio.output_summary_stats()

        print('Creating equity curve...')
        print(self.portfolio.equity_curve.tail(10))
        pprint.pprint(stats)

        print('Signals: %s' % self.signals)
        print('Orders: %s' % self.orders)
        print('Fills: %s' % self.fills)

    def simulate_trading(self):
        '''
        Simulates the backtest and outputs portfolio performance.
        '''
        self._run_backtest()
        self._output_performance()