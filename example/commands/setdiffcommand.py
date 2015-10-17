#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from __init__ import MIN_TIME_DIFF


# Command definition ==========================================================
def set_diff_command(obj, info):
    if info.msg == "":
        obj.send("`set_diff` expects one parameter!")
        return

    # convert commands parameter to number
    index = -1
    try:
        index = int(info.msg)
    except ValueError:
        obj.send("`set_diff` command expects one integer parameter!")
        return

    if index <= 0:
        obj.send("Time diff have to be positive number.")
        return

    if index < MIN_TIME_DIFF:
        obj.send(
            "Min. time diff: " + str(MIN_TIME_DIFF) +
            ". Leaving unchanged."
        )
        return

    obj.diff_data[info.nickname] = index
    obj.send("Time diff updated.")
