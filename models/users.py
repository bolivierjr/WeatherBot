import os
from datetime import datetime
from os.path import abspath, dirname, isfile, join

from dotenv import load_dotenv
from marshmallow import Schema, ValidationError, fields, validates
from peewee import CharField, DateTimeField, IntegerField, Model, SqliteDatabase
from supybot import log

path: str = dirname(abspath(__file__))
env_path: str = join(path, "..", ".env")
load_dotenv(dotenv_path=env_path)
db_path: str = join(path, "..", "data", os.getenv("DB_NAME"))

db = SqliteDatabase(db_path)


class User(Model):
    nick = CharField(unique=True, max_length=15, null=False)
    host = CharField(max_length=255, null=False)
    format = IntegerField(default=1)
    location = CharField(max_length=80, null=False)
    region = CharField(max_length=80, null=False)
    coordinates = CharField(max_length=20, null=False)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        db_table = "users"

    @classmethod
    def create_tables(cls) -> str:
        if isfile(db_path) and cls.table_exists():
            return "Users table already created."
        with db:
            cls.create_table()
            log.info("Created the users table")
            return "Created users table."

    def __repr__(self):
        return f"<User {self.nick}>"


class UserSchema(Schema):
    id = fields.Integer()
    nick = fields.String(required=True)
    host = fields.String(required=True)
    format = fields.Integer(required=True)
    location = fields.String(required=True)
    region = fields.String(required=True)
    coordinates = fields.String(required=True)

    @validates("location")
    def validate_location(self, data, **kwargs):
        if len(data) > 80:
            raise ValidationError("location is too long.")

    @validates("format")
    def validate_format(self, data, **kwargs):
        if data == 1 or data == 2:
            return
        raise ValidationError("Format setting must be set to 1 for imperial or 2 for metric units first.")
