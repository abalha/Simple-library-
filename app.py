"""Application factory for the Library Management Information System."""

import os
import secrets
from datetime import date
from pathlib import Path

from flask import Flask

from config import (
    DEFAULT_LIBRARIAN_PASSWORD,
    DEFAULT_LIBRARIAN_USERNAME,
    LOAN_DAYS,
    MAX_STUDENT_LOANS,
    MAX_TEACHER_LOANS,
)
from database import close_db, init_db
from i18n import LANGUAGES, current_language, translate
from routes import auth, books, loans, members, reports

__all__ = [
    "create_app",
    "DEFAULT_LIBRARIAN_PASSWORD",
    "DEFAULT_LIBRARIAN_USERNAME",
    "LOAN_DAYS",
    "MAX_STUDENT_LOANS",
    "MAX_TEACHER_LOANS",
]


def load_or_create_secret_key():
    # key ileile kila uzinduzi ili session ya mhudumu isikufee restart
    key_file = Path(__file__).with_name(".secret_key")
    if key_file.is_file():
        key = key_file.read_text().strip()
        if key:
            return key
    key = secrets.token_hex(32)
    key_file.write_text(key)
    key_file.chmod(0o600)
    return key


def create_app(database=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY") or load_or_create_secret_key(),
        DATABASE=str(database or Path(__file__).with_name("library.db")),
        MAX_CONTENT_LENGTH=64 * 1024,
        # CSS/mizingo ipate ETag revalidation kila refresh — mabadiliko ya UI yaonekane bila hard refresh
        SEND_FILE_MAX_AGE_DEFAULT=0,
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
        return {
            "t": translate,
            "language": current_language(),
            "languages": LANGUAGES,
            "current_year": date.today().year,
        }

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
