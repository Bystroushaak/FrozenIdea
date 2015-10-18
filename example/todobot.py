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
# Imports =====================================================================
import os
import json
import time
import os.path
import argparse

from frozenidea2 import FrozenIdea2

from commands import TIME_DIFF
from commands.state_info import StateInfo

from commands.addcommand import add_command
from commands.listcommand import list_command
from commands.removecommand import remove_command
from commands.helpcommand import help_command
from commands.seediffcommand import see_diff_command
from commands.setdiffcommand import set_diff_command


# Variables ===================================================================
DATA_FILE = "todo_data.json"
UNKNOWN_COMMAND = "Unknown command or bad syntax! Type 'help' for help."


# Functions & objects =========================================================
class TODObot(FrozenIdea2):
    def __init__(self, nickname, chans, server, port=6667):
        super(TODObot, self).__init__(nickname, server, port)
        self.channels = chans
        self.read_data_file()

        def rm_and_list(*args, **kwargs):
            remove_command(*args, **kwargs)
            list_command(*args, **kwargs)

        self.valid_commands = {
            "list": list_command,
            "ls": list_command,
            "la": list_command,
            "add": add_command,
            "remove": remove_command,
            "rm": rm_and_list,
            "help": help_command,
            "see_diff": see_diff_command,
            "see": see_diff_command,
            "set_diff": set_diff_command,
            "set": set_diff_command,
        }

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
        elif type(self.channels) in [tuple, list]:
            for chan in self.channels:
                self.join(chan)

    def on_channel_message(self, chan_name, nickname, hostname, msg):
        """React to messages posted to channel."""
        # message for bot
        if msg.startswith(self.nickname + ": "):
            msg = msg.split(" ", 1)[1]
            self.react_to_message(chan_name, nickname, msg)
            return

        # event for ticker
        self.react_to_anything()

    def on_private_message(self, nickname, hostname, msg):
        """React to messages posted to PM."""
        self.react_to_message(nickname, nickname, msg)


    # react_to_anything() callback block
    def on_somebody_leaved(self, chan_name, nick):
        self.react_to_anything()
    def on_somebody_joined_chan(self, chan_name, nick):
        self.react_to_anything()
    def on_channel_join(self, chan_name):
        self.react_to_anything()
    def on_select_timeout(self):
        self.react_to_anything()

    def on_kick(self, chan_name, who):
        time.sleep(1)
        self.join(self.chan)

    def prolong_user(self, username):
        """
        Don't bother user for some time defined in TIME_DIFF.
        """
        self.time_data[username] = time.time()

    def react_to_anything(self):
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

        # state info for command classes
        info = StateInfo()
        info.chan = chan
        info.nickname = nickname
        info.private_message = (chan == nickname)
        info.command, info.msg = self._parse_commands(msg)

        if info.command not in self.valid_commands:
            self.send(UNKNOWN_COMMAND)
            return

        # read data
        info.data = self.todo_data.get(nickname, [])
        info.data_len = len(info.data)

        # do the command
        self.valid_commands[info.command](self, info)

        # save the state
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


# Main program ================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='IRC TODObot')
    parser.add_argument(
        "-s",
        '--server',
        type=str,
        help='Address of the IRC server.'
    )
    parser.add_argument(
        "-p",
        '--port',
        type=int,
        default=6667,
        help='Port of the IRC server. Default 6667.'
    )
    parser.add_argument(
        "-n",
        '--nick',
        type=str,
        default="TODObot",
        help="Bot's nick. Default 'TODObot'."
    )
    parser.add_argument(
        'channels',
        metavar='CHANNEL',
        type=str,
        nargs='+',
        help='List of channels for bot to join. With or without #.'
    )
    args = parser.parse_args()

    bot = TODObot(args.nick, args.channels, args.server, args.port)
    bot.verbose = True

    try:
        bot.run()
    except KeyboardInterrupt:
        print "Clean exit."
