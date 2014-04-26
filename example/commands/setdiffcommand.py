#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
class SetDiffCommand:
    def react(self, obj, obj_locals):
        globals().update(obj_locals)

        if msg == "":
            obj.send("`set_diff` expects one parameter!")
            return

        # convert commands parameter to number
        index = -1
        try:
            index = int(msg)
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

        obj.diff_data[nickname] = index
        obj.send("Time diff updated.")
