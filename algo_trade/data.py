import pandas as pd
import tda


'''
TDA API Search Instruments can take multiple ticker arguments
'''

def get_fundamental(client, symbols):
    response = client.search_instruments(symbols, 'fundamental')

    result_dict = dict()
    for key in response:
        result_dict[key] = response[key]['fundamental']

    return result_dict

def get_price_history(client, symbols, period_type = 'year', period = 1, frequency_type = 'daily', frequency = 1, verbose = False):
    
    '''
    Output from TDA historicals in following format
    {
        'candles': List[{
            'open': float,
            'high': float,
            'low': float,
            'close': float,
            'volume': int (units of millions),
            'datetime': (units of miliseconds)
        }],
        'symbol': str,
        'empty': bool,
    }
    '''
    
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
        
        series_dict = {
            'open': price_history['open'].squeeze(),
            'high': price_history['high'].squeeze(),
            'low': price_history['low'].squeeze(),
            'close': price_history['close'].squeeze(),
        }

        if verbose:
            result_dict[ticker] = series_dict['close']
        else:
            result_dict[ticker] = series_dict

    return result_dict