#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
FrozenIdea2 event driven IRC bot class
by  Bystroushaak (bystrousak@kitakitsune.org)
and Thyrst (https://github.com/Thyrstv)
"""
# Interpreter version: python 2.7
#
# TODO
#   ACTION callbacky
#   :irc.cyberyard.net 401 TODObot � :No such nick/channel
#   ERROR :Closing Link: TODObot[31.31.73.113] (Excess Flood)
#
#= Imports ====================================================================
import socket
import select


#= Variables ==================================================================
ENDL = "\r\n"


#= Functions & objects ========================================================
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
        if not self.nickname is new_name:
            self.nickname = new_name
            self._socket_send_line("NICK " + new_name)

    def nickname_used(self, nickname):
        """Callback for `new_name` already in use"""
        self.nickname = nickname

    def send_msg(self, to, msg):
        """Send `msg` to `to`. `to` can be user or channel."""
        self._socket_send_line("PRIVMSG " + to + " :" + msg)

    def send_array(self, to, array):
        """Send list of messages from `array` to `to`."""
        for line in array:
            self.send_msg(to, str(line))

    def part(self, chan, msg = ""):
        """Leave channel `chan`. Show .part_msg if set."""
        if (msg == ""):
            msg = self.part_msg
        print "---", chan
        self._socket_send_line("PART " + chan + " :" + msg)

    def quit(self):
        """Leave all channels and close connection. Show .quit_msg if set."""
        self._socket_send_line("QUIT :" + self.quit_msg)
        self.socket.close()

    def run(self):
        """
        Run the ._really_run() method and wrap check it for errors to ensure
        clean quit.
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
            _ = msg_queue.split(ENDL)
            msgs = _[:-1]
            msg_queue = _[-1]

            for msg in msgs:
                msg = bytes(msg)
                if self.verbose:
                    print msg.strip()

                if msg.startswith("PING"):  # react o ping
                    ping_val = msg.split()[1].strip()
                    self._socket_send_line("PONG " + ping_val)
                    self.on_ping(ping_val)
                else:
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
            type_, msg = msg.split(":", 1)
        else:
            type_ = msg.strip()
            msg = ""

        return nickname.strip(), type_.strip(), msg.strip()

    def _logic(self, msg):
        """
        React to messages of given type. Here is what calls event callbacks.
        """
        nickname, type_, msg = self._parse_msg(msg)

        # end of motd
        if type_.startswith("376"):
            self.on_server_connected()

        # end of motd
        elif type_.startswith("422"):
            self.on_server_connected()

        # nickname already in use
        elif type_.startswith("433"):
            nickname = type_.split(" ", 2)[1]
            self.nickname_used(nickname)

        # nick list
        elif type_.startswith("353"):
            chan_name = "#" + type_.split("#")[-1].strip()

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
        elif type_.startswith("PRIVMSG"):
            nick, hostname = nickname.split("!", 1)

            if nick == self.nickname:
                return

            if "#" in type_:
                self.on_channel_message(type_.split()[-1], nick, hostname, msg)
            else:
                self.on_private_message(nick, hostname, msg)

        # kicked from chan
        elif type_.startswith("404") or type_.startswith("KICK"):
            type_ = type_.split()
            chan_name = type_[1]
            who = type_[2]
            msg = msg.split(":")[0]  # TODO: parse kick message

            if who == self.nickname:
                self.on_kick(chan_name, msg)
                del self.chans[chan_name]
            else:
                if msg in self.chans[chan_name]:
                    self.chans[chan_name].remove(msg)
                self.on_somebody_kicked(chan_name, who, msg)

        # somebody joined channel
        elif type_.startswith("JOIN"):
            nick = nickname.split("!")[0].strip()
            chan_name = type_.split()[1].strip()

            if nick != self.nickname:
                if nick not in self.chans[chan_name]:
                    self.chans[chan_name].append(nick)
                    self.on_somebody_joined_chan(chan_name, nick)

        # user renamed
        elif type_ == "NICK":
            old_nick = nickname.split("!")[0].strip()

            for chan in self.chans.keys():
                if old_nick in self.chans[chan]:
                    self.chans[chan].remove(old_nick)
                    self.chans[chan].append(msg)

            self.on_user_renamed(old_nick, msg)

        # user leaved the channel
        elif type_.startswith("PART"):
            chan = type_.split()[-1]
            nick = nickname.split("!")[0].strip()

            if nick in self.chans[chan]:
                self.chans[chan].remove(nick)

            self.on_somebody_leaved(chan, nick)

        # user quit the server
        elif type_.startswith("QUIT"):
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


#= Main program ===============================================================
if __name__ == '__main__':
    class Xex(FrozenIdea2):
        def __init__(self, nickname, chan, server, port=6667):
            super(Xex, self).__init__(nickname, server, port)
            self.chan = chan

        def on_server_connected(self):
            self.join(self.chan)

        def on_channel_message(self, chan_name, nickname, hostname, msg):
            print self.chans
            print "To:", chan_name
            print "From:", nickname
            print "Msg:", msg
            print

    x = Xex("xexasdasd", "#freedom99", "madjack.2600.net", 6667)
    x.verbose = True
    x.run()
