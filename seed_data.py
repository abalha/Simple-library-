"""Weka sample data ya presentation kwenye database tupu.

Endesha: python seed_data.py
Kwa test database: python seed_data.py njia/ya/test.db
"""

import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

from app import create_app

DATABASE = (
    Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("library.db")
)


def main():
    create_app(DATABASE)
    connection = sqlite3.connect(DATABASE)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        counts = [
            connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            for table in ("books", "members", "loans")
        ]
        if any(counts):
            raise SystemExit(
                "Sample data haijawekwa: database tayari ina data. "
                "Tumia database tupu ili kulinda taarifa zilizopo."
            )

        books = [
            ("Misingi ya Python", "Asha Mussa", "Teknolojia", 2024, 4),
            ("Utangulizi wa Database", "Juma Ali", "Teknolojia", 2023, 3),
            ("Mawasiliano ya Kiswahili", "Rehema Said", "Lugha", 2022, 5),
            ("Principles of Management", "Peter Drucker", "Biashara", 2021, 2),
            ("Basic Mathematics", "Salma Omar", "Hisabati", 2020, 4),
            ("Environmental Studies", "Hassan Mwinyi", "Sayansi", 2022, 3),
        ]
        members = [
            # ("ST001", "Amina Said", "student", "active"),
            # ("ST002", "Juma Hassan", "student", "active"),
            # ("ST003", "Zainab Omar", "student", "active"),
            # ("TC001", "Neema Mally", "teacher", "active"),
            # ("ST004", "Bakari Musa", "student", "inactive"),
        ]
        connection.executemany(
            "INSERT INTO books (title, author, category, publication_year, copies) VALUES (?, ?, ?, ?, ?)",
            books,
        )
        connection.executemany(
            "INSERT INTO members (member_number, full_name, member_type, status) VALUES (?, ?, ?, ?)",
            members,
        )

        today = date.today()
        loans = [
            # Mkopo wa kawaida ulio mikononi.
            (1, 1, today - timedelta(days=10), today + timedelta(days=20), None),
            # Mkopo uliochelewa, wa kuonyesha overdue/faini.
            (2, 2, today - timedelta(days=35), today - timedelta(days=5), None),
            # Mkopo uliorejeshwa kwa wakati.
            (
                3,
                3,
                today - timedelta(days=20),
                today + timedelta(days=10),
                today - timedelta(days=2),
            ),
            # Mkopo uliorejeshwa ukiwa umechelewa.
            (
                4,
                4,
                today - timedelta(days=45),
                today - timedelta(days=15),
                today - timedelta(days=12),
            ),
        ]
        connection.executemany(
            """INSERT INTO loans (book_id, member_id, borrowed_at, due_date, returned_at)
               VALUES (?, ?, ?, ?, ?)""",
            [
                (
                    book_id,
                    member_id,
                    borrowed.isoformat(),
                    due.isoformat(),
                    returned.isoformat() if returned else None,
                )
                for book_id, member_id, borrowed, due, returned in loans
            ],
        )
        connection.commit()
    finally:
        connection.close()

    print(f"Sample data imewekwa kwenye {DATABASE}.")


if __name__ == "__main__":
    main()
