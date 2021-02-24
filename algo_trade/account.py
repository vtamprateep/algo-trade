from abc import ABCMeta, abstractmethod


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
        order_book = list()

        for order in book:
            order_book.append(
                {
                    'ticker': order['orderLegCollection'][0]['instrument']['symbol'],
                    'quantity': order['quantity'],
                    'instruction': order['orderLegCollection'][0]['instruction'],
                    'order_type': order['orderType'],
                    'price': order['price'],
                    'status': order['status'],
                }
            )

        return order_book
    
    @property
    def position(self):
        response = self.client.get_account(self.ACC_ID, fields=['positions']).json()
        positions = response['securitiesAccount']['positions']
        entries = dict()
        total_balance = 0

        for instr in positions:
            entries[instr['instrument']['symbol']] = instr['marketValue']
            total_balance += instr['marketValue']

        for ticker in entries:
            entries[ticker] /= total_balance

        return entries