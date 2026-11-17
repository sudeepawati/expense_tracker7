import os
from pathlib import Path

from flask import Flask, redirect, render_template, session, url_for

from .db import close_db, init_db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me"),
        DATABASE=os.environ.get(
            "DATABASE_PATH", str(Path(app.instance_path) / "expense_tracker.sqlite3")
        ),
    )
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(close_db)
    init_db(app)

    from .auth import auth_bp
    from .reports import reports_bp
    from .transactions import transactions_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(reports_bp)

    @app.context_processor
    def inject_template_values():
        return {"current_user": session.get("username")}

    @app.get("/")
    def index():
        if session.get("user_id"):
            return redirect(url_for("transactions.dashboard"))
        return render_template("home.html")

    return app
