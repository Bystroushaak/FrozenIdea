#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""

by Bystroushaak (bystrousak@kitakitsune.org
"""
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import socket


#= Variables ==================================================================
ENDL = "\r\n"


#= Functions & objects ========================================================
class QuitException()
class FrozenIdea2:
	"""
	"""
	def __init__(self, nickname, server, port):
		self.nickname = nickname
		self.real_name = "FrozenIdea2 IRC bot"
		self.server = server
		self.port = port

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self._connect()

	def _connect(self):
		self.socket.connect((self.server, int(self.port)))
		self.socket.setblocking(0)

	def _socket_send_line(self, line):
		if not line.endswith(ENDL):
			line += ENDL

		self.socket.send(str(line))

	def _join(self, chan):
		if not chan.endswith("#"):
			chan = "#" + chan

		self._socket_send_line("JOIN " + chan)

	def _rename(self, new_name):
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

	def on_message_to_bad_chan(chan):
		raise ValueError("Bot is not joined in '%s'!") % (chan)



#= Main program ===============================================================
if __name__ == '__main__':
	pass
