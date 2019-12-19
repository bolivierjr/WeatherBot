import os
import logging
import sqlite3
from typing import Tuple, Union


log = logging.getLogger(__name__)


class UserInfo:
    """
    A users info stored in the db.
    """

    fullpath: str = os.path.dirname(os.path.abspath(__file__))
    db: str = f"{fullpath}/../data/{os.environ.get('DB_NAME')}"
    table: str = os.environ.get("DB_TABLE")

    def __init__(self, **kwargs):
        self.conn = self._connect()
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def get(self) -> Tuple:
        log.info("Getting user info from database.")
        sql: str = """ """
        cursor = self.conn.cursor()
        cursor.execute(sql())

    def set(self) -> None:
        pass

    def _connect(self) -> Union[sqlite3.Connection, None]:
        try:
            if not os.path.isfile(self.db):
                return self._create_database()

            log.info("Connecting to the SQLite3 database.")
            conn = sqlite3.connect(self.db)

            return conn

        except sqlite3.Error as err:
            log.error(err)

    def _create_database(self) -> None:
        # self.irc.reply("No database found. Creating a new database...")

        conn = None

        try:
            log.info(
                f"Connecting to SQLite3 database to create {os.environ.get('DB_NAME')}."
            )

            conn: sqlite3.Connection = sqlite3.connect(self.db)
            cursor: sqlite3.Cursor = conn.cursor()
            sql: str = f"""CREATE TABLE IF NOT EXISTS {self.table} (
                        id INTEGER PRIMARY KEY,
                        nick TEXT NOT NULL,
                        host TEXT NOT NULL,
                        units INTEGER NOT NULL,
                        location TEXT NOT NULL,
                        channel TEXT NOT NULL,
                        timestamp INT DEFAULT NULL);"""

            cursor.execute(sql)
            conn.commit()
            cursor.close()
            log.info(f"Database created with a '{self.table}' table.")

            return conn

        except sqlite3.Error as err:
            log.error(err)

    def __del__(self):
        if self.conn is not None:
            self.conn.close()
            log.info("Database connection closed.")
