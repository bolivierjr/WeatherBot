import os
from os.path import abspath, dirname, isfile, join
from typing import Union

from dotenv import load_dotenv
from peewee import DatabaseError

from ..models.users import User

path: str = dirname(abspath(__file__))
env_path: str = join(path, "..", ".env")
load_dotenv(dotenv_path=env_path)
db_path: str = join(path, "..", "data", os.getenv("DB_NAME"))


class AnonymousUser:
    """
    A default user if no user is found in the db.

    Attributes:
        format: The default display format for an anonymous user.
    """

    format = 1


def get_user(nick: str) -> Union[User, AnonymousUser]:
    """
    Gets a user out of the database. If not found, it returns a default user object.

    Args:
        nick: the name of the user's nick.

    Returns:
        A User model object or a default AnonymousUser.
    """
    user: Union[User, AnonymousUser]
    try:
        if not isfile(db_path) or not User.table_exists():
            raise DatabaseError("Users db and table not created yet.")
        user: User = User.get(nick=nick)
    except User.DoesNotExist:
        user: AnonymousUser = AnonymousUser()

    return user
