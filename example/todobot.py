#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple TODO IRC bot
by Bystroushaak (bystrousak@kitakitsune.org)
"""
# Interpreter version: python 2.7
# This work is licensed under a Creative Commons 3.0 Unported License
# (http://creativecommons.org/licenses/by/3.0/).
#
#= Imports ====================================================================
import os
import json
import time
import string
import os.path

from frozenidea2 import FrozenIdea2


#= Variables ==================================================================
MAX_DATA = 25
MIN_TIME_DIFF = 60
TIME_DIFF = 60 * 60  # 1 hour
POKE_DIFF = 5 * 60
DATA_FILE = "todo_data.json"
HELP_FILE = "help.txt"
UNKNOWN_COMMAND = "Unknown command or bad syntax! Type 'help' for help."


#= Functions & objects ========================================================
class TODObot(FrozenIdea2):
    def __init__(self, nickname, chans, server, port=6667):
        super(TODObot, self).__init__(nickname, server, port)
        self.channels = chans
        self.poking = False # poking feature - default off
        self.read_data_file()

    def on_quit(self):
        """
        Don't forget to save data on quit.

        Data are also saved periodically after each change.
        """
        self.save_data_file()

    def on_server_connected(self):
        """
        Join proper channels.
        """
        self._socket_send_line("MODE " + self.nickname + " +B")
        if type(self.channels) is str:
            self.join(self.channels)
        elif type(self.channels) is tuple:
            for chan in self.channels:
                self.join(chan)

    def on_channel_message(self, chan_name, nickname, hostname, msg):
        """React to messages posted to channel."""
        if msg.startswith(self.nickname + ": "):  # message for bot
            msg = msg.split(" ", 1)[1]
            self.react_to_message(chan_name, nickname, msg)
        else:                              # event for ticker
            self.react_to_anything(chan_name)

    def on_private_message(self, nickname, hostname, msg):
        """React to messages posted to PM."""
        self.react_to_message(nickname, nickname, msg)


    # react_to_anything() callback block
    def on_somebody_leaved(self, chan_name, nick):
        self.react_to_anything(chan_name)
    def on_somebody_joined_chan(self, chan_name, nick):
        self.react_to_anything(chan_name)
    def on_channel_join(self, chan_name):
        self.react_to_anything(chan_name)
    def on_select_timeout(self):
        self.react_to_anything(chan_name)

    def on_kick(self, chan_name, who):
        time.sleep(1)
        self.join(self.chan)


    def prolong_user(self, username):
        """
        Don't bother user for some time defined in TIME_DIFF.
        """
        self.time_data[username] = time.time()

    def react_to_anything(self, chan_name):
        """
        Called when certain events occurs:
            .on_somebody_leaved()
            .on_somebody_joined_chan()
            .on_channel_join()
            .on_channel_message()

        Used as ticker, to be able to send user warning about their TODO list
        after some time.
        """
        if self.time_data == {} or self.todo_data == {}:
            return

        # check which users have their TODO ready and warn them
        for username in self.time_data.keys():
            # skip users, which are not in any channel (this prevents bot from
            # posting to usernames, which are currently offline)
            present_usernames = set(sum(self.chans.values(), []))
            if username not in present_usernames:
                continue

            timestamp = int(self.time_data[username])

            # allow users to set their own diff
            diff = TIME_DIFF
            if username in self.diff_data:
                diff = self.diff_data[username]

            if timestamp < time.time() - diff:
                self.zapicuj(username)

    def zapicuj(self, username):
        """
        Send user information about their TODO after some time (see TIME_DIFF).
        """
        num = len(self.todo_data[username])
        self.send_msg(
            username,
            "You have " + str(num) +
            " item" +
            ("s" if num > 1 else "") +
            " on your TODO list. For listing, type 'list'."
        )
        self.prolong_user(username)

    def _parse_commands(self, message):
        """
        Parse `message` into command and message.

        Returns (command, message) tuple.
        """
        message = message.strip()

        if " " in message:
            return message.split(" ", 1)
        else:
            return message, ""

    def send(self, msg):
        """
        .send_msg() wrapper to save some effort and space by automatically
        choosing .msg_to as person to who will be `msg` delivered.

        Used only in .react_to_message().
        """
        self.send_msg(self.msg_to, msg)

    def react_to_message(self, chan, nickname, msg):
        """
        React to user's message send to the bot.

        chan -- message's origin - name of the channel or user's nick in case
                 that message was sent as PM
        nickname -- always name of user which sent the message, no matter of
                     the origin of the message
        msg -- string message
        """
        self.msg_to = nickname  # this is saved for .send()
        msg = msg.strip().replace("\n", "")
        private_message = True if chan == nickname else False
        output_template = "You have $number TODO$s on your TODO list$match$excl"

        commands = ["list", "add", "remove", "help", "set_diff", "see_diff", "poke"]
        command, msg = self._parse_commands(msg)

        if command not in commands:
            self.send(UNKNOWN_COMMAND)
            return

        if command == "help":
            if not os.path.exists(HELP_FILE):
                self.send("Help file '" + HELP_FILE + "' doesn't exits.")
                self.send("Please, contact owner of this bot.")
                return

            with open(HELP_FILE) as f:
                self.send_array(nickname, f.read().splitlines())

            return

        if command == "see_diff":
            if nickname not in self.diff_data:
                self.send(
                    "You didn't set your own time diff. Using default " +
                    str(TIME_DIFF) + "s."
                )
            else:
                self.send(
                    "Your time diff is set to %ds." % self.diff_data[nickname]
                )
            return

        # read data
        data = self.todo_data.get(nickname, [])
        data_len = len(data)

        if command == "set_diff":
            if msg == "":
                self.send("`set_diff` expects one parameter!")
                return

            # convert commands parameter to number
            index = -1
            try:
                index = int(msg)
            except ValueError:
                self.send("`set_diff` command expects one integer parameter!")
                return

            if index <= 0:
                self.send("Time diff have to be positive number.")
                return

            if index < MIN_TIME_DIFF:
                self.send(
                    "Min. time diff: " + str(MIN_TIME_DIFF) +
                    ". Leaving unchanged."
                )
                return

            self.diff_data[nickname] = index
            self.send("Time diff updated.")

        # react to `list` command
        elif command == "list":
            todos = []

            # skip listing of blank files
            if data_len == 0:
                self.send("There is no TODO for you (yet).")
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
            self.send(output)

            self.send_array(nickname, todos)
            self.prolong_user(nickname)

        # react to `add` command
        elif command == "add":
            if msg == "":
                self.send("Your TODO message is blank!")
                return

            if nickname in self.todo_data:
                if len(self.todo_data[nickname]) > MAX_DATA:
                    self.send("You can have only " + str(MAX_DATA) + " items!")
                    return
                self.todo_data[nickname].append(msg)
            else:
                self.todo_data[nickname] = [msg]

            self.send("TODO updated.")
            self.prolong_user(nickname)

        # react to `remove` command
        elif command == "remove":
            if data_len == 0:
                self.send("There is no TODO for you (yet).")
                return

            if msg == "":
                self.send("`remove` expects index parameter!")
                return

            if msg == "*":
                del self.time_data[nickname]
                del self.todo_data[nickname]
                self.send("All data removed.")
                return

            # convert commands parameter to number
            index = -1
            try:
                index = int(msg)
            except ValueError:
                self.send("`remove` command expects integer parameter!")
                return

            # check range of `remove` parameter
            if index < 0 or index >= data_len:
                self.send("Bad index!")
                return

            # actually remove todo from todolist
            del self.todo_data[nickname][index]
            self.send("Item #" + str(index) + " removed.")

            if len(self.todo_data[nickname]) == 0:
                del self.time_data[nickname]
                del self.todo_data[nickname]
            else:
                self.prolong_user(nickname)

        # react to `poke` command if is poke feature on
        elif command == "poke":
            if self.poking:
                if msg == "":
                    self.send("`poke` command expects nick of user to poke.")
                    return

                nick = msg.split(" ", 1)[0].strip()
                if nick in self.time_data and nick in self.todo_data and len(self.todo_data[nick]) > 0:
                    if int(self.time_data[nick]) < time.time() - POKE_DIFF:
                        self.send_msg(nick, nickname + " want you to do somthing! Check your TODOs with `list`.")
                        self.send(nick + " poked.")
                        self.prolong_user(nick)
                    else:
                        self.send("This user has been poked a little time ago. Let him be.")
                else:
                    self.send("Sorry, this user has no TODOs in my database.")
            else:
                self.send("Sorry, `poke` command is disabled.")

        self.save_data_file()


    def read_data_file(self):
        """
        Read data from DATA_FILE, save them into properties .time_data and
        .todo_data (both dicts).
        """
        data = {}
        if os.path.exists(DATA_FILE):
            data = json.load(open(DATA_FILE))

        self.time_data = data.get("time", {})
        self.todo_data = data.get("todo", {})
        self.diff_data = data.get("diff", {})

    def save_data_file(self):
        """
        Save data from .time_data and .todo_data dicts to JSON.
        """
        data = {
            "time": self.time_data,
            "todo": self.todo_data,
            "diff": self.diff_data
        }
        json.dump(data, open(DATA_FILE, "wt"), encoding="unicode_escape")


#= Main program ===============================================================
if __name__ == '__main__':
    bot = TODObot("TODObot", ("#c0r3", "#bots"), "xexexe.cyberyard.net", 6667)
    # bot = TODObot("todobotXXX", "#freedom99", "madjack.2600.net", 6667)
    bot.verbose = True
    bot.poking = True

    bot.run()
