from dataclasses import dataclass

import pandas as pd


class Account:
    def __init__(self):
        pass

class OrderBuilder:
    def __init__(self):
        pass

    def rebalancePortfolio(self, value: float, cur_state: pd.DataFrame, fut_state: pd.DataFrame):
        pass

@dataclass
class Order:
    ticker: str
    quantity: int
    action: str
    order_type: str