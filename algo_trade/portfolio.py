'''
The portfolio module includes modules needed import data and perform analysis to select a basket of stocks using Markowitz's efficient frontier portfolio theory.

This module contains the following classes:
    - Portfolio

Portfolio
---------

..  autoclass:: Portfolio
    :members:

'''

from dataclasses import dataclass, field

@dataclass
class Portfolio:
    '''
    Portfolio class, contains a collection of stock objects representing various securities and their price data at different resolutions.
    '''

    data: object = None
    params: dict = field(default=dict)

    # Run strategy and create optimal holdings to pass to orderbuilder
    def run(self):
        return self.strategy()

    def strategy(self):
        # Base class, override strategy when defining trading algorithms, should return dataframe with holdings and weight of each
        pass

    def set_data(self, other):
        self.data = other

    def set_params(self, other):
        self.params = other