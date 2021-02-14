from abc import ABCMeta, abstractmethod

import pandas as pd


class AccountClient(object):
    '''
    AccountClient abstract base class that allows access to broker account information. Contains property methods that returns information such as account balance, cash, order book, positions, etc.
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def balance(self):
        raise NotImplementedError('Should implement balance()')

    @abstractmethod
    def cash(self):
        raise NotImplementedError('Should implement cash()')

    @abstractmethod
    def order(self):
        raise NotImplementedError('Should implement order()')

    @abstractmethod
    def position(self):
        raise NotImplementedError('Should implement position()')

class TDAAccountClient(AccountClient):
    def __init__(self, client, acc_id):
        self.client = client
        self.ACC_ID = acc_id

        self.client.set_enforce_enums(enforce_enums=False) 

    @property
    def balance(self):
        response = self.client.get_account(self.ACC_ID).json()
        return response['securitiesAccount']['currentBalances']['liquidationValue']

    @property
    def cash(self):
        response = self.client.get_account(self.ACC_ID).json()
        return response['securitiesAccount']['currentBalances']['cashAvailableForTrading']

    @property
    def order(self):
        response = self.client.get_account(self.ACC_ID, fields=['orders']).json()
        book = response['securitiesAccount']['orderStrategies']
        entries = list()

        for order in book:
            entries.append([
                order['orderLegCollection'][0]['instrument']['symbol'],
                order['quantity'],
                order['orderLegCollection'][0]['instruction'],
                order['orderType'],
                order['price'],
                order['status'],
            ])

        return pd.DataFrame(data = entries, columns = ['ticker', 'quantity', 'action', 'order_type', 'limit', 'status'])
    
    @property
    def position(self):
        response = self.client.get_account(self.ACC_ID, fields=['positions']).json()
        positions = response['securitiesAccount']['positions']
        entries = list()

        for instr in positions:
            entries.append(
                [instr['instrument']['symbol'], instr['marketValue']]
            )

        position_df = pd.DataFrame(data = entries, columns = ['ticker', 'weight'])
        position_df['weight'] = position_df['weight'] / self.balance

        return position_df    