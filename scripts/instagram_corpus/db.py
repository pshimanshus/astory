from __future__ import annotations

import sqlite3
from pathlib import Path

from scripts.instagram_corpus.schema import SCHEMA_SQL


def connect(path):
    conn = sqlite3.connect(str(path if path == ":memory:" else Path(path)))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize(conn):
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_SQL)
    conn.commit()


def table_names(conn):
    rows = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        """
    )
    return {row["name"] for row in rows}

