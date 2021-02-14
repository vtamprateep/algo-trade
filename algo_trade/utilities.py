from datetime import datetime, timedelta
from scipy import stats

import pandas as pd
import math
import numpy as np


def create_sharpe_ratio(returns, periods=252, rf=0):
    '''
    Create Sharpe ratio for the strategy, based on a benchmark of zero (i.e. no risk-free rate information).

    :param returns: A pandas Series representing period percentage returns.
    :param periods: Daily (252), Hourly (252 * 6.5), Minutely (252 * 6.5 * 60), etc.
    '''
    return np.sqrt(periods) * (np.mean(returns - rf/periods)) / np.std(returns - rf/periods)

def create_drawdowns(pnl):
    '''
    Calculate the largest peak-to-trough drawdown of the PnL curve as well as the duration of the drawdown. Requires that the pnl_returns is a pandas Series.

    :param pnl: A pandas Series representing period percentage returns.
    '''
    # Calculate cumulative returns curve and set up High Water Mark
    hwm = [0]

    # Create drawdown and duration series
    idx = pnl.index
    drawdown = pd.Series(index=idx)
    duration = pd.Series(index=idx)

    # Loop over the index range
    for t in range(1, len(idx)):
        hwm.append(max(hwm[t-1], pnl[t]))
        drawdown[t] = (hwm[t] - pnl[t])
        duration[t] = (0 if drawdown[t] == 0 else duration[t-1] + 1)

    return drawdown, drawdown.max(), duration.max()

# TODO: Under development
def black_scholes(stock_price, strike_price, time, rf, div, volatility, option_type):
    '''
    Calculates option prices for European calls/puts using the Black-Scholes formula.

    :param stock_price: Current stock price
    :param strike_price: Strike price of the option to be priced
    :param time: Days until option expiry
    :param rf: Risk-free rate
    :param div: Dividend yield of the stock
    :param option_type: CALL or PUT
    '''
    d1 = (math.log(float(stock_price)/strike_price) + ((rf - div) + volatility * volatility / 2) * time) / (volatility * math.sqrt(time))
    d2 = d1 - volatility * math.sqrt(time)

    if option_type == 'call':
        return stock_price * math.exp(-div * time) * stats.norm.cdf(d1) - strike_price * math.exp(-rf * time) * stats.norm.cdf(d2)
    else:
        return strike_price * math.exp(-rf * time) * stats.norm.cdf(-d2) - stock_price * math.exp(-div * time) * stats.norm.cdf(-d1)