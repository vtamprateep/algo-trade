'''
Deprecated 3.1.2021: Roll data methods into broker.py
'''

from abc import ABCMeta, abstractmethod

import os
import numpy as np
import pandas as pd

from algo_trade.event import MarketEvent

class DataHandler(metaclass=ABCMeta):
    '''
    Abstract base class providing interface for all subsequent data handlers. Goal is to output a generated set of bars (OHLCVI) for each symbol requested.
    '''
    @abstractmethod
    def get_latest_bar(self, ticker):
        raise NotImplementedError('Should implement get_latest_bar()')

    @abstractmethod
    def get_latest_bars(self, ticker, N=1):
        raise NotImplementedError('Should implement get_latest_bars()')

    @abstractmethod
    def get_latest_bar_value(self, ticker, val_type):
        raise NotImplementedError('Should implement get_latest_bar_value()')

    @abstractmethod
    def get_latest_bars_values(self, ticker, val_type, N=1):
        raise NotImplementedError('Should implement get_latest_bars_values()')

    @abstractmethod
    def update_bars(self):
        raise NotImplementedError('Should implement update_bars()')

class HistoricCSVDataHandler(DataHandler):
    '''
    Designed to read CSV files for each requested symbol from disk and provide an interface to obtain the "latest" bar in a manner identical to a live trading interface.

    :param events:  Event queue
    :param csv_dir: Absolute directory path to CSV files
    :param ticker_list: List of ticker strings
    '''
    def __init__(self, events, csv_dir, ticker_list, test=False):
        self.events = events
        self.csv_dir = csv_dir
        self.ticker_list = ticker_list

        self.ticker_data = dict()
        self.latest_ticker_data = dict()
        self.ticker_generator = dict()
        
        self.continue_backtest = True

        if not test:
            self._open_convert_csv_files()

    def _open_convert_csv_files(self):
        '''
        Opens CSV files from the data directory, converting them in pandas DataFrames within a ticker dictionary. Current assumption is that the data is taken from YFinance.
        '''
        comb_index = None
        for t in self.ticker_list:
            self.ticker_data[t] = pd.io.parsers.read_csv(
                os.path.join(self.csv_dir, '%s.csv' % t),
                header=0,
                index_col=0,
                parse_dates=True,
                names=[
                    'datetime', 'open', 'high', 'low', 'close', 'volume', 'adj_close'
                ]
            ).sort_index()

            if comb_index is None:
                comb_index = self.ticker_data[t].index
            else:
                comb_index.union(self.ticker_data[t].index)

            self.latest_ticker_data[t] = []

        for t in self.ticker_list:
            self.ticker_data[t] = self.ticker_data[t].reindex(index=comb_index, method='pad')
            self.ticker_generator[t] = self.ticker_data[t].iterrows()

    def _get_new_bar(self, ticker):
        '''
        Returns latest bar from the data feed.
        '''
        return next(self.ticker_generator[ticker])

    def get_latest_bar(self, ticker):
        '''
        Returns the last bar from the latest_ticker list.
        '''
        try:
            bars_list = self.latest_ticker_data[ticker]
        except KeyError:
            print('That ticker is not available in the historical dataset.')
            raise
        else:
            return bars_list[-1]

    def get_latest_bars(self, ticker, N=1):
        '''
        Returns the last N bars from the latest_ticker list, of N-k if less available.
        '''
        try:
            bars_list = self.latest_ticker_data[ticker]
        except KeyError:
            print('That ticker is not available in the historical dataset.')
            raise
        else:
            return bars_list[-N:]

    def get_latest_bar_datetime(self, ticker):
        '''
        Return Python datetime object for the last bar.
        '''
        try:
            bars_list = self.latest_ticker_data[ticker]
        except KeyError:
            print('That ticker is not available in the historical dataset.')
            raise
        else:
            return bars_list[-1][0]

    def get_latest_bar_value(self, ticker, val_type):
        '''
        Returns one of the OHLCVI values from the pandas Bar series object.
        '''
        try:
            bars_list = self.latest_ticker_data[ticker]
        except KeyError:
            print('That ticker is not available in the historical dataset.')
            raise
        else:
            return getattr(bars_list[-1][1], val_type)

    def get_latest_bars_values(self, ticker, val_type, N=1):
        '''
        Returns last N bar values from the latest_symbol list, or N-k if less available.
        '''
        try:
            bars_list = self.get_latest_bars(ticker, N)
        except KeyError:
            print('That ticker is not available in the historical dataset.')
            raise
        else:
            return np.array([getattr(b[1], val_type) for b in bars_list])

    def update_bars(self):
        '''
        Pushes latest bar to the latest_ticker_data structure for all tickers in the ticker list.
        '''
        for t in self.ticker_list:
            try:
                bar = self._get_new_bar(t)
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_ticker_data[t].append((bar[0], bar[1]))

        self.events.put(MarketEvent())

