import portfolio


class ExponentialMovingAverage(portfolio.Portfolio):
    def __init__(self, ewa_short, ewa_long, buffer=0):
        self.population = ['SPY']
        self.params={
            'ewa_short': ewa_short,
            'ewa_long': ewa_long,
            'signal_line': signal_line,
        }

    def strategy(self):
        dataclose = self.data['SPY'].close
        ewa_short_value = dataclose.ewm(span=ewa_short).mean().iloc[-1]
        ewa_long_line = dataclose.ewm(span=ewa_long).mean().iloc[-1]

        ewa_avg = (ewa_short_value + ewa_long_value) / 2
        ewa_diff = ewa_short_recent - ewa_long_recent

        ewa_signal = ewa_diff / ewa_avg

        if ewa_signal > 0 and abs(ewa_signal) > buffer:
            return pd.DataFrame(
                data={
                    'ticker': self.population,
                    'weight': [1],
                }
            )
        elif ewa_signal < 0 and abs(ewa_signal) > buffer:
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