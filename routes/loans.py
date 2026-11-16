"""Book borrowing, returns, overdue rules, and loan query helpers."""

from datetime import date, timedelta
import sqlite3

from flask import abort, flash, redirect, render_template, request, url_for

from config import LOAN_DAYS, MAX_STUDENT_LOANS, MAX_TEACHER_LOANS
from database import get_db
from i18n import translate


def overdue_days(loan, today):
    due = date.fromisoformat(loan["due_date"])
    end = date.fromisoformat(loan["returned_at"]) if loan["returned_at"] else today
    return max(0, (end - due).days)


def loan_or_404(loan_id):
    loan = get_db().execute("SELECT * FROM loans WHERE id = ?", (loan_id,)).fetchone()
    if loan is None:
        abort(404)
    return loan


def active_loans_for_book(book_id):
    return (
        get_db()
        .execute(
            "SELECT count(*) FROM loans WHERE book_id = ? AND returned_at IS NULL",
            (book_id,),
        )
        .fetchone()[0]
    )


def active_loans_for_member(member_id):
    return (
        get_db()
        .execute(
            "SELECT count(*) FROM loans WHERE member_id = ? AND returned_at IS NULL",
            (member_id,),
        )
        .fetchone()[0]
    )


def member_has_overdue(member_id):
    return (
        get_db()
        .execute(
            "SELECT count(*) FROM loans WHERE member_id = ? AND returned_at IS NULL AND due_date < ?",
            (member_id, date.today().isoformat()),
        )
        .fetchone()[0]
        > 0
    )


def loan_limit_for(member):
    return (
        MAX_TEACHER_LOANS if member["member_type"] == "teacher" else MAX_STUDENT_LOANS
    )


def loan_rows(query=""):
    return (
        get_db()
        .execute(
            """SELECT loans.*, books.title AS book_title, books.author AS book_author,
        members.member_number AS member_number, members.full_name AS member_name
        FROM loans JOIN books ON books.id = loans.book_id JOIN members ON members.id = loans.member_id
        WHERE instr(lower(books.title), lower(?)) > 0 OR instr(lower(members.member_number), lower(?)) > 0
           OR instr(lower(members.full_name), lower(?)) > 0
        ORDER BY (loans.returned_at IS NOT NULL), loans.borrowed_at DESC, loans.id DESC""",
            (query, query, query),
        )
        .fetchall()
    )


def enrich_loans(rows, today=None):
    today = today or date.today()
    enriched = []
    for row in rows:
        loan = dict(row)
        loan["overdue_days"] = overdue_days(row, today)
        enriched.append(loan)
    return enriched


