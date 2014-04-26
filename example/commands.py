#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import string
import os.path


#= Variables ==================================================================
HELP_FILE = "help.txt"


#= Functions & objects ========================================================
class CommandPattern(object):
    def react(self, obj, obj_locals):
        globals().update(obj_locals)

        self.run_command(obj)

    def run_command(self, obj):
        pass


class ListCommand(CommandPattern):
    def run_command(self, obj):
        todos = []

        # skip listing of blank files
        if data_len == 0:
            obj.send("There is no TODO for you (yet).")
            return

        for i, line in enumerate(data):
            if msg != "" and msg not in line:
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


class AddCommand(CommandPattern):
    def run_command(self, obj):
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


class RemoveCommand(CommandPattern):
    def run_command(self, obj):
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


class HelpCommand(CommandPattern):
    def run_command(self, obj):
        if not os.path.exists(HELP_FILE):
            obj.send("Help file '" + HELP_FILE + "' doesn't exits.")
            obj.send("Please, contact owner of this bot.")
            return

        with open(HELP_FILE) as f:
            obj.send_array(nickname, f.read().splitlines())


class SeeDiffCommand(CommandPattern):
    def run_command(self, obj):
        if nickname not in obj.diff_data:
            obj.send(
                "You didn't set your own time diff. Using default " +
                str(TIME_DIFF) + "s."
            )
        else:
            obj.send(
                "Your time diff is set to %ds." % obj.diff_data[nickname]
            )



class SetDiffCommand(CommandPattern):
    def run_command(self, obj):
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
