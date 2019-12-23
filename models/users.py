from datetime import datetime
from supybot import log
from os.path import dirname, abspath, join, isfile
from marshmallow import Schema, fields, validates, ValidationError
from peewee import SqliteDatabase, CharField, DateTimeField, Model


path: str = dirname(abspath(__file__))
db_path: str = join(path, "..", "data", "Weather.db")
db = SqliteDatabase(db_path)


class User(Model):
    nick = CharField(unique=True, max_length=15, null=False)
    host = CharField(max_length=255, null=False)
    location = CharField(max_length=80, null=False)
    region = CharField(max_length=80, null=False)
    coordinates = CharField(max_length=20, null=False)
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

    def __repr__(self):
        return f"<User {self.nick}>"


class UserSchema(Schema):
    id = fields.Integer()
    nick = fields.String(required=True)
    host = fields.String(required=True)
    location = fields.String(required=True)
    region = fields.String(required=True)
    coordinates = fields.String(required=True)

    @validates("location")
    def validate_location(self, data, **kwargs):
        if len(data) > 80:
            raise ValidationError("location is too long.")
