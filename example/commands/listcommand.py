#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import string


# Command definition ==========================================================
def list_command(obj, info):
    todos = []

    # skip listing of blank files
    if info.data_len == 0:
        obj.send("There is no TODO for you (yet).")
        return

    for line_cnt, line in enumerate(info.data):
        if info.msg and info.msg not in line:
            continue

        todos.append(" #%d: %s" % (line_cnt, line))

    amount = len(todos)

    # compose output message from template string
    output_templ = "You have $number TODO$s on your TODO list$match$excl"
    output = string.Template(output_templ).substitute(
        number=str(amount) if amount > 0 else "no",
        s="s" if amount > 1 else "",
        match="" if not info.msg else " with match `" + str(info.msg) + "`",
        excl=":" if amount > 0 else "!"
    )
    obj.send(output)

    obj.send_array(info.nickname, todos)
    obj.prolong_user(info.nickname)
