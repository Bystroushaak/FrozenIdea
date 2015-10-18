#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

MAX_DATA = 25  # how much items will be stored for one user (warning: flood)
TIME_DIFF = 60 * 60 * 24  # 1 hour (default time diff)
HELP_FILE = "help.txt"  # path to file with help
MIN_TIME_DIFF = 60  # minimal time diff (used to prevent flood kick)
