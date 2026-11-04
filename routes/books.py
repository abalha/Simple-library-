"""Book catalogue routes and book-related dashboard data."""

from datetime import date

from flask import abort, flash, redirect, render_template, request, url_for

from config import FINE_PER_DAY
from database import get_db
from i18n import translate


def book_or_404(book_id):
    book = get_db().execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if book is None:
        abort(404)
    return book


def active_loans_for_book(book_id):
    return (
        get_db()
        .execute(
            "SELECT count(*) FROM loans WHERE book_id = ? AND returned_at IS NULL",
            (book_id,),
        )
        .fetchone()[0]
    )


def register(app):
    @app.get("/")
    def index():
        query = request.args.get("q", "").strip()
        connection = get_db()
        books = connection.execute(
            """SELECT books.*, books.copies - coalesce(
                (SELECT count(*) FROM loans WHERE loans.book_id = books.id AND loans.returned_at IS NULL), 0) AS available
            FROM books
            WHERE instr(lower(title), lower(?)) > 0 OR instr(lower(author), lower(?)) > 0
            ORDER BY title, id""",
            (query, query),
        ).fetchall()
        totals = connection.execute(
            "SELECT count(*) AS titles, coalesce(sum(copies), 0) AS copies FROM books"
        ).fetchone()
        member_totals = connection.execute(
            "SELECT count(*) AS members, coalesce(sum(status = 'active'), 0) AS active FROM members"
        ).fetchone()
        active_loans = connection.execute(
            "SELECT due_date FROM loans WHERE returned_at IS NULL"
        ).fetchall()
        today = date.today()
        overdue_count = sum(
            date.fromisoformat(loan["due_date"]) < today for loan in active_loans
        )
        estimated_fines = sum(
            max(0, (today - date.fromisoformat(loan["due_date"])).days) * FINE_PER_DAY
            for loan in active_loans
        )
        summary = {
            "members": member_totals["members"],
            "active_members": member_totals["active"],
            "active_loans": len(active_loans),
            "overdue_loans": overdue_count,
            "estimated_fines": estimated_fines,
        }
        return render_template(
            "index.html", books=books, query=query, totals=totals, summary=summary
        )

    @app.route("/books/new", methods=["GET", "POST"])
    @app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
    def edit_book(book_id=None):
        book = book_or_404(book_id) if book_id is not None else None
        values = dict(book) if book is not None else {}
        errors = []
        if request.method == "POST":
            values = {
                key: request.form.get(key, "").strip()
                for key in ("title", "author", "category", "publication_year", "copies")
            }
            for key, label in (
                ("title", "Jina"),
                ("author", "Mwandishi"),
                ("category", "Aina"),
            ):
                if not values[key] or len(values[key]) > 150:
                    errors.append(f"{label}: jaza herufi 1 hadi 150.")
            numbers = {}
            for key, label, minimum, maximum in (
                ("publication_year", "Mwaka", 1, date.today().year),
                ("copies", "Nakala", 0, 1000000),
            ):
                try:
                    numbers[key] = int(values[key])
                    if not minimum <= numbers[key] <= maximum:
                        raise ValueError
                except ValueError:
                    errors.append(
                        f"{label}: jaza namba kamili kati ya {minimum} na {maximum}."
                    )
            if book_id is not None and "copies" in numbers:
                borrowed = active_loans_for_book(book_id)
                if numbers["copies"] < borrowed:
                    errors.append(
                        f"Nakala: haziwezi kupungua chini ya {borrowed}, idadi inayokopeshwa kwa sasa."
                    )
            if not errors:
                data = (
                    values["title"],
                    values["author"],
                    values["category"],
                    numbers["publication_year"],
                    numbers["copies"],
                )
                if book_id is None:
                    get_db().execute(
                        "INSERT INTO books (title, author, category, publication_year, copies) VALUES (?, ?, ?, ?, ?)",
                        data,
                    )
                else:
                    get_db().execute(
                        "UPDATE books SET title=?, author=?, category=?, publication_year=?, copies=? WHERE id=?",
                        data + (book_id,),
                    )
                get_db().commit()
                flash(translate("Taarifa za kitabu zimehifadhiwa."))
                return redirect(url_for("index"))
        return render_template(
            "form.html",
            values=values,
            errors=errors,
            editing=book_id is not None,
            current_year=date.today().year,
        )

    @app.route("/books/<int:book_id>/delete", methods=["GET", "POST"])
    def delete_book(book_id):
        book = book_or_404(book_id)
        has_loans = (
            get_db()
            .execute("SELECT count(*) FROM loans WHERE book_id = ?", (book_id,))
            .fetchone()[0]
            > 0
        )
        if request.method == "POST":
            if has_loans:
                flash("Kitabu hiki kina historia ya uazimaji; hakiwezi kufutwa.")
            else:
                get_db().execute("DELETE FROM books WHERE id=?", (book_id,))
                get_db().commit()
                flash(translate("Kitabu kimefutwa."))
            return redirect(url_for("index"))
        return render_template("delete.html", book=book, has_loans=has_loans)
