#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2019, Bruce Olivier
# All rights reserved.

import html
from typing import Dict, List, Tuple, Union

from marshmallow import ValidationError
from peewee import DatabaseError
from requests import RequestException
from supybot import callbacks, ircmsgs, log
from supybot.commands import getopts, optional, wrap

from .models.users import User, UserSchema
from .utils.errors import LocationNotFound, WeatherNotFound
from .utils.services import query_current_weather, query_location
from .utils.users import AnonymousUser, get_user

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("WeatherBot")
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    def _(x):
        return x


class WeatherBot(callbacks.Plugin):
    """A weather script that uses Darksky and Weatherstack.
    """

    threaded = True

    @wrap(["owner"])
    def createdb(self, irc: callbacks.NestedCommandsIrcProxy, msg: ircmsgs.IrcMsg, args: List[str]) -> None:
        """- takes no arguments.
        Creates a new user table.
        """
        try:
            result: str = User.create_tables()
            irc.reply(result, prefixNick=False)

        except DatabaseError as exc:
            log.error(str(exc))
            irc.reply("There was an error with the database. Check logs.", prefixNick=False)

    @wrap([getopts({"user": ""}), optional("text")])
    def weather(
        self,
        irc: callbacks.NestedCommandsIrcProxy,
        msg: ircmsgs.IrcMsg,
        args: List[str],
        optlist: List[Tuple[str, bool]],
        text: str,
    ) -> None:
        """- optional <location> OR [--user] <username>
        Calls the current weather given an optional arg .e.g. .weather 70119 -
        If you leave out the location, it will try to use the user's set location that is saved -
        You can find another user's weather by using the --user flag. e.g. .weather --user Chad
        """
        lookup_user: bool = False
        for opt, _ in optlist:
            if opt == "user":
                lookup_user = True

        try:
            optional_user = html.escape(text) if lookup_user and text else msg.nick
            if lookup_user and not text:
                irc.reply(f"Please specify the user name.", prefixNick=False)
                return

            user: Union[User, AnonymousUser] = get_user(optional_user)

            if lookup_user:
                if not isinstance(user, AnonymousUser):
                    weather: str = query_current_weather("", user)
                    irc.reply(weather, prefixNick=False)
                else:
                    irc.reply(f"No such user by the name of {text}.", prefixNick=False)

            elif not text and isinstance(user, AnonymousUser):
                irc.reply(f"No weather location set by {msg.nick}", prefixNick=False)

            elif not text:
                weather: str = query_current_weather(text, user)
                irc.reply(weather, prefixNick=False)

            else:
                deserialized_location: Dict[str, str] = UserSchema().load({"location": html.escape(text)}, partial=True)
                weather: str = query_current_weather(deserialized_location["location"], user)
                irc.reply(weather, prefixNick=False)

        except ValidationError as exc:
            if "location" in exc.messages:
                message = exc.messages["location"][0]
            irc.reply(message, prefixNick=False)
            log.error(str(exc), exc_info=True)

        except DatabaseError as exc:
            log.error(str(exc), exc_info=True)
            if "not created" in str(exc):
                irc.reply(str(exc), prefixNick=True)
            else:
                irc.reply("There is an error. Contact admin.", prefixNick=False)

        except (LocationNotFound, WeatherNotFound) as exc:
            irc.reply(str(exc), prefixNick=False)

        except RequestException as exc:
            log.error(str(exc), exc_info=True)
            if exc.response.status_code == 400:
                irc.reply("Unable to find this location.", prefixNick=False)
            else:
                irc.reply("There is an error. Contact admin.", prefixNick=False)

    @wrap([getopts({"metric": ""}), "text"])
    def setweather(
        self,
        irc: callbacks.NestedCommandsIrcProxy,
        msg: ircmsgs.IrcMsg,
        args: List[str],
        optlist: List[Tuple[str, bool]],
        text: str,
    ) -> None:
        """[--metric] <location>
        Sets the weather location for a user. Format is set to show imperial first by default.
        To show metric first, use the --metric option. e.g. setweather --metric 70118
        """
        try:
            format = 1
            for option, _ in optlist:
                if option == "metric":
                    format = 2

            deserialized_location: Dict[str, str] = UserSchema().load(
                {"location": html.escape(text), "format": format}, partial=True,
            )
            geo: Dict[str, str] = query_location(deserialized_location["location"])
            geo.update({"nick": msg.nick, "host": f"{msg.user}@{msg.host}", "format": format})
            if geo["location"] is None:
                raise LocationNotFound("Unable to find this location.")

            user_schema: Dict[str, str] = UserSchema().load(geo)
            user, created = User.get_or_create(
                nick=msg.nick,
                defaults={
                    "host": user_schema["host"],
                    "format": user_schema["format"],
                    "location": user_schema["location"],
                    "region": user_schema["region"],
                    "coordinates": user_schema["coordinates"],
                },
            )

            # If created is a boolean of 0, it means it found a user.
            # Updates the user fields and saves to db.
            if not created:
                user.host = user_schema["host"]
                user.format = user_schema["format"]
                user.location = user_schema["location"]
                user.region = user_schema["region"]
                user.coordinates = user_schema["coordinates"]
                user.save()

            units = "imperial" if format == 1 else "metric"
            log.info(f"{msg.nick} set their location to {text}")
            irc.reply(f"{msg.nick} set their weather to {units} first and {text}.", prefixNick=False)

        except ValidationError as exc:
            if "location" in exc.messages:
                message = exc.messages["location"][0]
                irc.reply(message, prefixNick=False)
            elif "format" in exc.messages:
                message = exc.messages["format"][0]
                irc.reply(message, prefixNick=False)
            log.error(str(exc), exc_info=True)

        except DatabaseError as exc:
            log.error(str(exc), exc_info=True)
            if "not created" in str(exc):
                irc.reply(str(exc), prefixNick=True)
            else:
                irc.reply("There is an error. Contact admin.", prefixNick=False)

        except LocationNotFound as exc:
            irc.reply(str(exc), prefixNick=False)

        except RequestException as exc:
            log.error(str(exc), exc_info=True)
            irc.reply("Unable to find this location.", prefixNick=False)


Class = WeatherBot
