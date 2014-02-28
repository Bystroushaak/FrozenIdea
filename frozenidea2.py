#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""

by Bystroushaak (bystrousak@kitakitsune.org
"""
# Interpreter version: python 2.7
#
# TODO
#   partmsg pri .part()
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
    """
    def __init__(self, nickname, server, port):
        self.nickname = nickname
        self.server = server
        self.port = port

        self.real_name = "FrozenIdea2 IRC bot"
        self.part_msg = "Fuck it, I quit."
        self.password = ""

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connect()
        self.chans = {}

    def _connect(self):
        self.socket.connect((self.server, int(self.port)))
        self.socket.setblocking(0)

    def _socket_send_line(self, line):
        if not line.endswith(ENDL):
            line += ENDL

        self.socket.send(str(line))

    def join(self, chan):
        if not chan.startswith("#"):
            chan = "#" + chan

        self._socket_send_line("JOIN " + chan)

    def rename(self, new_name):
        self._socket_send_line("RENAME " + new_name)

    def send_msg(self, chan, msg):
        if chan not in self.chans:
            self.on_message_to_bad_chan(chan)

    def send_priv_msg(self, to, msg):
        self._socket_send_line("PRIVMSG " + to + " :" + msg)

    def part(self, chan):
        self._socket_send_line("PART " + chan)

    def quit(self):
        for chan in self.chans:
            self.part(chan)

        self._socket_send_line("QUIT :" + self.part_msg)
        self.socket.close()

    def run(self):
        try:
            self.really_run()
        except KeyboardInterrupt:
            self.on_quit()
            self.quit()
            return

    def really_run(self):
        if self.password != "":
            self._socket_send_line("PASS " + self.password)

        # identify to server
        self._socket_send_line(
            "USER " + self.nickname + " 0 0 :" + self.real_name
        )
        self._socket_send_line("NICK " + self.nickname)

        msg_queue = ""
        while True:

            ready_to_read, ready_to_write, in_error = select.select(
                [self.socket],
                [self.socket],
                [self.socket]
            )

            if not ready_to_read:
                continue

            # todo: add try / quiet quit
            msg_queue += self.socket.recv(4096)

            print msg_queue

            if ENDL not in msg_queue:
                continue

            _ = msg_queue.split(ENDL)
            msgs = _[:-1]
            msg_queue = _[-1]

            for msg in msgs:
                if msg.startswith("PING"):
                    self._socket_send_line("PONG " + msg.split()[1].strip())
                else:
                    try:
                        self._logic(msg)
                    except QuitException:
                        self.on_quit()
                        self.quit()
                        return

    def _parse_msg(self, msg):
        msg = msg[1:]  # remove : from the beggining

        from_, msg = msg.split(" ", 1)
        if ":" in msg:
            type_, msg = msg.split(":", 1)
        else:
            type_ = msg.strip()
            msg = ""

        return from_.strip(), type_.strip(), msg.strip()

    def _logic(self, msg):
        from_, type_, msg = self._parse_msg(msg)

        print "type_", type_

        if type_.startswith("376"):    # end of motd
            self.on_server_connected()

        elif type_.startswith("353"):  # nick list
            chan_name = type_.split("#")[-1].strip()

            new_chan = True
            if chan_name in self.chans:
                self.chans.remove(chan_name)
                new_chan = False

            # get list of nicks, remove chan statuses (op/halfop/..)
            msg = map(
                lambda nick: nick if nick[0] not in "&@%+" else nick[1:],
                msg.split()
            )

            self.chans[chan_name] = msg

            if new_chan:
                self.on_channel_join(chan_name)

        elif type_.startswith("PRIVMSG"):
            nick, hostname = from_.split("!", 1)

            if "#" in type_:
                self.on_channel_message(type_.split()[-1], nick, hostname, msg)
            else:
                self.on_private_message(type_.split()[-1], hostname, msg)

        elif type_.startswith("404"):  # kicked from chan
            chan_name = type_.split()[-1]
            self.chans.remove(chan_name)
            self.on_kick(chan_name)

        elif type_.startswith("JOIN"):
            nick = from_.split("!")[0].strip()
            chan_name = msg

            if nick != self.nickname:
                if nick not in self.chans[chan_name]:
                    self.chans[chan_name].append(nick)

                    self.on_somebody_joined_chan(chan_name, nick)

        elif type_ == "NICK":
            old_nick = from_.split("!")[0].strip()

            for chan in self.chans.keys():
                if old_nick in self.chans[chan]:
                    self.chans[chan].remove(old_nick)
                    self.chans[chan].append(msg)

            self.on_user_renamed(old_nick, msg)

        elif type_.startswith("PART"):
            chan = type_.split()[-1]
            nick = from_.split("!")[0].strip()

            if nick in self.chans[chan]:
                self.chans[chan].remove(nick)

            self.on_somebody_leaved(chan, nick)

        elif type_.startswith("QUIT"):
            nick = from_.split("!")[0].strip()

            for chan in self.chans.keys():
                if nick in self.chans[chan]:
                    self.chans[chan].remove(nick)

            self.on_somebody_quit(nick)

    def on_somebody_quit(self, nick):
        pass

    def on_somebody_leaved(self, chan, nick):
        pass

    def on_user_renamed(self, old_nick, new_nick):
        pass

    def on_somebody_joined_chan(self, chan_name, nick):
        pass

    def on_kick(self, chan_name):
        pass

    def on_channel_message(self, chan_name, from_, hostname, msg):
        pass

    def on_private_message(self, from_, hostname, msg):
        pass

    def on_channel_join(self, chan_name):
        pass

    def on_server_connected(self):
        pass

    def on_quit(self):
        pass

    def on_message_to_bad_chan(self, chan):
        raise ValueError("Bot is not joined in '%s'!") % (chan)


#= Main program ===============================================================
if __name__ == '__main__':
    class Xex(FrozenIdea2):
        def __init__(self, nickname, server, port=6667):
            super(Xex, self).__init__(nickname, server, port)

        def on_server_connected(self):
            self.join("#freedom99")

        def on_channel_message(self, chan_name, from_, hostname, msg):
            print self.chans
            print "To:", chan_name
            print "From:", from_
            print "Msg:", msg
            print


    x = Xex("xexasdasd", "madjack.2600.net", 6667)
    x.run()