class TDADataHandler(DataHandler):
    '''
    Designed to take a TDA client and allow the user to pull data via the API using the tda-api Python library.

    :param client:  TDA api client, based off of tda-api Python package
    :param ticker_list: List of ticker strings
    '''
    def __init__(self, client, events, ticker_list):
        self.client = client
        self.ticker_list = ticker_list
        self.events = events

        self.ticker_data = dict()
        self.latest_ticker_data = dict()
        self.ticker_generator = dict()

        self.continue_backtest = True
        self.client.set_enforce_enums(enforce_enums=False)

    def get_data(self, period_type = 'year', period = 1, frequency_type = 'daily', frequency = 1):
        '''
        Returns dataframe dictionary of historical prices for a list of tickers
        '''
        comb_index = None
        for t in self.ticker_list:
            response = self.client.get_price_history(
                t,
                period_type=period_type,
                period=period,
                frequency_type=frequency_type,
                frequeny=frequency,
            ).json()

            price_history = pd.DataFrame(
                    data=response['candles'],
                    columns=['datetime', 'open', 'high', 'low', 'close'],
                )
            price_history.set_index('datetime', inplace=True)

            self.ticker_data[t] = price_history

            if comb_index is None:
                comb_index = self.ticker_data[t].index
            else:
                comb_index.union(self.ticker_data[t].index)

            self.latest_ticker_data[t] = list()

        for t in self.ticker_list:
            self.ticker_data[t] = self.ticker_data[t].reindex(index=comb_index, method='pad')
            self.ticker_data[t].sort_index(inplace=True)
            self.ticker_generator[t] = self.ticker_data[t].iterrows()

        return self.ticker_data

    def _get_new_bar(self, ticker):
        '''
        Returns latest bar from the data feed.
        '''
        return next(self.ticker_generator[ticker])

    def get_latest_bar(self, ticker):
        '''
        Returns the last bar from the latest_ticker list.
        '''
        try:
            bars_list = self.latest_ticker_data[ticker]
        except KeyError:
            print('That ticker is not available in the historical dataset.')
            raise
        else:
            return bars_list[-1]

    def get_latest_bars(self, ticker, N=1):
        '''
        Returns the last N bars from the latest_ticker list, of N-k if less available.
        '''
        try:
            bars_list = self.latest_ticker_data[ticker]
        except KeyError:
            print('That ticker is not available in the historical dataset.')
            raise
        else:
            return bars_list[-N:]

    def get_latest_bar_datetime(self, ticker):
        '''
        Return Python datetime object for the last bar.
        '''
        try:
            bars_list = self.latest_ticker_data[ticker]
        except KeyError:
            print('That ticker is not available in the historical dataset.')
            raise
        else:
            return bars_list[-1][0]

    def get_latest_bar_value(self, ticker, val_type):
        '''
        Returns one of the OHLCVI values from the pandas Bar series object.
        '''
        try:
            bars_list = self.latest_ticker_data[ticker]
        except KeyError:
            print('That ticker is not available in the historical dataset.')
            raise
        else:
            return getattr(bars_list[-1][1], val_type)

    def get_latest_bars_values(self, ticker, val_type, N=1):
        '''
        Returns last N bar values from the latest_symbol list, or N-k if less available.
        '''
        try:
            bars_list = self.get_latest_bars(ticker, N)
        except KeyError:
            print('That ticker is not available in the historical dataset.')
            raise
        else:
            return np.array([getattr(b[1], val_type) for b in bars_list])

    def get_current_quotes(self, ticker_list):
        '''
        Returns dictionary of last ticker prices. If input is none, defaults to self.ticker_list created at DataHandler class instantiation.
        '''
        entries = dict()
        if ticker_list is None:
            response = self.client.get_quotes(self.ticker_list).json()
        else:
            response = self.client.get_quotes(ticker_list).json()
        

        for t in self.ticker_list:
            entries[t] = response[t]['lastPrice']
            
        return entries

    def update_bars(self):
        '''
        Pushes latest bar to the latest_ticker_data structure for all tickers in the ticker list.
        '''
        for t in self.ticker_list:
            try:
                bar = self._get_new_bar(t)
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_ticker_data[t].append((bar[0], bar[1]))

        self.events.put(MarketEvent())