#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
class AddCommand:
    def react(self, obj, obj_locals):
        globals().update(obj_locals)

        if msg == "":
            obj.send("Your TODO message is blank!")
            return

        if nickname in obj.todo_data:
            if len(obj.todo_data[nickname]) > MAX_DATA:
                obj.send("You can have only " + str(MAX_DATA) + " items!")
                return
            obj.todo_data[nickname].append(msg)
        else:
            obj.todo_data[nickname] = [msg]

        obj.send("TODO updated.")
        obj.prolong_user(nickname)