def register(app):
    @app.get("/loans")
    def loans():
        query = request.args.get("q", "").strip()
        today = date.today()
        enriched = enrich_loans(loan_rows(query), today)
        active_count = (
            get_db()
            .execute("SELECT count(*) FROM loans WHERE returned_at IS NULL")
            .fetchone()[0]
        )
        overdue_count = (
            get_db()
            .execute(
                "SELECT count(*) FROM loans WHERE returned_at IS NULL AND due_date < ?",
                (today.isoformat(),),
            )
            .fetchone()[0]
        )
        return render_template(
            "loans.html",
            loans=enriched,
            active_count=active_count,
            overdue_count=overdue_count,
            today=today.isoformat(),
            query=query,
        )

    @app.route("/loans/new", methods=["GET", "POST"])
    def new_loan():
        books = get_db().execute("""SELECT books.*, books.copies - coalesce(
            (SELECT count(*) FROM loans WHERE loans.book_id = books.id AND loans.returned_at IS NULL), 0) AS available
            FROM books ORDER BY title""").fetchall()
        values, errors = {}, {}
        if request.method == "POST":
            values = {
                key: request.form.get(key, "").strip()
                for key in ("member_number", "book_id")
            }
            values["member_number"] = values["member_number"].upper()
            connection = get_db()
            # This transaction serializes the availability and quota checks with
            # the INSERT, so simultaneous requests cannot lend the same copy.
            try:
                connection.execute("BEGIN IMMEDIATE")
                member = connection.execute(
                    "SELECT * FROM members WHERE member_number = ? COLLATE NOCASE",
                    (values["member_number"],),
                ).fetchone()
                book = (
                    connection.execute(
                        "SELECT * FROM books WHERE id = ?", (values["book_id"],)
                    ).fetchone()
                    if values["book_id"].isdigit()
                    else None
                )
                if member is None:
                    errors["member_number"] = translate(
                        "Namba ya mwanachama haipo. Hakiki namba au msajili mwanachama kwanza."
                    )
                elif member["status"] != "active":
                    errors["member_number"] = translate(
                        "Mwanachama huyu si hai (inactive); hawezi kuazima kitabu."
                    )
                elif member_has_overdue(member["id"]):
                    errors["member_number"] = translate(
                        "Mwanachama huyu ana kitabu kilichochelewa ambacho bado hajarejesha; hawezi kuazima kingine mpaka akirejeshe."
                    )
                elif active_loans_for_member(member["id"]) >= loan_limit_for(member):
                    errors["member_number"] = (
                        f"{translate('Mwanachama huyu ana vitabu')} {loan_limit_for(member)} {translate('ambavyo bado hajarejesha; hawezi kuazima kingine')}."
                    )
                if book is None:
                    errors["book_id"] = translate("Chagua kitabu halali.")
                elif active_loans_for_book(book["id"]) >= book["copies"]:
                    errors["book_id"] = translate(
                        "Hakuna nakala za kitabu hiki zilizobaki kwa sasa."
                    )
                if not errors:
                    borrowed_at = date.today()
                    due_date = borrowed_at + timedelta(days=LOAN_DAYS)
                    connection.execute(
                        "INSERT INTO loans (book_id, member_id, borrowed_at, due_date) VALUES (?, ?, ?, ?)",
                        (
                            book["id"],
                            member["id"],
                            borrowed_at.isoformat(),
                            due_date.isoformat(),
                        ),
                    )
                    connection.commit()
                    flash(translate("Kitabu kimekopeshwa."))
                    return redirect(url_for("loans"))
                connection.rollback()
            except sqlite3.OperationalError:
                connection.rollback()
                errors["book_id"] = translate(
                    "Mfumo una shughuli nyingine ya kukopesha. Jaribu tena."
                )
        members = get_db().execute(
            """SELECT member_number, full_name FROM members
            WHERE status = 'active' ORDER BY full_name"""
        ).fetchall()
        return render_template(
            "loan_form.html",
            values=values,
            errors=errors,
            books=books,
            members=members,
            loan_days=LOAN_DAYS,
            due_date=(date.today() + timedelta(days=LOAN_DAYS)).isoformat(),
        )

    @app.route("/loans/<int:loan_id>/return", methods=["GET", "POST"])
    def return_loan(loan_id):
        loan = loan_or_404(loan_id)
        book = (
            get_db()
            .execute("SELECT * FROM books WHERE id = ?", (loan["book_id"],))
            .fetchone()
        )
        member = (
            get_db()
            .execute("SELECT * FROM members WHERE id = ?", (loan["member_id"],))
            .fetchone()
        )
        if loan["returned_at"] is not None:
            flash(translate("Kitabu hiki tayari kimerejeshwa."))
            return redirect(url_for("loans"))
        today = date.today()
        days_late = overdue_days(loan, today)
        if request.method == "POST":
            get_db().execute(
                "UPDATE loans SET returned_at = ? WHERE id = ?",
                (today.isoformat(), loan_id),
            )
            get_db().commit()
            flash(
                f"{translate('Kitabu kimerejeshwa.')} {translate('Kimechelewa siku')} {days_late}."
                if days_late
                else translate("Kitabu kimerejeshwa.")
            )
            return redirect(url_for("loans"))
        return render_template(
            "loan_return.html",
            loan=loan,
            book=book,
            member=member,
            days_late=days_late,
        )
