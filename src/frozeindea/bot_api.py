import sys
import time
import argparse
import logging
import logging.handlers
from functools import wraps

from .frozenidea import FrozenIdea

logger = logging.getLogger("bot")


def get_rotating_logger(fn="irc.log"):
    formatter = logging.Formatter(
        "%(asctime)s %(filename)s:%(lineno)d %(funcName)s() %(levelname)s:\n%(message)s"
    )

    file_logger = logging.handlers.TimedRotatingFileHandler(
        fn, when="midnight", backupCount=5
    )
    file_logger.setFormatter(formatter)

    stderr_logger = logging.StreamHandler(sys.stderr)
    stderr_logger.setFormatter(formatter)

    logger.addHandler(file_logger)
    logger.addHandler(stderr_logger)
    logger.setLevel(logging.DEBUG)

    return logger


def once_in_n_seconds(seconds, alt_val=None):
    def once_in_n_seconds_wrapper(fn):
        last_time = [0]

        @wraps(fn)
        def once_in_n_seconds_decorator(*args, **kwargs):
            if time.time() - last_time[0] < seconds:
                return alt_val

            last_time[0] = time.time()
            return fn(*args, **kwargs)

        return once_in_n_seconds_decorator

    return once_in_n_seconds_wrapper


class BotAPI(FrozenIdea):
    def __init__(self, nickname, chans, server, port=6667, logger=logger):
        super(BotAPI, self).__init__(nickname, server, port)
        self.join_list = chans
        self.socket_timeout = 10
        self.logger = logger

    def on_channel_message(self, chan_name, nickname, hostname, msg):
        """React to messages posted to channel."""
        # message for bot
        if msg.startswith(self.nickname + ":"):
            msg = msg.split(":", 1)[1]
            self.react_to_message(chan_name, nickname, msg)
            return

        # event for ticker
        self.react_to_anything()

    def on_private_message(self, nickname, hostname, msg):
        """React to messages posted to PM."""
        self.react_to_message(nickname, nickname, msg)

    def on_joined_to_chan(self, chan):
        super(BotAPI, self).on_joined_to_chan(chan)
        self.send_update(to=chan)

    # react_to_anything() callback block
    def on_somebody_leaved(self, chan, nick):
        super(BotAPI, self).on_somebody_leaved(chan, nick)
        self.react_to_anything()

    def on_somebody_joined_chan(self, chan, nick):
        super(BotAPI, self).on_somebody_joined_chan(chan, nick)
        self.react_to_anything()

    def on_select_timeout(self):
        super(BotAPI, self).on_select_timeout()
        self.react_to_anything()

    def on_kick(self, chan, who):
        super(BotAPI, self).on_kick(chan, who)
        self.react_to_anything()

    def on_ping(self, ping_val):
        super(BotAPI, self).on_ping(ping_val)
        self.react_to_anything()

    @once_in_n_seconds(5 * 60)
    def react_to_anything(self):
        """
        Called when certain events occurs:
            .on_kick()
            .on_ping()
            .on_channel_join()
            .on_select_timeout()
            .on_somebody_leaved()
            .on_somebody_joined_chan()

        Used as ticker.
        """
        # sometimes, ping comes before the bot is joined, so don't send_update if
        # not connected to any channel
        if not self.chans:
            return

        try:
            self.send_update()
        except Exception as e:
            self.logger.exception(str(e))

    def react_to_message(self, chan, nickname, msg):
        msg = msg.strip().replace("\n", "")

        try:
            self.send_update(nickname)
        except Exception as e:
            self.logger.exception("Couldn't send update to %s: %s", nickname, str(e))
            self.send_msg(to=nickname, msg="Sorry, couldn't parse data.")

    def send_update(self, to=None):
        raise NotImplementedError()


def get_args_parser(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-s", "--server", type=str, help="Address of the IRC server.")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=6667,
        help="Port of the IRC server. Default 6667.",
    )
    parser.add_argument(
        "-n",
        "--nick",
        type=str,
        default="KoronaBot",
        help="Bot's nick. Default 'KoronaBot'.",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Be quiet.")
    parser.add_argument(
        "channels",
        metavar="CHANNEL",
        type=str,
        nargs="+",
        help="List of channels for bot to join. With or without #.",
    )

    return parser
