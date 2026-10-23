import json
import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager


def data_root():
    return Path(os.getenv('LOCALAPPDATA', str(Path.home() / '.local/share'))) / 'SheikhHamamomin'


class Memory:
    def __init__(self, root=None):
        self.root = Path(root or data_root())
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / 'memory.sqlite3'
        with self.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, role TEXT, content TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
            CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, kind TEXT, detail TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS preferences(key TEXT PRIMARY KEY, value TEXT);
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        try:
            db.row_factory = sqlite3.Row
            with db:
                yield db
        finally:
            db.close()

    def add(self, role, content):
        with self.connect() as db:
            db.execute('INSERT INTO messages(role,content) VALUES (?,?)', (role, content))

    def history(self, limit=40):
        with self.connect() as db:
            rows = db.execute('SELECT * FROM messages ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
            return [dict(r) for r in reversed(rows)]

    def get(self, key, default=None):
        with self.connect() as db:
            row = db.execute('SELECT value FROM settings WHERE key=?', (key,)).fetchone()
            return json.loads(row[0]) if row else default

    def set(self, key, value):
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO settings VALUES (?,?)', (key, json.dumps(value)))

    def preference(self, key, value):
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO preferences VALUES (?,?)', (key, value))

    def preferences(self):
        with self.connect() as db:
            return dict(db.execute('SELECT key,value FROM preferences').fetchall())

    def event(self, kind, detail):
        with self.connect() as db:
            db.execute('INSERT INTO events(kind,detail) VALUES (?,?)', (kind, detail))

    def export(self):
        with self.connect() as db:
            return {table: [dict(r) for r in db.execute(f'SELECT * FROM {table}')] for table in ('messages', 'preferences', 'events', 'settings')}

    def clear(self):
        with self.connect() as db:
            for table in ('messages', 'preferences', 'events'):
                db.execute(f'DELETE FROM {table}')

    def edit_message(self, message_id, content):
        with self.connect() as db:
            db.execute('UPDATE messages SET content=? WHERE id=?', (content, message_id))
