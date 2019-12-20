#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2018, Bruce Olivier
# All rights reserved.

import html
import logging
from typing import List, Union
from peewee import DatabaseError
from marshmallow import ValidationError
from .models.users import User, UserSchema
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
        try:
            result: str = User.create_tables()
            irc.reply(result, prefixNick=False)

        except DatabaseError as exc:
            log.error(str(exc))
            irc.reply(
                "There was an error with the database. Check logs.",
                prefixNick=False,
            )

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
        location: str = text
        userinfo: Union[User, None]

        try:
            try:
                userinfo = User.get(host=msg.nick)
            except User.DoesNotExist:
                log.info(f"{msg.nick} not found in db.")
                userinfo = None

            if not location and userinfo:
                pass

            irc.reply(
                f"No weather location set by {msg.nick}.", prefixNick=False
            )

        except DatabaseError as exc:
            log.error(str(exc))
            irc.reply("There is an error. Contact admin.", prefixNick=False)

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
        userinfo = {
            "nick": msg.nick,
            "host": msg.host,
            "location": html.escape(text),
        }
        user: Union[User, None]

        try:
            try:
                user = User.get(nick=msg.nick)
            except User.DoesNotExist:
                user = None

            userschema = UserSchema().load(userinfo)
            location = userschema["location"]

            if user:
                user.location = location
                user.save()
            else:
                new_user = User(**userschema)
                new_user.save()

            log.info(f"{msg.nick} set it his location to {location}")
            irc.reply(
                f"{msg.nick} has set location to {location}", prefixNick=False,
            )

        except ValidationError as exc:
            if "location" in exc.messages:
                message = exc.messages["location"][0]
                irc.reply(message, prefixNick=False)

        except DatabaseError as exc:
            log.error(str(exc))
            irc.reply("There is an error. Contact admin.", prefixNick=False)

    setweather = wrap(setweather, ["text"])


Class = WeatherBot
