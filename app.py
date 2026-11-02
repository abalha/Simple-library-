"""Hatua ya 1: CRUD ya vitabu. Hatua ya 2: Wanachama. Hatua ya 3: Mikopo.
Hatua ya 4: Overdue/faini. Hatua ya 5: Login + ripoti. Endesha kwa python app.py."""
import os
import secrets
import sqlite3
from datetime import date, timedelta
from pathlib import Path
from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for


LOAN_DAYS = 30
MAX_ACTIVE_LOANS = 5
FINE_PER_DAY = 1000
DEFAULT_LIBRARIAN_PASSWORD = 'maktaba2026'


def overdue_days(loan, today):
    due = date.fromisoformat(loan['due_date'])
    end = date.fromisoformat(loan['returned_at']) if loan['returned_at'] else today
    return max(0, (end - due).days)


def create_app(database=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    app.config['DATABASE'] = str(database or Path(__file__).with_name('library.db'))
    app.config['MAX_CONTENT_LENGTH'] = 64 * 1024
    app.config['LIBRARIAN_PASSWORD'] = os.environ.get('LIBRARIAN_PASSWORD') or DEFAULT_LIBRARIAN_PASSWORD

    def db():
        if 'db' not in g:
            g.db = sqlite3.connect(app.config['DATABASE'])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(error):
        connection = g.pop('db', None)
        if connection is not None:
            connection.close()

    with app.app_context():
        db().execute('''CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL,
            publication_year INTEGER NOT NULL CHECK(publication_year >= 1),
            copies INTEGER NOT NULL CHECK(copies >= 0)
        )''')
        db().execute('''CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY,
            member_number TEXT NOT NULL CHECK(length(member_number) <= 50),
            full_name TEXT NOT NULL CHECK(length(full_name) <= 150),
            member_type TEXT NOT NULL CHECK(member_type IN ('student', 'teacher')),
            status TEXT NOT NULL CHECK(status IN ('active', 'inactive')) DEFAULT 'active',
            UNIQUE(member_number COLLATE NOCASE)
        )''')
        db().execute('''CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL REFERENCES books(id),
            member_id INTEGER NOT NULL REFERENCES members(id),
            borrowed_at TEXT NOT NULL,
            due_date TEXT NOT NULL,
            returned_at TEXT
        )''')
        db().commit()

    @app.before_request
    def protect_forms():
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)
        if request.method == 'POST':
            token = request.form.get('csrf_token', '')
            if not secrets.compare_digest(token, session['csrf_token']):
                abort(400, 'Fomu imeisha muda. Fungua ukurasa tena.')

    @app.before_request
    def require_login():
        if request.endpoint in (None, 'login', 'static') or session.get('logged_in'):
            return
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            password = request.form.get('password', '')
            if secrets.compare_digest(password, app.config['LIBRARIAN_PASSWORD']):
                session['logged_in'] = True
                flash('Umeingia.')
                return redirect(url_for('index'))
            error = 'Password si sahihi.'
        return render_template('login.html', error=error)

    @app.get('/logout')
    def logout():
        session.pop('logged_in', None)
        flash('Umetoka.')
        return redirect(url_for('login'))

    def book_or_404(book_id):
        book = db().execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        if book is None:
            abort(404)
        return book

    def member_or_404(member_id):
        member = db().execute('SELECT * FROM members WHERE id = ?', (member_id,)).fetchone()
        if member is None:
            abort(404)
        return member

    def loan_or_404(loan_id):
        loan = db().execute('SELECT * FROM loans WHERE id = ?', (loan_id,)).fetchone()
        if loan is None:
            abort(404)
        return loan

    def active_loans_for_book(book_id):
        return db().execute('SELECT count(*) FROM loans WHERE book_id = ? AND returned_at IS NULL', (book_id,)).fetchone()[0]

    def active_loans_for_member(member_id):
        return db().execute('SELECT count(*) FROM loans WHERE member_id = ? AND returned_at IS NULL', (member_id,)).fetchone()[0]

    def member_has_overdue(member_id):
        return db().execute('''SELECT count(*) FROM loans
            WHERE member_id = ? AND returned_at IS NULL AND due_date < ?''',
            (member_id, date.today().isoformat())).fetchone()[0] > 0

    @app.get('/')
    def index():
        query = request.args.get('q', '').strip()
        books = db().execute('''SELECT books.*, books.copies - coalesce(
                (SELECT count(*) FROM loans WHERE loans.book_id = books.id AND loans.returned_at IS NULL), 0) AS available
            FROM books
            WHERE instr(lower(title), lower(?)) > 0
               OR instr(lower(author), lower(?)) > 0
            ORDER BY title, id''', (query, query)).fetchall()
        totals = db().execute('SELECT count(*) AS titles, coalesce(sum(copies), 0) AS copies FROM books').fetchone()
        return render_template('index.html', books=books, query=query, totals=totals)

    @app.route('/books/new', methods=['GET', 'POST'])
    @app.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
    def edit_book(book_id=None):
        book = book_or_404(book_id) if book_id is not None else None
        values = dict(book) if book is not None else {}
        errors = []
        if request.method == 'POST':
            values = {key: request.form.get(key, '').strip() for key in
                      ('title', 'author', 'category', 'publication_year', 'copies')}
            for key, label in [('title', 'Jina'), ('author', 'Mwandishi'), ('category', 'Aina')]:
                if not values[key] or len(values[key]) > 150:
                    errors.append(f'{label}: jaza herufi 1 hadi 150.')
            numbers = {}
            for key, label, minimum, maximum in [
                ('publication_year', 'Mwaka', 1, date.today().year),
                ('copies', 'Nakala', 0, 1000000),
            ]:
                try:
                    numbers[key] = int(values[key])
                    if not minimum <= numbers[key] <= maximum:
                        raise ValueError
                except ValueError:
                    errors.append(f'{label}: jaza namba kamili kati ya {minimum} na {maximum}.')
            if book_id is not None and 'copies' in numbers:
                borrowed = active_loans_for_book(book_id)
                if numbers['copies'] < borrowed:
                    errors.append(f'Nakala: haziwezi kupungua chini ya {borrowed}, idadi inayokopeshwa kwa sasa.')
            if not errors:
                data = (values['title'], values['author'], values['category'],
                        numbers['publication_year'], numbers['copies'])
                if book_id is None:
                    db().execute('INSERT INTO books (title, author, category, publication_year, copies) VALUES (?, ?, ?, ?, ?)', data)
                else:
                    db().execute('UPDATE books SET title=?, author=?, category=?, publication_year=?, copies=? WHERE id=?', data + (book_id,))
                db().commit()
                flash('Taarifa za kitabu zimehifadhiwa.')
                return redirect(url_for('index'))
        return render_template('form.html', values=values, errors=errors, editing=book_id is not None, current_year=date.today().year)

    @app.route('/books/<int:book_id>/delete', methods=['GET', 'POST'])
    def delete_book(book_id):
        book = book_or_404(book_id)
        has_loans = db().execute('SELECT count(*) FROM loans WHERE book_id = ?', (book_id,)).fetchone()[0] > 0
        if request.method == 'POST':
            if has_loans:
                flash('Kitabu hiki kina historia ya mikopo; hakiwezi kufutwa.')
                return redirect(url_for('index'))
            db().execute('DELETE FROM books WHERE id=?', (book_id,))
            db().commit()
            flash('Kitabu kimefutwa.')
            return redirect(url_for('index'))
        return render_template('delete.html', book=book, has_loans=has_loans)

    @app.get('/members')
    def members():
        query = request.args.get('q', '').strip()
        rows = db().execute('''SELECT * FROM members
            WHERE instr(lower(member_number), lower(?)) > 0
               OR instr(lower(full_name), lower(?)) > 0
            ORDER BY full_name, id''', (query, query)).fetchall()
        totals = db().execute('''SELECT count(*) AS members,
            coalesce(sum(status = 'active'), 0) AS active
            FROM members''').fetchone()
        return render_template('members.html', members=rows, query=query, totals=totals)

    @app.route('/members/new', methods=['GET', 'POST'])
    @app.route('/members/<int:member_id>/edit', methods=['GET', 'POST'])
    def edit_member(member_id=None):
        member = member_or_404(member_id) if member_id is not None else None
        editing = member_id is not None
        values = dict(member) if member is not None else {'status': 'active'}
        errors = []
        if request.method == 'POST':
            values = {key: request.form.get(key, '').strip() for key in
                      ('member_number', 'full_name', 'member_type', 'status')}
            values['member_number'] = values['member_number'].upper()
            if not editing:
                values['status'] = 'active'
            if not values['member_number'] or len(values['member_number']) > 50:
                errors.append('Namba ya mwanachama: jaza herufi 1 hadi 50.')
            if not values['full_name'] or len(values['full_name']) > 150:
                errors.append('Jina kamili: jaza herufi 1 hadi 150.')
            if values['member_type'] not in ('student', 'teacher'):
                errors.append('Aina ya mwanachama: chagua mwanafunzi au mwalimu.')
            if values['status'] not in ('active', 'inactive'):
                errors.append('Hali: chagua active au inactive.')
            if not errors:
                data = (values['member_number'], values['full_name'], values['member_type'], values['status'])
                try:
                    if member_id is None:
                        db().execute('''INSERT INTO members (member_number, full_name, member_type, status)
                            VALUES (?, ?, ?, ?)''', data)
                    else:
                        db().execute('''UPDATE members SET member_number=?, full_name=?, member_type=?, status=?
                            WHERE id=?''', data + (member_id,))
                    db().commit()
                    flash('Taarifa za mwanachama zimehifadhiwa.')
                    return redirect(url_for('members'))
                except sqlite3.IntegrityError:
                    errors.append('Namba ya mwanachama hii tayari inatumika na mwanachama mwingine.')
        return render_template('member_form.html', values=values, errors=errors, editing=editing)

    @app.get('/loans')
    def loans():
        rows = db().execute('''SELECT loans.*, books.title AS book_title, books.author AS book_author,
            members.member_number AS member_number, members.full_name AS member_name
            FROM loans
            JOIN books ON books.id = loans.book_id
            JOIN members ON members.id = loans.member_id
            ORDER BY (loans.returned_at IS NOT NULL), loans.borrowed_at DESC, loans.id DESC''').fetchall()
        today = date.today()
        enriched = []
        for row in rows:
            loan = dict(row)
            loan['overdue_days'] = overdue_days(row, today)
            loan['fine'] = loan['overdue_days'] * FINE_PER_DAY
            enriched.append(loan)
        active_count = db().execute('SELECT count(*) FROM loans WHERE returned_at IS NULL').fetchone()[0]
        overdue_count = db().execute('''SELECT count(*) FROM loans
            WHERE returned_at IS NULL AND due_date < ?''', (today.isoformat(),)).fetchone()[0]
        return render_template('loans.html', loans=enriched, active_count=active_count,
                                overdue_count=overdue_count, today=today.isoformat(), fine_per_day=FINE_PER_DAY)

    @app.route('/loans/new', methods=['GET', 'POST'])
    def new_loan():
        books_with_availability = db().execute('''SELECT books.*, books.copies - coalesce(
                (SELECT count(*) FROM loans WHERE loans.book_id = books.id AND loans.returned_at IS NULL), 0) AS available
            FROM books ORDER BY title''').fetchall()
        values = {}
        errors = []
        if request.method == 'POST':
            values = {key: request.form.get(key, '').strip() for key in ('member_number', 'book_id')}
            values['member_number'] = values['member_number'].upper()
            member = db().execute('SELECT * FROM members WHERE member_number = ? COLLATE NOCASE', (values['member_number'],)).fetchone()
            book = db().execute('SELECT * FROM books WHERE id = ?', (values['book_id'],)).fetchone() if values['book_id'].isdigit() else None
            if member is None:
                errors.append('Namba ya mwanachama haipo. Hakiki namba au msajili mwanachama kwanza.')
            elif member['status'] != 'active':
                errors.append('Mwanachama huyu si hai (inactive); hawezi kukopa kitabu.')
            elif member_has_overdue(member['id']):
                errors.append('Mwanachama huyu ana mkopo uliochelewa ambao bado hajarejesha; hawezi kukopa kingine mpaka arejeshe uliopo.')
            elif active_loans_for_member(member['id']) >= MAX_ACTIVE_LOANS:
                errors.append(f'Mwanachama huyu ana mikopo {MAX_ACTIVE_LOANS} ambayo bado hajarejesha; hawezi kukopa kingine.')
            if book is None:
                errors.append('Chagua kitabu halali.')
            elif active_loans_for_book(book['id']) >= book['copies']:
                errors.append('Hakuna nakala za kitabu hiki zilizobaki kwa sasa.')
            if not errors:
                borrowed_at = date.today()
                due_date = borrowed_at + timedelta(days=LOAN_DAYS)
                db().execute('''INSERT INTO loans (book_id, member_id, borrowed_at, due_date)
                    VALUES (?, ?, ?, ?)''', (book['id'], member['id'], borrowed_at.isoformat(), due_date.isoformat()))
                db().commit()
                flash('Kitabu kimekopeshwa.')
                return redirect(url_for('loans'))
        return render_template('loan_form.html', values=values, errors=errors, books=books_with_availability, loan_days=LOAN_DAYS)

    @app.route('/loans/<int:loan_id>/return', methods=['GET', 'POST'])
    def return_loan(loan_id):
        loan = loan_or_404(loan_id)
        book = db().execute('SELECT * FROM books WHERE id = ?', (loan['book_id'],)).fetchone()
        member = db().execute('SELECT * FROM members WHERE id = ?', (loan['member_id'],)).fetchone()
        if loan['returned_at'] is not None:
            flash('Kitabu hiki tayari kimerejeshwa.')
            return redirect(url_for('loans'))
        today = date.today()
        days_late = overdue_days(loan, today)
        if request.method == 'POST':
            db().execute('UPDATE loans SET returned_at = ? WHERE id = ?', (today.isoformat(), loan_id))
            db().commit()
            if days_late > 0:
                flash(f'Kitabu kimerejeshwa. Kimechelewa siku {days_late}; faini TZS {days_late * FINE_PER_DAY}.')
            else:
                flash('Kitabu kimerejeshwa.')
            return redirect(url_for('loans'))
        return render_template('loan_return.html', loan=loan, book=book, member=member,
                                days_late=days_late, fine=days_late * FINE_PER_DAY)

    @app.get('/reports/books')
    def books_report():
        books_rows = db().execute('''SELECT books.*, books.copies - coalesce(
                (SELECT count(*) FROM loans WHERE loans.book_id = books.id AND loans.returned_at IS NULL), 0) AS available
            FROM books ORDER BY title''').fetchall()
        totals = db().execute('''SELECT count(*) AS titles, coalesce(sum(copies), 0) AS copies,
                coalesce(sum(copies - (SELECT count(*) FROM loans
                    WHERE loans.book_id = books.id AND loans.returned_at IS NULL)), 0) AS available
            FROM books''').fetchone()
        return render_template('books_report.html', books=books_rows, totals=totals, generated_at=date.today().isoformat())

    return app


if __name__ == '__main__':
    create_app().run(host='127.0.0.1', port=5000)
