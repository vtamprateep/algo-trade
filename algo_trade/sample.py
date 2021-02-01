import portfolio
import pandas as pd

class ExponentialMovingAverage(portfolio.Portfolio):
    def __init__(self, ewa_short, ewa_long, buffer=0):
        self.population = ['SPY']
        self.params={
            'ewa_short': ewa_short,
            'ewa_long': ewa_long,
        }

    def strategy(self):
        dataclose = self.data['SPY'].close
        ewa_short_value = dataclose.ewm(span=self.params.ewa_short).mean().iloc[-1]
        ewa_long_value = dataclose.ewm(span=self.params.ewa_long).mean().iloc[-1]

        ewa_avg = (ewa_short_value + ewa_long_value) / 2
        ewa_diff = ewa_short_value - ewa_long_value

        ewa_signal = ewa_diff / ewa_avg

        if ewa_signal > 0 and abs(ewa_signal) > self.params.buffer:
            return pd.DataFrame(
                data={
                    'ticker': self.population,
                    'weight': [1],
                }
            )
        elif ewa_signal < 0 and abs(ewa_signal) > self.params.buffer:
            return pd.DataFrame(
                data={
                    'ticker': self.population,
                    'weight': [0],
                }
            )
        else:
            return None       

class SimpleMovingAverage(portfolio.Portfolio):
    pass