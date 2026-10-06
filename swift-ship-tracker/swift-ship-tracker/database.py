from pathlib import Path
import sqlite3
from flask import current_app, g

def get_db():
    if 'db' not in g:
        path = Path(current_app.config['DATABASE_PATH']); path.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(path); g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db

def close_db(exception=None):
    db = g.pop('db', None)
    if db: db.close()

def init_db():
    db = get_db(); db.executescript(Path(current_app.root_path, 'schema.sql').read_text()); db.commit()
