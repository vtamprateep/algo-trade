from dataclasses import dataclass, field


@dataclass
class BaseModel:
    client: object = None
    data: object = None
    params: dict = {
        'period_type': 'year',
        'period': 1,
        'frequency_type': 'daily',
        'frequency': 1,
    }
    population: list = field(default=list)

    def _validate(self, data):
        assert len(self.population) > 0, 'Missing security population'

        if data:
            assert self.client != None, 'Missing TDAmeritrade client'
            assert 'period_type' in self.params, 'Missing period_type param'
            assert self.params['period_type'] in {'day', 'month', 'year', 'ytd'}
            assert 'period' in self.params, 'Missing period param'
            assert 'frequency_type' in self.params, 'Missing frequency_type param'
            assert self.params['frequency_type'] in {'minute', 'daily', 'weekly', 'monthly'}
            assert 'frequency' in self.params, 'Missing frequency param'

    def _get_data(self, client, symbols, period_type='year', period=1, frequency_type='daily', frequency=1):
        if type(symbols) == str:
            response = client.get_price_history(
                symbols,
                period_type=period_type,
                period=period,
                frequency_type=frequency_type,
                frequeny=frequency,
            ).json()

            price_history = pd.DataFrame(
                    data=response['candles'],
                    columns=['date', 'open', 'high', 'low', 'close'],
                )
            price_history['Date'] = price_history['Date'].dt.date
            
            return price_history

        result_dict = dict()
        for ticker in symbols:
            response = client.get_price_history(
                ticker,
                period_type=period_type,
                period=period,
                frequency_type=frequency_type,
                frequeny=frequency,
            ).json()

            price_history = pd.DataFrame(
                    data=response['candles'],
                    columns=['date', 'open', 'high', 'low', 'close'],
                )
            price_history['Date'] = price_history['Date'].dt.date

            result_dict[ticker] = price_history

        return result_dict
        
    def run(self, data=True):
        self._validate(data)

        if data:
            self.data = self._get_data(
                self.client,
                self.population,
                self.params['period_type'],
                self.params['period'],
                self.params['frequency_type'],
                self.params['frequency'],
            )

        return self.strategy(self.data)

    def strategy(self, data=None):
        pass