import re
import secrets
from functools import wraps

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user_id") is None:
            flash("Please log in to continue.", "info")
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


@auth_bp.before_app_request
def protect_post_requests():
    if request.method == "POST":
        submitted_token = request.form.get("csrf_token", "")
        session_token = session.get("csrf_token", "")
        if not session_token or not secrets.compare_digest(submitted_token, session_token):
            return "Your form expired or could not be verified. Please go back and try again.", 400


@auth_bp.app_context_processor
def csrf_context():
    def csrf_token():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(32)
        return session["csrf_token"]

    return {"csrf_token": csrf_token}


@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = get_db().execute(
        "SELECT id, username, email FROM users WHERE id = ?", (user_id,)
    ).fetchone() if user_id else None


@auth_bp.get("/register")
def register():
    return render_template("auth/register.html")


@auth_bp.post("/register")
def register_post():
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    error = None

    if not re.fullmatch(r"[A-Za-z0-9_]{3,30}", username):
        error = "Username must be 3–30 characters using letters, numbers, or underscores."
    elif len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        error = "Enter a valid email address."
    elif len(password) < 8:
        error = "Password must be at least 8 characters."

    database = get_db()
    if error is None:
        existing = database.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?", (username, email)
        ).fetchone()
        if existing:
            error = "That username or email is already registered."

    if error:
        flash(error, "error")
        return render_template("auth/register.html", username=username, email=email), 400

    cursor = database.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, generate_password_hash(password)),
    )
    database.commit()
    session.clear()
    session["user_id"] = cursor.lastrowid
    session["username"] = username
    flash("Your account is ready. Welcome!", "success")
    return redirect(url_for("transactions.dashboard"))


@auth_bp.get("/login")
def login():
    return render_template("auth/login.html")


@auth_bp.post("/login")
def login_post():
    identity = request.form.get("identity", "").strip()
    password = request.form.get("password", "")
    user = get_db().execute(
        "SELECT * FROM users WHERE username = ? OR email = ?", (identity, identity)
    ).fetchone()
    if user is None or not check_password_hash(user["password_hash"], password):
        flash("The email/username or password is incorrect.", "error")
        return render_template("auth/login.html", identity=identity), 400

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    flash("Welcome back!", "success")
    return redirect(url_for("transactions.dashboard"))


@auth_bp.post("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
