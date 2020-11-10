'''
The indicator module includes classes and functions designed to operate on a time-series to produce signals or other calculations used to determine a buy/sell decision within a strategy object.

Overview
========

This module contains the following classes
    - Indicator

Usage
=====

The indicator class serves as a library of calculations, either by industry standard or user-made, to be performed on a set of time-series price information. This class should be instantiated within a strategy object and used on the time-series information which is then used to create buy/sell decisions.
'''

from datetime import datetime, timedelta

import yfinance as yf
import pandas as pd
import numpy as np
import math
import random


class Indicator:
    '''
    Feature requirements:
        - Needs to be able to work on DataFrames and Lists
        - Needs to be able to work on a list of lists
        - Needs to be able to work on DataFrames with multiple columns
    '''

    def getVolatility(self, data):
        pass
    
    def getSharpe(self):
        pass

    def getSortino(self):
        pass

    