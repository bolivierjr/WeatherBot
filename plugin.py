#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2019, Bruce Olivier
# All rights reserved.

import html
from typing import Dict, List, Union

from marshmallow import ValidationError
from peewee import DatabaseError
from requests import RequestException
from supybot import callbacks, ircmsgs, log
from supybot.commands import optional, wrap

from .models.users import AnonymousUser, User, UserSchema
from .utils.errors import LocationNotFound, WeatherNotFound
from .utils.services import query_current_weather, query_location

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

    @wrap([optional("text")])
    def weather(self, irc: callbacks.NestedCommandsIrcProxy, msg: ircmsgs.IrcMsg, args: List[str], text: str) -> None:
        """- optional <location>
        Calls the weather.
        """
        try:
            user: Union[User, AnonymousUser] = User.get_user(msg.nick)

            if not text and isinstance(user, AnonymousUser):
                irc.reply(f"No weather location set by {msg.nick}", prefixNick=False)

            elif not text:
                weather: str = query_current_weather(f"{user.location}, {user.region}", user.format)
                irc.reply(weather, prefixNick=False)

            else:
                deserialized_location: Dict[str, str] = UserSchema().load({"location": html.escape(text)}, partial=True)
                weather: str = query_current_weather(deserialized_location["location"], user.format)
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

    @wrap([optional("int"), "text"])
    def setweather(
        self, irc: callbacks.NestedCommandsIrcProxy, msg: ircmsgs.IrcMsg, args: List[str], num: int, text: str
    ) -> None:
        """<display_format> <location>
        Sets the weather location for a user.
        Format number is set to 1 for imperial, and 2 for metric, for which
        units to display first. e.g. setweather 2 70118
        """
        try:
            format_error = {"format": ["Must enter in an integer for the display format."]}
            if not isinstance(num, int):
                raise ValidationError(format_error)

            deserialized_location: Dict[str, str] = UserSchema().load(
                {"location": html.escape(text), "format": num}, partial=True,
            )
            geo: Dict[str, str] = query_location(deserialized_location["location"])
            geo.update({"nick": msg.nick, "host": f"{msg.user}@{msg.host}", "format": num})
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

            units = "imperial" if num == 1 else "metric"
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
