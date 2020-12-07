from dataclasses import dataclass

import src.portfolio as portfolio # How can I make my module a package so it will automatically work?
import pandas as pd


class SpyIwmStrategy(portfolio.Portfolio):
    holdings = ['SPY', 'IWM']
    dca = True

    def strategy(self):
        return pd.DataFrame(
            data = {
                'ticker': self.holdings,
                'weight': [0.75, 0.25],
            }
        )