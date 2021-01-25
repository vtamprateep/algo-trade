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
'''

@dataclass
class BackTest:
    data_lines = None # Needs to be mirror of data_tota
    params = field(default=dict) # Currently not used
    
    _commission = 0
    _cash_value = 100000
    _data_total = field(default=dict) # Dictionary of symbol keys mapping to dictionary of all price lines
    _instr_value = 0
    _logger = {
        'open_value': list(),
        'close_value': list(),
        'day_gain': list(),
        'day_return': list()
    }
    _order = {
        'open': Queue(),
        'pending': Queue(),
        'close': list(),
        'rejected': list(),
    }
    _population = field(default=set)
    _strategy = field(default=dict)

    def _compile(self):
        assert len(self._data_total), 'No data provided'
        assert len(self._strategy), 'No strategy provided'

        self.data_lines = {k:[] for k in self._data_total.keys}

    def _compute(self):
        pass
    
    def _day_close(self):
        pass

    def _day_start(self, data, new_data):
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
        for i in range(len(self._data_total.values()[0])):
            pass

        