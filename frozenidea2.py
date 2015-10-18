#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
FrozenIdea2 event driven IRC bot class
by  Bystroushaak (bystrousak@kitakitsune.org)
and Thyrst (https://github.com/Thyrst)
"""
# Interpreter version: python 2.7
#
# TODO
#   :irc.cyberyard.net 401 TODObot � :No such nick/channel
#   ERROR :Closing Link: TODObot[31.31.73.113] (Excess Flood)
#
# Imports =====================================================================
import socket
import select


# Variables ===================================================================
ENDL = "\r\n"


# Functions & classes =========================================================
class QuitException(Exception):
    def __init__(self, message):
        super(self, message)


class FrozenIdea2(object):
    """
    FrozenIdea2 IRC bot template class.

    This class allows you to write easily event driven IRC bots.

    Notable properties:
        .real_name -- real name irc property - shown in whois
        .part_msg  -- message shown when IRC bot is leaving the channel
        .quit_msg  -- same as .part_msg, but when quitting
        .password  -- password for irc server (not channel)
        .chans     -- dict {"chan_name": [users,]}
        .verbose   -- should the bot print all incomming messages to stdin?
                      default False

    Raise QuitException if you wish to quit.
    """
    def __init__(self, nickname, server, port):
        self.nickname = nickname
        self.server = server
        self.port = port

        self.real_name = "FrozenIdea2 IRC bot"
        self.part_msg = "Fuck it, I quit."
        self.quit_msg = self.part_msg
        self.password = ""
        self.verbose = False

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connect()
        self.chans = {}

    def _connect(self):
        """Connect socket to server"""
        self.socket.connect((self.server, int(self.port)))
        self.socket.setblocking(0)

    def _socket_send_line(self, line):
        """Send line thru socket. Adds ENDL if there is not already one."""
        if not line.endswith(ENDL):
            line += ENDL

        # lot of fun with this shit -- if you wan't to enjoy some unicode
        # errors, try sending "��"
        try:
            line = bytes(line)
        except UnicodeEncodeError:
            line = bytearray(line, "ascii", "ignore")

        self.socket.send(line)

    def join(self, chan):
        """Join channel. Adds # before `chan`, if there is not already one."""
        if not chan.startswith("#"):
            chan = "#" + chan

        self._socket_send_line("JOIN " + chan)

    def rename(self, new_name):
        """Change .nickname to `new_name`."""
        if self.nickname != new_name:
            self.nickname = new_name
            self._socket_send_line("NICK " + new_name)

    def nickname_used(self, nickname):
        """Callback when `new_name` is already in use."""
        self.nickname = nickname

    def send_msg(self, to, msg, msg_type=0):
        """
        Send message to given user or channel.

        Args:
            to (str): User or channel.
            msg (str): Message.
            msg_type (int, default 0): Type of the message. `0` for normal
                     message, `1` for action message or `2` for notice.
        """
        line = [
            "PRIVMSG %s :%s" % (to, msg),
            "PRIVMSG %s :\x01ACTION %s\x01" % (to, msg),
            "NOTICE %s :%s" % (to, msg),
        ]

        try:
            line = line[int(msg_type)]
        except IndexError:
            line = "PRIVMSG " + to + " :" + msg

        self._socket_send_line(line)

    def send_array(self, to, array):
        """Send list of messages from `array` to `to`."""
        for line in array:
            self.send_msg(to, line)

    def part(self, chan, msg=None):
        """Leave channel `chan`. Show .part_msg if set."""
        if msg is None:
            msg = self.part_msg

        if self.verbose:
            print "---", chan

        self._socket_send_line("PART " + chan + " :" + str(msg))

    def quit(self):
        """Leave all channels and close connection. Show .quit_msg if set."""
        self._socket_send_line("QUIT :" + self.quit_msg)
        self.socket.close()

    def run(self):
        """
        Run the ._really_run() method and check it for errors to ensure clean
        quit.
        """
        try:
            self._really_run()

        except KeyboardInterrupt:
            self.on_quit()
            self.quit()
            return

        finally:
            self.on_quit()
            self.quit()
            raise

    def _really_run(self):
        """
        Lowlevel socekt operations.

        Read data from socket, join them into messages, react to pings and so
        on.
        """
        # check server password
        if self.password != "":
            self._socket_send_line("PASS " + self.password)

        # identify to server
        self._socket_send_line(
            "USER " + self.nickname + " 0 0 :" + self.real_name
        )
        self._socket_send_line("NICK " + self.nickname)

        msg_queue = ""
        while True:
            # select read doesn't consume that much resources from server
            ready_to_read, ready_to_write, in_error = select.select(
                [self.socket],
                [],
                [],
                60
            )

            # timeouted, call .on_select_timeout()
            if not ready_to_read:
                self.on_select_timeout()
                continue

            # read 4096B from the server
            msg_queue += self.socket.recv(4096)

            # whole message doesn't arrived yet
            if ENDL not in msg_queue:
                continue

            # get arrived messages
            splitted = msg_queue.split(ENDL)
            msgs = splitted[:-1]  # all fully parsed messages
            msg_queue = splitted[-1]  # last one may not be whole

            for msg in msgs:
                msg = bytes(msg)
                if self.verbose:
                    print msg.strip()

                if msg.startswith("PING"):  # react o ping
                    ping_val = msg.split()[1].strip()
                    self._socket_send_line("PONG " + ping_val)
                    self.on_ping(ping_val)
                    continue

                try:
                    self._logic(msg)
                except QuitException:
                    self.on_quit()
                    self.quit()
                    return

    def _parse_msg(self, msg):
        """
        Get from who is the `msg`, which type it is and it's body.

        Returns tuple (from, type, msg_body).
        """
        msg = msg[1:]  # remove : from the beggining

        nickname, msg = msg.split(" ", 1)
        if ":" in msg:
            msg_type, msg = msg.split(":", 1)
        else:
            msg_type = msg.strip()
            msg = ""

        return nickname.strip(), msg_type.strip(), msg.strip()  # TODO: namedtuple

    def _logic(self, msg):
        """
        React to messages of given type. This is what calls event callbacks.
        """
        nickname, msg_type, msg = self._parse_msg(msg)

        # end of motd
        if msg_type.startswith("376"):
            self.on_server_connected()

        # end of motd
        elif msg_type.startswith("422"):
            self.on_server_connected()

        # nickname already in use
        elif msg_type.startswith("433"):
            nickname = msg_type.split(" ", 2)[1]
            self.nickname_used(nickname)

        # nick list
        elif msg_type.startswith("353"):
            chan_name = "#" + msg_type.split("#")[-1].strip()

            new_chan = True
            if chan_name in self.chans:
                del self.chans[chan_name]
                new_chan = False

            # get list of nicks, remove chan statuses (op/halfop/..)
            msg = map(
                lambda nick: nick if nick[0] not in "&@%+" else nick[1:],
                msg.split()
            )

            self.chans[chan_name] = msg

            if new_chan:
                self.on_joined_to_chan(chan_name)

        # PM or chan message
        elif msg_type.startswith("PRIVMSG"):
            nick, hostname = nickname.split("!", 1)

            if nick == self.nickname:
                return

            # channel message
            if "#" in msg_type:
                msg_type = msg_type.split()[-1]

                if msg.startswith("\x01ACTION"):
                    msg = msg.split("\x01ACTION", 1)[1].strip().strip("\x01")
                    self.on_channel_action_message(
                        msg_type,
                        nick,
                        hostname,
                        msg
                    )
                    return

                self.on_channel_message(
                    msg_type,
                    nick,
                    hostname,
                    msg
                )
                return

            # pm msg
            if not msg.startswith("\x01ACTION"):
                self.on_private_message(nick, hostname, msg)
                return

            # pm action message
            msg = msg.split("\x01ACTION", 1)[1].strip().strip("\x01")
            self.on_private_action_message(nick, hostname, msg)

        # kicked from chan
        elif msg_type.startswith("404") or msg_type.startswith("KICK"):
            msg_type = msg_type.split()
            chan_name = msg_type[1]
            who = msg_type[2]
            msg = msg.split(":")[0]  # TODO: parse kick message

            if who == self.nickname:
                self.on_kick(chan_name, msg)
                del self.chans[chan_name]
            else:
                if msg in self.chans[chan_name]:
                    self.chans[chan_name].remove(msg)
                self.on_somebody_kicked(chan_name, who, msg)

        # somebody joined channel
        elif msg_type.startswith("JOIN"):
            nick = nickname.split("!")[0].strip()
            try:
                chan_name = msg_type.split()[1].strip()
            except IndexError:
                chan_name = msg

            if nick != self.nickname:
                if nick not in self.chans[chan_name]:
                    self.chans[chan_name].append(nick)
                    self.on_somebody_joined_chan(chan_name, nick)

        # user renamed
        elif msg_type == "NICK":
            old_nick = nickname.split("!")[0].strip()

            for chan in self.chans.keys():
                if old_nick in self.chans[chan]:
                    self.chans[chan].remove(old_nick)
                    self.chans[chan].append(msg)

            self.on_user_renamed(old_nick, msg)

        # user leaved the channel
        elif msg_type.startswith("PART"):
            chan = msg_type.split()[-1]
            nick = nickname.split("!")[0].strip()

            if nick in self.chans[chan]:
                self.chans[chan].remove(nick)

            self.on_somebody_leaved(chan, nick)

        # user quit the server
        elif msg_type.startswith("QUIT"):
            nick = nickname.split("!")[0].strip()

            for chan in self.chans.keys():
                if nick in self.chans[chan]:
                    self.chans[chan].remove(nick)

            self.on_somebody_quit(nick)

    def on_server_connected(self):
        """
        Called when bot is successfully connected to server.

        It is good idea to put here .join() call.
        """
        pass

    def on_joined_to_chan(self, chan_name):
        """Called when the bot has successfully joined the channel."""
        pass

    def on_somebody_joined_chan(self, chan_name, nick):
        """Called when somebody joined the channel you are in."""
        pass

    def on_channel_message(self, chan_name, nickname, hostname, msg):
        """
        Called when somebody posted message to a channel you are in.

        chan_name -- name of the channel (starts with #)
        nickname -- name of the origin of the message
        hostname -- users hostname - IP address usually
        msg -- users message
        """
        pass

    def on_private_message(self, nickname, hostname, msg):
        """
        Called when somebody send you private message.

        nickname -- name of the origin of the message
        hostname -- users hostname - IP address usually
        msg -- users message
        """
        pass

    def on_channel_action_message(self, chan_name, nickname, hostname, msg):
        """Called for channel message with action."""
        pass

    def on_private_action_message(self, nickname, hostname, msg):
        """Called for private message with action."""
        pass

    def on_user_renamed(self, old_nick, new_nick):
        """
        Called when user renamed himself.

        See .chans property, where user nicknames are tracked and stored.
        """
        pass

    def on_kick(self, chan_name, who):
        """
        Called when somebody kicks you from the channel.

        who -- who kicked you
        """
        pass

    def on_somebody_kicked(self, chan_name, who, kicked_user):
        """
        Called when somebody kick someone from `chan_name`.

        who -- who kicked `kicked_user`
        kicked_user -- person who was kicked from chan
        """
        pass

    def on_somebody_leaved(self, chan_name, nick):
        """Called when somebody leaves the channel."""
        pass

    def on_somebody_quit(self, nick):
        """Called when somebody leaves the server."""
        pass

    def on_select_timeout(self):
        """
        Called every 60s if nothing else is happening on the socket.

        This can be usefull source of event ticks.

        PS: Ping from server IS considered as something.
        """
        pass

    def on_ping(self, ping_val):
        """
        Called when the server sends PING to the bot. PONG is automatically
        sent back.
        """
        pass

    def on_quit(self):
        """
        Called when the bot is quitiing the server. Here should be your code
        which takes care of everything you need to do.
        """
        pass
