"""Authentication routes and request guards."""

import secrets
import time
from urllib.parse import urlsplit

from flask import abort, flash, redirect, render_template, request, session, url_for

from i18n import LANGUAGES, translate

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 300
FAILURE_WINDOW = 600
LOCKOUT_MESSAGE = "Majaribio mengi yamefanywa. Jaribu tena baada ya {seconds} sekunde."
CSRF_EXPIRED_MESSAGE = "Fomu imeisha muda. Fungua ukurasa tena."


def _same(first, second):
    # compare_digest ina-hit TypeError kwa herufi za non-ASCII; encoding inazuia
    return secrets.compare_digest(first.encode("utf-8"), second.encode("utf-8"))


def _safe_next(target):
    # inarudisha URL ya ndani tu — inazuia open redirect
    if not target:
        return ""
    parts = urlsplit(target)
    if parts.scheme or parts.netloc or not parts.path.startswith("/"):
        return ""
    if "\\" in target:  # vivinjari vyao hutengua "/" kuwa "//"
        return ""
    return target


def register(app):
    attempts = {}

    def _clear_expired(now):
        for key in [
            key
            for key, entry in attempts.items()
            if entry[2] <= now and now - entry[1] > FAILURE_WINDOW
        ]:
            del attempts[key]

    @app.before_request
    def protect_forms():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(32)
        if request.method == "POST":
            token = request.form.get("csrf_token", "")
            if not _same(token, session["csrf_token"]):
                abort(400, CSRF_EXPIRED_MESSAGE)

    @app.before_request
    def require_login():
        if request.endpoint in (None, "login", "static", "set_language") or session.get(
            "logged_in"
        ):
            return
        target = request.full_path.rstrip("?") if request.method == "GET" else request.path
        return redirect(url_for("login", next=target))

    @app.errorhandler(400)
    def bad_request(error):
        return (
            render_template(
                "error.html",
                code=400,
                message=translate(CSRF_EXPIRED_MESSAGE),
            ),
            400,
        )

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        username = ""
        next_url = _safe_next(
            request.form.get("next") or request.args.get("next") or ""
        )
        key = request.remote_addr or "unknown"
        max_attempts = app.config.get("LOGIN_MAX_ATTEMPTS", MAX_LOGIN_ATTEMPTS)
        lockout_seconds = app.config.get("LOGIN_LOCKOUT_SECONDS", LOCKOUT_SECONDS)
        now = time.time()
        fails, last_ts, until = attempts.get(key, (0, 0.0, 0.0))
        if until and until <= now:
            fails, until = 0, 0.0  # kifungu kimeisha — hesabu upya
        if now - last_ts > FAILURE_WINDOW:
            fails = 0
        if until > now:
            seconds = int(until - now) + 1
            error = translate(LOCKOUT_MESSAGE).format(seconds=seconds)
            status = 429 if request.method == "POST" else 200
            return (
                render_template(
                    "login.html", error=error, username="", next_url=next_url
                ),
                status,
            )
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            username_ok = _same(username, app.config["LIBRARIAN_USERNAME"])
            password_ok = _same(password, app.config["LIBRARIAN_PASSWORD"])
            if username_ok and password_ok:
                attempts.pop(key, None)
                language = session.get("language")
                session.clear()
                session.permanent = True
                session["logged_in"] = True
                if language:
                    session["language"] = language
                session["csrf_token"] = secrets.token_hex(32)
                flash(translate("Umeingia."))
                return redirect(next_url or url_for("index"))
            fails += 1
            attempts[key] = (fails, now, 0.0)
            if fails >= max_attempts:
                until = now + lockout_seconds
                attempts[key] = (fails, now, until)
                if len(attempts) > 500:
                    _clear_expired(now)
                error = translate(LOCKOUT_MESSAGE).format(seconds=lockout_seconds)
                return (
                    render_template(
                        "login.html", error=error, username=username, next_url=next_url
                    ),
                    429,
                )
            error = translate("Jina la mtumiaji au nenosiri si sahihi.")
        return render_template("login.html", error=error, username=username, next_url=next_url)

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
