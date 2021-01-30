import pandas as pd
import tda


'''
TDA API Search Instruments can take multiple ticker arguments
'''

def get_fundamental(client, symbols):
    response = client.search_instruments(symbols, 'fundamental').json()
    
    if len(response) == 1:
        return response[symbols]['fundamental']

    result_dict = dict()
    for key in response:
        result_dict[key] = response[key]['fundamental']

    return result_dict

def get_price_history(client, symbols, period_type = 'year', period = 1, frequency_type = 'daily', frequency = 1):
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