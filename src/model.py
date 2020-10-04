'''
The builder module includes methods to randomly generate stock prices. This is to help support unit testing and increase readability by using random seeds to generate random prices rather than rely on external APIs or retain .CSV files containing pricing information.

Usage
=====

This module is not designed to be used standalone but imported into relevant test files to generate datasets for unit testing.
'''

from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import random


class PriceBuilder:
    def __init__(self, volatility: float, average: float, size: int, start: datetime = datetime(2000,1,1)):
        self.volatility = volatility
        self.average = average
        self.size = size
        self.start = start
        self.rng = random.Random()

    def build(self):
        date_array = np.arange(start=self.start,stop=self.start + timedelta(days=self.size), step=timedelta(days=1))
        price_array = [self.average]

        for _ in range(self.size - 1):
            rand_num = self.rng.random()
            change_factor = 2 * rand_num * self.volatility

            if change_factor > self.volatility:
                change_factor -= 2 * self.volatility

            price_array.append(price_array[-1] + price_array[-1] * change_factor)

        return pd.DataFrame({
            'Date': date_array,
            'Adj Close': price_array
        })