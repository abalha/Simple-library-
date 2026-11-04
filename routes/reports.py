"""Printable book, borrowing, and member reports."""

from datetime import date

from flask import render_template

from database import get_db
from routes.loans import enrich_loans, loan_rows


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
        estimated_fines = sum(
            loan["fine"]
            for loan in loans
            if loan["returned_at"] is None and loan["overdue_days"] > 0
        )
        return render_template(
            "loans_report.html",
            loans=loans,
            active_count=active_count,
            overdue_count=overdue_count,
            estimated_fines=estimated_fines,
            generated_at=today.isoformat(),
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
