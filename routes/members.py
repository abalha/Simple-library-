"""Member registration and management routes."""

import sqlite3

from flask import abort, flash, redirect, render_template, request, url_for

from database import get_db
from i18n import translate


def member_or_404(member_id):
    member = (
        get_db().execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()
    )
    if member is None:
        abort(404)
    return member


def register(app):
    @app.get("/members")
    def members():
        query = request.args.get("q", "").strip()
        rows = (
            get_db()
            .execute(
                """SELECT * FROM members
            WHERE instr(lower(member_number), lower(?)) > 0 OR instr(lower(full_name), lower(?)) > 0
            ORDER BY full_name, id""",
                (query, query),
            )
            .fetchall()
        )
        totals = (
            get_db()
            .execute(
                "SELECT count(*) AS members, coalesce(sum(status = 'active'), 0) AS active FROM members"
            )
            .fetchone()
        )
        return render_template("members.html", members=rows, query=query, totals=totals)

    @app.route("/members/new", methods=["GET", "POST"])
    @app.route("/members/<int:member_id>/edit", methods=["GET", "POST"])
    def edit_member(member_id=None):
        member = member_or_404(member_id) if member_id is not None else None
        editing = member_id is not None
        values = dict(member) if member is not None else {"status": "active"}
        errors = []
        if request.method == "POST":
            values = {
                key: request.form.get(key, "").strip()
                for key in ("member_number", "full_name", "member_type", "status")
            }
            values["member_number"] = values["member_number"].upper()
            if not editing:
                values["status"] = "active"
            if not values["member_number"] or len(values["member_number"]) > 50:
                errors.append("Namba ya mwanachama: jaza herufi 1 hadi 50.")
            if not values["full_name"] or len(values["full_name"]) > 150:
                errors.append("Jina kamili: jaza herufi 1 hadi 150.")
            if values["member_type"] not in ("student", "teacher"):
                errors.append("Aina ya mwanachama: chagua mwanafunzi au mwalimu.")
            if values["status"] not in ("active", "inactive"):
                errors.append("Hali: chagua active au inactive.")
            if not errors:
                data = (
                    values["member_number"],
                    values["full_name"],
                    values["member_type"],
                    values["status"],
                )
                try:
                    if member_id is None:
                        get_db().execute(
                            "INSERT INTO members (member_number, full_name, member_type, status) VALUES (?, ?, ?, ?)",
                            data,
                        )
                    else:
                        get_db().execute(
                            "UPDATE members SET member_number=?, full_name=?, member_type=?, status=? WHERE id=?",
                            data + (member_id,),
                        )
                    get_db().commit()
                    flash(translate("Taarifa za mwanachama zimehifadhiwa."))
                    return redirect(url_for("members"))
                except sqlite3.IntegrityError:
                    errors.append(
                        "Namba ya mwanachama hii tayari inatumika na mwanachama mwingine."
                    )
        return render_template(
            "member_form.html", values=values, errors=errors, editing=editing
        )
