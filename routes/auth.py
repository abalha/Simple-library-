"""Authentication routes and request guards."""

import secrets

from flask import abort, flash, redirect, render_template, request, session, url_for

from i18n import LANGUAGES, translate


def register(app):
    @app.before_request
    def protect_forms():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(32)
        if request.method == "POST":
            token = request.form.get("csrf_token", "")
            if not secrets.compare_digest(token, session["csrf_token"]):
                abort(400, "Fomu imeisha muda. Fungua ukurasa tena.")

    @app.before_request
    def require_login():
        if request.endpoint in (None, "login", "static") or session.get("logged_in"):
            return
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        username = ""
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            username_ok = secrets.compare_digest(
                username, app.config["LIBRARIAN_USERNAME"]
            )
            password_ok = secrets.compare_digest(
                password, app.config["LIBRARIAN_PASSWORD"]
            )
            if username_ok and password_ok:
                session.clear()
                session["logged_in"] = True
                session["csrf_token"] = secrets.token_hex(32)
                flash(translate("Umeingia."))
                return redirect(url_for("index"))
            error = translate("Username au password si sahihi.")
        return render_template("login.html", error=error, username=username)

    @app.post("/logout")
    def logout():
        session.pop("logged_in", None)
        flash(translate("Umetoka."))
        return redirect(url_for("login"))

    @app.post("/language/<language>")
    def set_language(language):
        if language in LANGUAGES:
            session["language"] = language
        return redirect(request.referrer or url_for("index"))
