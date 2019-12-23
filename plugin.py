#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2018, Bruce Olivier
# All rights reserved.

import html
from peewee import DatabaseError
from typing import List, Union, Dict
from requests import RequestException
from marshmallow import ValidationError
from .utils.errors import LocationNotFound
from .models.users import User, UserSchema
from .utils.helpers import check_user, find_geolocation, find_current_weather
from supybot import utils, plugins, ircutils, callbacks, ircmsgs, log
from supybot.commands import wrap, optional, getopts

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("APIXUWeather")
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    def _(x):
        return x


class WeatherBot(callbacks.Plugin):
    """A weather script that uses Darksky and Weatherstack.
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
        try:
            geo: Dict[str, str]
            weather: Union[Dict[str, str], None] = None
            user: Union[User, None] = check_user(msg.nick)

            if not text and not user:
                irc.reply(
                    f"No weather location set by {msg.nick}", prefixNick=False
                )

            elif user and not text:
                weather = find_current_weather(user.coordinates)

            else:
                deserialized_location: Dict[str, str] = UserSchema().load(
                    {"location": html.escape(text)}, partial=True
                )
                geo = find_geolocation(deserialized_location["location"])
                weather = find_current_weather(geo["coordinates"])

            if weather:
                irc.reply(f"{weather}", prefixNick=False)

        except ValidationError as exc:
            if "location" in exc.messages:
                message = exc.messages["location"][0]
                irc.reply(message, prefixNick=False)
            log.error(str(exc), exc_info=True)

        except DatabaseError as exc:
            log.error(str(exc), exc_info=True)
            irc.reply("There is an error. Contact admin.", prefixNick=False)

        except LocationNotFound as exc:
            irc.reply(str(exc), prefixNick=False)

        except RequestException as exc:
            log.error(str(exc), exc_info=True)
            irc.reply("There was an error. Contact admin.", prefixNick=False)

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
        try:
            deserialized_location: Dict[str, str] = UserSchema().load(
                {"location": html.escape(text)}, partial=True
            )
            geo: Dict[str, str] = find_geolocation(
                deserialized_location["location"]
            )
            geo.update({"nick": msg.nick, "host": f"{msg.user}@{msg.host}"})
            user_schema: Dict[str, str] = UserSchema().load(geo)
            user: Union[User, None] = check_user(msg.nick)

            if user:
                user.host = user_schema["host"]
                user.location = user_schema["location"]
                user.region = user_schema["region"]
                user.coordinates = user_schema["coordinates"]
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
            log.error(str(exc), exc_info=True)

        except DatabaseError as exc:
            log.error(str(exc), exc_info=True)
            irc.reply("There was an error. Contact admin.", prefixNick=False)

        except LocationNotFound as exc:
            irc.reply(str(exc), prefixNick=False)

        except RequestException as exc:
            log.error(str(exc), exc_info=True)
            irc.reply("Unable to find this location.", prefixNick=False)

    setweather = wrap(setweather, ["text"])


Class = WeatherBot
