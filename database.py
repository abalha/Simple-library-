"""SQLite connection and schema helpers."""

import sqlite3

from flask import current_app, g

SCHEMA = (
    """CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        category TEXT NOT NULL,
        publication_year INTEGER NOT NULL CHECK(publication_year >= 1),
        copies INTEGER NOT NULL CHECK(copies >= 0)
    )""",
    """CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY,
        member_number TEXT NOT NULL CHECK(length(member_number) <= 50),
        full_name TEXT NOT NULL CHECK(length(full_name) <= 150),
        member_type TEXT NOT NULL CHECK(member_type IN ('student', 'teacher')),
        status TEXT NOT NULL CHECK(status IN ('active', 'inactive')) DEFAULT 'active',
        UNIQUE(member_number COLLATE NOCASE)
    )""",
    """CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY,
        book_id INTEGER NOT NULL REFERENCES books(id),
        member_id INTEGER NOT NULL REFERENCES members(id),
        borrowed_at TEXT NOT NULL,
        due_date TEXT NOT NULL,
        returned_at TEXT
    )""",
)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db():
    connection = get_db()
    for statement in SCHEMA:
        connection.execute(statement)
    connection.commit()
