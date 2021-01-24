import numpy as np
import pandas as pd
import yfinance as yf
import tda


'''
TDA API Search Instruments can take multiple ticker arguments
'''

def get_fundamental(client, symbols: list):
    response = client.search_instruments(symbols, 'fundamental')

    result_dict = dict()
    for key in response:
        result_dict[key] = response[key]['fundamental']

    return result_dict

def get_price_history(client, symbols: list, period_type: str = 'year', period: int = 1, frequency_type: str = 'daily', frequency: int = 1, verbose: bool = False):
    
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
        price_history = price_history.set_index('Date')

        if verbose:
            result_dict[ticker] = price_history['close'].squeeze()
        else:
            result_dict[ticker] = price_history

    return result_dict