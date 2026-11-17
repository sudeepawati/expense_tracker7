from datetime import date

from flask import Blueprint, render_template, request, session

from .auth import login_required
from .db import get_db

reports_bp = Blueprint("reports", __name__)


@reports_bp.get("/reports")
@login_required
def monthly_report():
    selected_month = request.args.get("month", date.today().strftime("%Y-%m"))
    try:
        date.fromisoformat(f"{selected_month}-01")
    except ValueError:
        selected_month = date.today().strftime("%Y-%m")

    user_id = session["user_id"]
    database = get_db()
    summary = database.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN kind = 'income' THEN amount ELSE 0 END), 0) AS income,
            COALESCE(SUM(CASE WHEN kind = 'expense' THEN amount ELSE 0 END), 0) AS expenses
        FROM transactions
        WHERE user_id = ? AND substr(transaction_date, 1, 7) = ?
        """,
        (user_id, selected_month),
    ).fetchone()
    categories = database.execute(
        """
        SELECT category, SUM(amount) AS total
        FROM transactions
        WHERE user_id = ? AND kind = 'expense'
          AND substr(transaction_date, 1, 7) = ?
        GROUP BY category ORDER BY total DESC
        """,
        (user_id, selected_month),
    ).fetchall()
    days = database.execute(
        """
        SELECT substr(transaction_date, 9, 2) AS day, SUM(amount) AS total
        FROM transactions
        WHERE user_id = ? AND kind = 'expense'
          AND substr(transaction_date, 1, 7) = ?
        GROUP BY day ORDER BY day
        """,
        (user_id, selected_month),
    ).fetchall()
    return render_template(
        "reports.html",
        selected_month=selected_month,
        income=summary["income"] / 100,
        expenses=summary["expenses"] / 100,
        balance=(summary["income"] - summary["expenses"]) / 100,
        categories=categories,
        category_labels=[row["category"] for row in categories],
        category_values=[row["total"] / 100 for row in categories],
        day_labels=[row["day"] for row in days],
        day_values=[row["total"] / 100 for row in days],
    )
