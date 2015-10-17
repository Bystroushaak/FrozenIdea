#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from __init__ import TIME_DIFF


# Command definition ==========================================================
def see_diff_command(obj, info):
    if info.nickname not in obj.diff_data:
        obj.send(
            "You didn't set your own time diff. Using default " +
            str(TIME_DIFF) + "s."
        )
        return

    obj.send(
        "Your time diff is set to %ds." % obj.diff_data[info.nickname]
    )
