'''
In development
'''

from datetime import date, datetime, timedelta
from dataclasses import dataclass, field
from queue import Queue
from typing import Iterable

import pandas as pd

'''
Separate OHLC into separate pd.Series object, easier to manipulate. Do this for the data module too.

Iterator to give data values to data_lines and yields to allow self.next computation
'''

@dataclass
class BackTest:
    data_lines = None # Needs to be mirror of data_tota
    params = field(default=dict) # Currently not used
    
    _commission = 0
    _cash_value = 100000
    _account = field(default=dict)
    _data_total = field(default=dict) # Dictionary of symbol keys mapping to dictionary of all price lines
    _log = list()
    _order = {
        'open': Queue(),
        'pending': Queue(),
        'close': list(),
    }
    _population = field(default=set)
    _strategy = field(default=dict)

    def _compile(self):
        assert len(self._data_total), 'No data provided'
        assert len(self._strategy), 'No strategy provided'

        self.data_lines = {k: pd.Series() for k in self._data_total.keys}
        self._log.append(
            {
                'open_value': self._cash_value,
                'close_value': self._cash_value,
                'day_gain': 0,
                'day_pct_gain': 0,
            }
        )

    def _get_account_value(self, account, data):
        total_value = 0

        for key, value in account.items():
            try:
                total_value += data[key]['close'][-1] * value
            except:
                total_value += data[key][-1] * value

        return total_value

    def _logger(self, log, prev_log, cur_cash, cur_stock_val):
        cur_total = cur_cash + cur_stock_val
        day_gain = cur_total - prev_log['close_value']

        entry = {
            'open_value': prev_log['close_value'],
            'close_value': cur_total,
            'day_gain': day_gain,
            'day_pct_gain': float(day_gain / prev_log['close_value']),
        }

        log.append(entry)
        return
    
    def _post_session(self):
        pass

    def _pre_session(self):
        pass
    
    def add_data(self, other, name):
        self._data_total[name] = other
        return
    
    def add_strategy(self, other, name):
        self._strategy[name] = other
        return

    def run(self):
        self._compile()

        # Is there a better way to do this?
        data_key = self._data_total.keys
        for index in range(len(self._data_total[data_key[0]])):
            self._pre_session()
            self._post_session()
            self._logger(
                self._log,
                self._log[-1], 
                self._cash_value,
                self._get_account_value(self._account, self.data_lines),
            )

    def session(self):
        pass

        