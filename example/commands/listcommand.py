#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import string


class ListCommand:
    def react(self, obj, obj_locals):
        globals().update(obj_locals)

        todos = []

        # skip listing of blank files
        if data_len == 0:
            obj.send("There is no TODO for you (yet).")
            return

        for i, line in enumerate(data):
            if msg and msg not in str(line):
                continue
            todos.append(" #" + str(i) + ": " + line)
        amount = len(todos)

        # compile output message from template string
        output = string.Template(output_template).substitute(
            number=str(amount) if amount > 0 else "no",
            s="s" if amount > 1 else "",
            match="" if msg == "" else " with match `" + str(msg) + "`",
            excl=":" if amount > 0 else "!"
        )
        obj.send(output)

        obj.send_array(nickname, todos)
        obj.prolong_user(nickname)
