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


def _check_user(nick: str) -> Union[User, None]:
    user: Union[User, None]

    try:
        user = User.get(User.nick == nick)
    except User.DoesNotExist:
        user = None

    return user


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

        try:
            user: Union[User, None] = _check_user(msg.nick)

            if not location and user:
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
        info = {
            "nick": msg.nick,
            "host": msg.host,
            "location": html.escape(text),
        }

        try:
            user_schema: Dict[str, str] = UserSchema().load(info)
            user: Union[User, None] = _check_user(user_schema["nick"])

            if user:
                user.location = user_schema["location"]
                user.host = user_schema["host"]
                user.save()
            else:
                new_user = User(**user_schema)
                new_user.save()

            log.info(f"{msg.nick} set it his location to {text}")
            irc.reply(
                f"{msg.nick} has set location to {text}", prefixNick=False,
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
