#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
class SeeDiffCommand:
    def react(self, obj, obj_locals):
        globals().update(obj_locals)

        if nickname not in obj.diff_data:
            obj.send(
                "You didn't set your own time diff. Using default " +
                str(TIME_DIFF) + "s."
            )
        else:
            obj.send(
                "Your time diff is set to %ds." % obj.diff_data[nickname]
            )
