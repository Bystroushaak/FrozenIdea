#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""

by Bystroushaak (bystrousak@kitakitsune.org
"""
# Interpreter version: python 2.7
# This work is licensed under a Creative Commons 3.0 Unported License
# (http://creativecommons.org/licenses/by/3.0/).
#
#= Imports ====================================================================
import os
import os.path
import sys
import time
import random

from frozenidea2 import FrozenIdea2


#= Variables ==================================================================
TODO_LIST_DIR = "todos/"  # / at the end is important
HELP = "help.txt"
TIME_FILE = "times.txt"
TIME_DIFF = 60 * 60  # 1 hour
UNKNOWN_COMMAND = "Unknown command or bad syntax! Type 'help' for help. Seed: "

# make sure, that directory exists
if not os.path.exists(TODO_LIST_DIR):
    os.mkdir(TODO_LIST_DIR)


#= Functions & objects ========================================================
class TODObot(FrozenIdea2):
    def __init__(self, nickname, chan, server, port=6667):
        super(TODObot, self).__init__(nickname, server, port)
        self.chan = chan

        self.time_data = {}
        if os.path.exists(TIME_FILE):
            with open(TIME_FILE) as f:
                self.time_data = map(
                    lambda x: x.split(" ", 1),
                    f.read().splitlines()
                )
                self.time_data = dict(self.time_data)

    def on_server_connected(self):
        self.join(self.chan)

    def on_channel_message(self, chan_name, from_, hostname, msg):
        if msg.startswith(self.nickname):
            msg = msg.split(" ", 1)[1]
            self.react_to_message(chan_name, from_, msg)
        else:
            self.react_to_anything(chan_name)

    def on_private_message(self, from_, hostname, msg):
        self.react_to_message(from_, from_, msg)


    def on_somebody_leaved(self, chan_name, nick):
        self.react_to_anything(chan_name)

    def on_somebody_joined_chan(self, chan_name, nick):
        self.react_to_anything(chan_name)

    def on_channel_join(self, chan_name):
        self.react_to_anything(chan_name)

    def react_to_anything(self, chan_name):
        if self.time_data == {}:
            return

        for username in self.time_data.keys():
            timestamp = int(self.time_data[username])
            act_time = int(time.time())

            if timestamp < act_time - TIME_DIFF:
                self.zapicuj(username)
                self.time_data[username] = act_time + TIME_DIFF

    def zapicuj(self, username):
        self.send_msg(
            username,
            "You have items on your TODO list. For listing, type 'list'."
        )

    def on_quit(self):
        out = []
        for username in self.time_data.keys():
            out.append(username + " " + str(self.time_data[username]))

        with open(TIME_FILE, "wt") as f:
            f.write("\n".join(out))

    def _get_filename(self, nick):
        safe_nick = nick.replace(".", "").replace("/", "")
        filename = TODO_LIST_DIR + safe_nick

        return filename

    def _read_user_file(self, nick):
        filename = self._get_filename(nick)

        # read data from file
        data = []
        if os.path.exists(filename):
            with open(filename) as f:
                data = f.read().splitlines()

        return data

    def react_to_message(self, from_, from_nick, msg):
        msg = msg.strip()
        filename = self._get_filename(from_nick)
        commands = ["list", "add", "remove", "help"]

        # print help
        if msg == "help":
            if not os.path.exists(HELP):
                sys.stderr.write("Help file '%s' doesn't exits!") % (HELP)
                return

            with open(HELP) as f:
                self.send_array(from_nick, f.read().splitlines())

            return

        # skip commands without parameters other than `list`
        if " " not in msg and msg != "list":
            self.send_msg(from_, UNKNOWN_COMMAND + str(random.randint(1, 100000)))
            return

        # list is only command without parameter
        command = ""
        if msg.startswith("list"):
            command = "list"
        else:
            command, msg = msg.split(" ", 1)

            # normalize data
            msg = msg.strip()
            command = command.lower().replace("\n", "")

        # skip unknown commands
        if command not in commands:
            self.send_msg(from_, UNKNOWN_COMMAND + str(random.randint(1, 100000)))
            return

        # skip listing of blank files
        if command == "list" and (not os.path.exists(filename)):
            self.send_msg(
                from_nick,
                "There is no TODO for you (yet)."
            )
            return

        data = self._read_user_file(from_nick)

        # react to `list` command
        if command == "list":
            output = "You have " + str(len(data)) if len(data) > 0 else "no"
            output += " TODO on your TODO list"
            output += ":" if len(data) > 0 else "!"

            self.send_msg(from_nick, output)

            if len(data) == 0:
                return

            for i, line in enumerate(data):
                    self.send_msg(from_nick, str(i) + "; " + line)

            self.time_data[from_nick] = int(time.time()) + TIME_DIFF

        # react to `add` command
        elif command == "add":
            if msg == "":
                self.send_msg(from_nick, "Your TODO is blank!")
                return

            data.append(msg)
            self.send_msg(from_nick, "TODO updated.")

            if from_nick not in self.time_data:
                self.time_data[from_nick] = int(time.time()) + TIME_DIFF

        # react to `remove` command
        elif command == "remove":
            index = -1
            try:
                index = int(msg)
            except ValueError:
                self.send_msg(from_nick, "remove expects number as parameter!")
                return

            # check range of remove
            if len(data) > index < 0:
                self.send_msg(from_nick, "Bad index!")
                return

            del data[index]
            self.send_msg(from_nick, str(index) + " removed.")

            if len(data) == 0:
                del self.time_data[from_nick]
            else:
                self.time_data[from_nick] = int(time.time()) + TIME_DIFF

        # save data
        with open(filename, "wt") as f:
            f.write("\n".join(data))








#= Main program ===============================================================
if __name__ == '__main__':
    bot = TODObot("todobotXXX", "#c0r3", "xexexe.cyberyard.net", 6667)

    bot.run()
