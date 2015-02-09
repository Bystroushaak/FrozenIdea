#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#


# Classes =====================================================================
class StateInfo(object):
    def __init__(self):
        self.chan = None
        self.nickname = None
        self.msg = None
        self.private_message = None
        self.command = None
        self.data = None
        self.data_len = None
