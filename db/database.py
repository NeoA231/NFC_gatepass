import os
import sqlite3
from flask import g

DATABASE = "gatepass.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    # Resolve schema path relative to database.py directory
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, mode="r") as f:
        db.executescript(f.read())