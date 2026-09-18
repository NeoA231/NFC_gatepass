import sqlite3
from flask import g, current_app

DATABASE = "gatepass.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES

        )
        #Enables column access by name: row["student_number"]
        g.db.row_factory = sqlite3.Row
        #Crucial: enable foreign key consttraints per connection
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db

def close_db(e=None):
    db = g.pop("db",None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with open("db/schema.sql", mode="r") as f:
        db.executescript(f.read())