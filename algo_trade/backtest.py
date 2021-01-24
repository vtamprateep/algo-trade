'''
In development
'''

from datetime import datetime, timedelta, date
from dataclasses import dataclass, field
from typing import Iterable

import pandas as pd


@dataclass
class BaseTest:
    client: object = None
    data: object = None
    hparams: dict = field(default=dict)
    population: set = field(default=set)
    strategy: dict = field(default=dict)
    _strategy_count: int = 1

    def add_strategy(self, other, name = None):
        if name:
            self.strategy[name] = other
        else:
            self.strategy[self._strategy_count] = other
            self._strategy_count += 1

        return

    def compile(self, data_function):
        

    def configure(self):
        for _, item in self.strategy.items():
            self.population.update(item.population)

        return

    def run(self):
        pass

if __name__ == '__main__':
    pass