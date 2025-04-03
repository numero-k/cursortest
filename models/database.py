import sqlite3
from flask import g
import os
from dotenv import load_dotenv

load_dotenv()

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            os.getenv('DATABASE_PATH', 'instance/bulletin.db'),
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with open('schema.sql') as f:
        db.executescript(f.read())
    db.commit()

def init_app(app):
    app.teardown_appcontext(close_db) 