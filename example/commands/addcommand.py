#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from __init__ import MAX_DATA


# Command definition ==========================================================
class AddCommand:
    def react(self, obj, info):
        if info.msg == "":
            obj.send("Your TODO message is blank!")
            return

        if info.nickname in obj.todo_data:
            if len(obj.todo_data[info.nickname]) > MAX_DATA:
                obj.send("You can have only " + str(MAX_DATA) + " items!")
                return
            obj.todo_data[info.nickname].append(info.msg)
        else:
            obj.todo_data[info.nickname] = [info.msg]

        obj.send("TODO updated.")
        obj.prolong_user(info.nickname)
