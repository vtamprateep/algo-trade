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
    pass