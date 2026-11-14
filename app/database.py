import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .config import settings


def connect() -> sqlite3.Connection:
    path = Path(settings.database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def transaction():
    connection = connect()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialise() -> None:
    with transaction() as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL CHECK(length(title) BETWEEN 1 AND 120),
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL CHECK(status IN ('todo','in_progress','done')),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
            )"""
        )
