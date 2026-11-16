"""Printable book, borrowing, and member reports."""

from datetime import date

from flask import render_template

from database import get_db
from routes.loans import enrich_loans, loan_rows


def active_loan_rows(where="", parameters=()):
    return get_db().execute(
        f"""SELECT loans.*, books.title AS book_title, books.author AS book_author,
        members.member_number AS member_number, members.full_name AS member_name
        FROM loans JOIN books ON books.id = loans.book_id
        JOIN members ON members.id = loans.member_id
        WHERE loans.returned_at IS NULL {where}
        ORDER BY loans.due_date, loans.borrowed_at, loans.id""",
        parameters,
    ).fetchall()


def register(app):
    @app.get("/reports/books")
    def books_report():
        connection = get_db()
        books = connection.execute("""SELECT books.*, books.copies - coalesce(
            (SELECT count(*) FROM loans WHERE loans.book_id = books.id AND loans.returned_at IS NULL), 0) AS available
            FROM books ORDER BY title""").fetchall()
        totals = connection.execute(
            """SELECT count(*) AS titles, coalesce(sum(copies), 0) AS copies,
            coalesce(sum(copies - (SELECT count(*) FROM loans WHERE loans.book_id = books.id AND loans.returned_at IS NULL)), 0) AS available
            FROM books"""
        ).fetchone()
        return render_template(
            "books_report.html",
            books=books,
            totals=totals,
            generated_at=date.today().isoformat(),
        )

    @app.get("/reports/loans")
    def loans_report():
        today = date.today()
        loans = enrich_loans(loan_rows(), today)
        active_count = sum(loan["returned_at"] is None for loan in loans)
        overdue_count = sum(
            loan["returned_at"] is None and loan["overdue_days"] > 0 for loan in loans
        )
        return render_template(
            "loans_report.html",
            loans=loans,
            active_count=active_count,
            overdue_count=overdue_count,
            generated_at=today.isoformat(),
        )

    @app.get("/reports/current-loans")
    def current_loans_report():
        today = date.today()
        loans = enrich_loans(active_loan_rows(), today)
        return render_template(
            "current_loans_report.html", loans=loans, generated_at=today.isoformat()
        )

    @app.get("/reports/overdue")
    def overdue_report():
        today = date.today()
        loans = enrich_loans(
            active_loan_rows("AND loans.due_date < ?", (today.isoformat(),)), today
        )
        return render_template(
            "overdue_report.html", loans=loans, generated_at=today.isoformat()
        )

    @app.get("/reports/low-stock")
    def low_stock_report():
        connection = get_db()
        books = connection.execute(
            """SELECT books.*, books.copies - coalesce(
                (SELECT count(*) FROM loans
                 WHERE loans.book_id = books.id AND loans.returned_at IS NULL), 0
            ) AS available
            FROM books
            WHERE books.copies - coalesce(
                (SELECT count(*) FROM loans
                 WHERE loans.book_id = books.id AND loans.returned_at IS NULL), 0
            ) <= 1
            ORDER BY available, title, id"""
        ).fetchall()
        totals = {
            "titles": len(books),
            "out_of_stock": sum(book["available"] == 0 for book in books),
            "one_left": sum(book["available"] == 1 for book in books),
        }
        return render_template(
            "low_stock_report.html",
            books=books,
            totals=totals,
            generated_at=date.today().isoformat(),
        )

    @app.get("/reports/members")
    def members_report():
        connection = get_db()
        members = connection.execute(
            "SELECT * FROM members ORDER BY full_name, id"
        ).fetchall()
        totals = connection.execute(
            """SELECT count(*) AS members, coalesce(sum(status = 'active'), 0) AS active,
            coalesce(sum(status = 'inactive'), 0) AS inactive FROM members"""
        ).fetchone()
        return render_template(
            "members_report.html",
            members=members,
            totals=totals,
            generated_at=date.today().isoformat(),
        )
