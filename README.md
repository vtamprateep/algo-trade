# Algorithmic Portfolio Management

**DISCLAIMER: This is a personal project of mine to create a library that facilitates portfolio management using the TDAmeritrade platform. I am not a professional software engineer and cannot attest to robust testing of this library. Additionally, stock trading is an inherently risky practice and is subject to substantial losses. I am not responsible for any losses incurred through use of this library nor any edge cases/bugs that may occur. You have been warned.**

## Overview

`algo_trade` is designed to facilitate the creation and implementation of a portfolio management strategy. There exists free Python packages that either facilitate getting financial data, backtesting trading strategies, or connecting to trading accounts to place trades. This package is specifically created with the intent to combine those features of other financial Python tools. `algo_trade` utilizes other financial Python packages and serves as a wrapper to provide an end-to-end trading experience.

## How Does It Work?

Install the package via `pip install [INSERT PACKAGE NAME HERE]`

As `algo_trade` is designed to integrate features of existing Python packages, usage of the package to define and implement trading strategies requires subclassing as well as knowledge of integrated Python packages. The two main classes used are `AccountClient` and `Portfolio`.

`AccountClient` serves as a connection to trading accounts - currently, the only supported client is TDAmeritrade due to their public API and leverages the [`tda-api`](https://github.com/alexgolec/tda-api) Python package. A sample instantiation of the `AccountClient` class can be seen below:

```python
from tda import auth, client
from algo_trade.account import AccountClient


tda_client = auth.easy_client(
        api_key = API_KEY, 
        redirect_uri = REDIRECT_URI,
        token_path = TOKEN_PATH,
    )

account = AccountClient(client=tda_client, ACC_ID=ACC_ID)
```

`Portfolio` is the container for algorithmic strategies and can be considered where all the logic, documentation, and indicators the user wants to establish should be placed. A sample definition and instantiation of the `Portfolio` class can be seen below, implementing a dollar-cost-averaging of SPY and IWM using a 75:25 weighting:

```python
from algo_trade.portfolio import Portfolio
import pandas as pd


class SpyIwmStrategy(Portfolio):
    population = ['SPY', 'IWM']

    def strategy(self):
        return pd.DataFrame(
            data={
                'ticker': population,
                'weight': [0.75, 0.25]
            }
        )

port_strat = SpyIwmStrategy()
print(port_strat.run())
```

An important but not strictly needed class (depending on how you intend to set up your strategy and whether you need data) is the `DataBuilder` class, also present in the `portfolio.py` module. `DataBuilder` allows you to get data, using either `yfinance` or `tda-api`, to perform necessary calculations in your strategy. A sample instantiation of `DataBuilder` to get data via TDAmeritrade can be seen below:

```python
from tda import auth, client
from algo_trade.portfolio import DataBuilder


data_builder = DataBuilder(client=tda_client) # tda_client created in above code sample
data_builder.TDAmeritrade(
    port_strat,
    port_strat.population,
)
print(port_strat.holdings)
```

Stock level data are all added to the `Portfolio` object as `Stock` objects which contain their symbol as well as historical price data stored as a dataframe.

Trade orders are created by the `AccountClient` by comparing the current account portfolio weights against target portfolio weights, selling and buying stocks as necessary to get as close to the target portfolio weights as possible. Below is an example of a `Portfolio` strategy returning target portfolio weights to the `AccountClient` which calculates the difference, creates the orders, and submits the order onto the TDAmeritrade platform:

```python
target_weights = port_strat.run()
account.buildOrder(target_weights)
account.placeOrderTDAmeritrade()
```

Lastly, the `indicator.py` module contains a series of pre-defined calculations that a use can use within a strategy to calculate metrics such as volatility, sharpe ratio, mean, geometric mean, etc. This module provides a toolset that users can leverage but is not strictly necessary. Most calculations are done on dataframes, so it is relatively simple to create a personal library of indicators if desired.

## FAQ

***Is there a built in way to designate frequency of the strategy trades?***

No, though it was considered for a time. A workaround would be to set up a cron job to run the strategy at the appropriate frequency.

***Can this library be used for day-trading or high-frequency trading?***

Similar to the above answer, you could use the package for day-trading by setting up a strategy and a related cron job to run every minute or half-hour, though if you have a day-trading account there would be other platforms that provide the tool to do so already. Additionally, this package leverages the `tda-api` library specifically for HTTP clients - there is an additionally feature in that library used for streaming data that would be better suited for day-trading, but that is out of the scope of this project

For high-frequency trading, and depending on the trading strategy, some would argue that Python would not be the best language to do this and that a faster programming language (such as C++ or Golang) is better. Again, this too is out of the scope of the project, but even if it were in-scope, Python would probably not be the best approach.

***Will there be additional APIs/clients incorporated into this project besides TDAmeritrade?***

Perhaps if other clients that both the API and account administration fees are free, I would consider it. However, there are also other features generally that I would like to implement, so this library will probably be limited to TDAmeritrade for the time being.