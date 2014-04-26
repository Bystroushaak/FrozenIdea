#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import os


class HelpCommand:
    def react(self, obj, obj_locals):
        globals().update(obj_locals)

        if not os.path.exists(HELP_FILE):
            obj.send("Help file '" + HELP_FILE + "' doesn't exits.")
            obj.send("Please, contact owner of this bot.")
            return

        with open(HELP_FILE) as f:
            obj.send_array(nickname, f.read().splitlines())
