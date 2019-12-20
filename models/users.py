import logging
from datetime import datetime
from os.path import dirname, abspath, join, isfile
from peewee import (
    SqliteDatabase,
    CharField,
    DateTimeField,
    Model,
)


log = logging.getLogger(__name__)
path: str = dirname(abspath(__file__))
db_path: str = join(path, "..", "data", "Weather.db")
db = SqliteDatabase(db_path)


class User(Model):
    nick = CharField(max_length=15)
    host = CharField(unique=True, max_length=255)
    channel = CharField(max_length=255)
    location = CharField(max_length=255)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db

    @staticmethod
    def create_tables() -> str:
        if isfile(db_path):
            return "Users table already created."
        with db:
            db.create_tables([User])
            log.info("Created the users table")
            return "Created users table."
