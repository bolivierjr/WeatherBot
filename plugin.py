#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2018, Bruce Olivier
# All rights reserved.

import logging
from typing import List
from .models.users import User
from supybot import utils, plugins, ircutils, callbacks, ircmsgs
from supybot.commands import wrap, optional, getopts

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("APIXUWeather")
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    def _(x):
        return x


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class WeatherBot(callbacks.Plugin):
    """A weather script that uses APIXU's api.
    """

    threaded = True

    def createdb(
        self,
        irc: callbacks.NestedCommandsIrcProxy,
        msg: ircmsgs.IrcMsg,
        args: List[str],
    ) -> None:
        """- takes no arguments.
        Creates a new user table.
        """
        result: str = User.create_tables()
        irc.reply(result, prefixNick=False)

    createdb = wrap(createdb, ["owner"])

    def wz(
        self,
        irc: callbacks.NestedCommandsIrcProxy,
        msg: ircmsgs.IrcMsg,
        args: List[str],
        text: str,
    ) -> None:
        """- optional <location>
        Calls the weather.
        """
        location = text

        try:
            if not location:
                userinfo: User = User.get(host=msg.host)
                irc.reply(f"host is {msg.host}", prefixNick=False)
            else:
                irc.reply(location)

        except User.DoesNotExist:
            irc.reply(
                f"No weather location set by {msg.nick}.", prefixNick=False
            )

    wz = wrap(wz, [optional("text")])

    def setweather(
        self,
        irc: callbacks.NestedCommandsIrcProxy,
        msg: ircmsgs.IrcMsg,
        args: List[str],
        text: str,
    ) -> None:
        """<location>
        Sets the weather location for a user.
        """

    setweather = wrap(setweather, ["text"])


Class = WeatherBot
