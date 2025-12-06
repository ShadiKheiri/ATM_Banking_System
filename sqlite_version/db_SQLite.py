import sqlite3
import os

# database file in the same folder as this script
script_dir = os.path.dirname(os.path.abspath(__file__))
# database path
db_path = os.path.join(script_dir, "ATM_Manager.db")

# allow SQLite connection to be shared across Streamlit threads
mydb = sqlite3.connect(db_path, check_same_thread=False)

# activate foreign key constraints (SQLite disables them by default)
# constraints = rules that ensure data is valid (e.g., primary key, foreign key, unique)
# PRAGMA = SQLite’s built-in command to control database settings.
mydb.execute("PRAGMA foreign_keys = ON")


class MyCursor:
    def __init__(self, conn):
        self.conn = conn
        self.cur = conn.cursor()

    def execute(self, query, params=None):
        if params is None:
            self.cur.execute(query)
        else:
            self.cur.execute(query, params)
        return self

    def fetchone(self):
        return self.cur.fetchone()

    def fetchall(self):
        return self.cur.fetchall()

    @property
    def lastrowid(self):
        return self.cur.lastrowid


cursor = MyCursor(mydb)
