# Algorithmic Portfolio Management

**DISCLAIMER: This is a personal project of mine to create a library that facilitates portfolio management using the TDAmeritrade platform. I am not a professional software engineer and cannot attest to robust testing of this library. Additionally, stock trading is an inherently risky practice and is subject to substantial losses. I am not responsible for any losses incurred through use of this library nor any edge cases/bugs that may occur. You have been warned.**

## Overview

`algo_trade` is designed to facilitate the creation and implementation of a portfolio management strategy. There exists free Python packages that either facilitate getting financial data, backtesting trading strategies, or connecting to trading accounts to place trades. This package is specifically created with the intent to combine those features of other financial Python tools. `algo_trade` utilizes other financial Python packages and serves as a wrapper to provide an end-to-end trading experience.

## How Does It Work?

Install the package via `pip install algo-trade`

As `algo_trade` is designed to integrate features of existing Python packages, usage of the package to define and implement trading strategies requires subclassing as well as knowledge of integrated Python packages. There are three main classes that allow for account information and trading: `Strategy`, `TDABroker`, and `AccountClient`

`Strategy` is the base strategy class that should be subclassed when defining and instantiating a strategy. As of now, `Strategy` subclasses should only output two types of objects: (1) A dictionary containing target asset weights and (2) `OrderEvents`, objects defining a certain asset to be traded, submitted to a `TDABroker` instance to be executed via the TDA API. A sample constant weight, dollar-cost-averaging strategy can be seen below:

```python
from algo_trade.strategy import Strategy

class SpyIwmDCA(Strategy):
    def calculate_signals(self):
        target_weight = { 'SPY': 0.75, 'IWM': 0.25 }
        return target_weight
```

`TDABroker` is a broker instance that feeds data to strategies as well as executes trades. The object also contains a `rebalance` method to help individuals with strategies that return a target portfolio asset weighting rather than signals/orders. Currently, `algo-trade` does not support any form of signal parsing into `OrderEvents`. Adding onto the above example, a sample portfolio rebalancing can be seen below:

```python
from algo_trade.broker import TDABroker
from queue import Queue

event_queue = Queue()
tda_client = auth.easy_client(
        api_key = API_KEY, 
        redirect_uri = REDIRECT_URI,
        token_path = TOKEN_PATH,
    )
tda_broker = TDABroker(tda_client, TDA_ACC_ID, event_queue, None)

# Create dummy constants for portfolio rebalancing
balance = 100000.0
price = { 'SPY': 300, 'IWM': 200 }
current_asset_allocation = { 'MMDA1': 1.0 } # 'MMDA1' is the cash equivalent for TDAmeritrade
target_weight = { 'SPY': 0.75, 'IWM': 0.25 }

# Rebalance portfolio
tda_broker.rebalance(balance, price, target_weight, current_asset_allocation)

# Execute created orders
while not event_queue.empty():
    next_order = event_queue.get()
    tda_broker.execute_order(next_order)
```

`TDAAccountClient` is a general class that gives account information, including outstanding orders, balances, cash, and position. The main use for this, outside of general account information, is to get current cash balance and input it into the `TDABroker` rebalance method to do dollar-cost-averaging. The same sub-sample code above but for dollar-cost-averaging:

```python
from algo_trade.broker import TDABroker
from algo_trade.account import TDAAccountClient
from queue import Queue
tda_client = auth.easy_client(
        api_key = API_KEY, 
        redirect_uri = REDIRECT_URI,
        token_path = TOKEN_PATH,
    )
tda_broker = TDABroker(tda_client, TDA_ACC_ID, event_queue, None)
tda_account = TDAAccountClient(tda_client, TDA_ACC_ID)

# Create dummy constants for portfolio rebalancing
balance = tda_account.cash
price = { 'SPY': 300, 'IWM': 200 }
target_weight = { 'SPY': 0.75, 'IWM': 0.25 }

# Rebalance portfolio
tda_broker.rebalance(balance, price, target_weight)

# Execute created orders
while not event_queue.empty():
    next_order = event_queue.get()
    tda_broker.execute_order(next_order)
```
(Note: Omitting the current asset allocation in the `rebalance` method is equivalent to assuming the entire `balance` variable is cash)

## Backtesting

Part of every good 

## FAQ

***Is there a built in way to designate frequency of the strategy trades?***

No, though it was considered for a time. A workaround would be to set up a cron job to run the strategy at the appropriate frequency.

***Can this library be used for day-trading or high-frequency trading?***

Similar to the above answer, you could use the package for day-trading by setting up a strategy and a related cron job to run every minute or half-hour, though if you have a day-trading account there would be other platforms that provide the tool to do so already. Additionally, this package leverages the `tda-api` library specifically for HTTP clients - there is an additionally feature in that library used for streaming data that would be better suited for day-trading, but that is out of the scope of this project

For high-frequency trading, and depending on the trading strategy, some would argue that Python would not be the best language to do this and that a faster programming language (such as C++ or Golang) is better. Again, this too is out of the scope of the project, but even if it were in-scope, Python would probably not be the best approach.

***Will there be additional APIs/clients incorporated into this project besides TDAmeritrade?***

Perhaps if other clients that both the API and account administration fees are free, I would consider it. However, there are also other features generally that I would like to implement, so this library will probably be limited to TDAmeritrade for the time being.
