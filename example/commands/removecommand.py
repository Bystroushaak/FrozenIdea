#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#


# Command definition ==========================================================
class RemoveCommand:
    def react(self, obj, info):
        if info.data_len == 0:
            obj.send("There is no TODO for you (yet).")
            return

        if info.msg == "":
            obj.send("`remove` expects index parameter!")
            return

        if info.msg == "*":
            del obj.time_data[info.nickname]
            del obj.todo_data[info.nickname]
            obj.send("All data removed.")
            return

        # convert commands parameter to number
        index = -1
        try:
            index = int(info.msg)
        except ValueError:
            obj.send("`remove` commandPattern expects integer parameter!")
            return

        # check range of `remove` parameter
        if index < 0 or index >= info.data_len:
            obj.send("Bad index!")
            return

        # actually remove todo from todolist
        del obj.todo_data[info.nickname][index]
        obj.send("Item #" + str(index) + " removed.")

        if len(obj.todo_data[info.nickname]) == 0:
            del obj.time_data[info.nickname]
            del obj.todo_data[info.nickname]
        else:
            obj.prolong_user(info.nickname)
