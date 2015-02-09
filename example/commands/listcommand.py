#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import string

from __init__ import OUTPUT_TEMPLATE


# Command definition ==========================================================
class ListCommand:
    def react(self, obj, info):
        todos = []

        # skip listing of blank files
        if info.data_len == 0:
            obj.send("There is no TODO for you (yet).")
            return

        for i, line in enumerate(info.data):
            if info.msg and info.msg not in str(line):
                continue
            todos.append(" #" + str(i) + ": " + line)
        amount = len(todos)

        # compose output message from template string
        output = string.Template(OUTPUT_TEMPLATE).substitute(
            number=str(amount) if amount > 0 else "no",
            s="s" if amount > 1 else "",
            match="" if not info.msg else " with match `" + str(info.msg) + "`",
            excl=":" if amount > 0 else "!"
        )
        obj.send(output)

        obj.send_array(info.nickname, todos)
        obj.prolong_user(info.nickname)
