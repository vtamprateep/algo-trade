'''
The test_stock_selection module includes unit tests for the following classes in the stock_selection module.

Overview
========

This module tests the following classes:
    - Stock

Stock Tests
-----------

..  autoclass:: TestStock

Usage
=====

This module uses the standard text runner, so it can be executed from the command line as follows:: python test_stock_selection.py
'''

from datetime import datetime, timedelta
from pandas._testing import assert_frame_equal
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import portfolio
import unittest


class TestModuleFunction(unittest.TestCase):
    def setUp(self):
        # Valid
        self.tar_state1 = pd.DataFrame(
            data={'ticker': ['SPY'],'weight': [0.75],}
        )
        self.tar_state2 = pd.DataFrame(
            data={'ticker': ['IWM'],'weight': [1],}
        )
        self.tar_state3 = pd.DataFrame(
            data={'ticker': ['SPY', 'IWM'],'weight': [0.75, 0.25],}
        )
        self.cur_state1 = pd.DataFrame(
            data={'ticker': ['MMDA1'],'weight': [1],}
        )
        self.cur_state2 = pd.DataFrame(
            data={'ticker': ['SPY', 'IWO'],'weight': [0.5, 0.5],}
        )

        # Invalid
        self.tar_state_er = pd.DataFrame(
            data={'ticker': ['SPY', 'IWM'],'weight': [0, -0.1],}
        )
        self.cur_state_er = pd.DataFrame(
            data={'ticker': ['SPY', 'IWM'],'weight': [0.9, 0.9],}
        )

    def test_get_data_yahoofinance(self):
        output1 = portfolio.get_data_YahooFinance(['SPY'])
        self.assertIn('SPY', output1)

        output2 = portfolio.get_data_YahooFinance(['SPY', 'IWO', 'IWM'])
        self.assertEqual(set(output2.keys()), {'SPY', 'IWO', 'IWM'})
        for item in output2:
            print(output2[item].shape[0])
            self.assertLessEqual(abs(output2[item].shape[0] - 252), 5)
            self.assertEqual(set(output2[item].columns), {'Open', 'High', 'Low', 'Close'})

        output3 = portfolio.get_data_YahooFinance(['SPY'], '2y', '1wk')
        self.assertLessEqual(abs(output3['SPY'].shape[0] - 104), 4)

    def test_rebalance(self):
        with self.assertRaises(Exception) as cm:
            portfolio.rebalance(self.tar_state_er)
            portfolio.rebalance(self.tar_state1, self.cur_state_er)

        self.assertTrue(
            pd.DataFrame.equals(
                portfolio.rebalance(self.tar_state1, self.cur_state1),
                pd.DataFrame(data={'ticker':['SPY'], 'weight':[-0.75]})
            )
        )
        self.assertTrue(
            pd.DataFrame.equals(
                portfolio.rebalance(self.tar_state1),
                pd.DataFrame(data={'ticker':['SPY'], 'weight':[-0.75]})
            )
        )
        self.assertTrue(
            pd.DataFrame.equals(
                portfolio.rebalance(self.tar_state2, self.cur_state2),
                pd.DataFrame(data={'ticker':['IWM', 'IWO', 'SPY'], 'weight':[-1, 0.5, 0.5]})
            )
        )
        self.assertTrue(
            pd.DataFrame.equals(
                portfolio.rebalance(self.tar_state3, self.cur_state2),
                pd.DataFrame(data={'ticker':['IWM', 'IWO', 'SPY'], 'weight':[-0.25, 0.5, -0.25]})
            )
        )