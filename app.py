"""Application factory for the Library Management Information System."""

import os
import secrets
from datetime import date
from pathlib import Path

from flask import Flask

from config import (
    DEFAULT_LIBRARIAN_PASSWORD,
    DEFAULT_LIBRARIAN_USERNAME,
    FINE_PER_DAY,
    LOAN_DAYS,
    MAX_ACTIVE_LOANS,
)
from database import close_db, init_db
from i18n import LANGUAGES, current_language, translate
from routes import auth, books, loans, members, reports

__all__ = [
    "create_app",
    "DEFAULT_LIBRARIAN_PASSWORD",
    "DEFAULT_LIBRARIAN_USERNAME",
    "FINE_PER_DAY",
    "LOAN_DAYS",
    "MAX_ACTIVE_LOANS",
]


def create_app(database=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        DATABASE=str(database or Path(__file__).with_name("library.db")),
        MAX_CONTENT_LENGTH=64 * 1024,
        LIBRARIAN_USERNAME=os.environ.get("LIBRARIAN_USERNAME")
        or DEFAULT_LIBRARIAN_USERNAME,
        LIBRARIAN_PASSWORD=os.environ.get("LIBRARIAN_PASSWORD")
        or DEFAULT_LIBRARIAN_PASSWORD,
    )

    @app.template_filter("display_date")
    def display_date(value):
        try:
            return date.fromisoformat(value).strftime("%d/%m/%Y")
        except (TypeError, ValueError):
            return value

    @app.context_processor
    def inject_i18n():
        return {"t": translate, "language": current_language(), "languages": LANGUAGES}

    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()

    auth.register(app)
    books.register(app)
    members.register(app)
    loans.register(app)
    reports.register(app)
    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000)
