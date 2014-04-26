#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
class RemoveCommand:
    def react(self, obj, obj_locals):
        globals().update(obj_locals)

        if data_len == 0:
            obj.send("There is no TODO for you (yet).")
            return

        if msg == "":
            obj.send("`remove` expects index parameter!")
            return

        if msg == "*":
            del obj.time_data[nickname]
            del obj.todo_data[nickname]
            obj.send("All data removed.")
            return

        # convert commands parameter to number
        index = -1
        try:
            index = int(msg)
        except ValueError:
            obj.send("`remove` commandPattern expects integer parameter!")
            return

        # check range of `remove` parameter
        if index < 0 or index >= data_len:
            obj.send("Bad index!")
            return

        # actually remove todo from todolist
        del obj.todo_data[nickname][index]
        obj.send("Item #" + str(index) + " removed.")

        if len(obj.todo_data[nickname]) == 0:
            del obj.time_data[nickname]
            del obj.todo_data[nickname]
        else:
            obj.prolong_user(nickname)
