import portfolio


class MovingAverageCD(portfolio.Portfolio):
    def __init__(self, ewa_short, ewa_long, signal_line, ):
        self.population = ['SPY']
        self.params={
            'ewa_short': ewa_short,
            'ewa_long': ewa_long,
            'signal_line': signal_line,
        }

    def strategy(self):
        pass