from datetime import datetime, timedelta, date

from dataclasses import dataclass
from collections.abc import Iterable

import backtrader as bt
import pandas as pd


@dataclass
class BaseTest:
    strategy: Iterable = set()
    client = None
    data_source = None
    start = None
    end = None
    frequency: str = None
    cash: int = None

    def addStrategy(self, other):
        self.strategy.add(other)

@dataclass
class BackTest(BaseTest):
    def __post_init__(self):
        pass

    def run(self):
        pass


@dataclass
class FrontTest(BaseTest):
    def __post_init__(self):
        pass


if __name__ == '__main__':
    pass