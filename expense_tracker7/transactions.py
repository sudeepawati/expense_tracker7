from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from .auth import login_required
from .db import get_db

transactions_bp = Blueprint("transactions", __name__)
CATEGORIES = ("Food", "Travel", "Shopping", "Bills", "Health", "Entertainment", "Other")
KINDS = {"income": "Income", "expense": "Expense"}


def parse_transaction_form():
    kind = request.form.get("kind", "")
    category = request.form.get("category", "")
    description = request.form.get("description", "").strip()
    raw_amount = request.form.get("amount", "").strip()
    raw_date = request.form.get("transaction_date", "").strip()
    errors = []

    if kind not in KINDS:
        errors.append("Choose income or expense.")
    if category not in CATEGORIES:
        errors.append("Choose a valid category.")
    if not description or len(description) > 120:
        errors.append("Description must be between 1 and 120 characters.")
    try:
        amount = Decimal(raw_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if not amount.is_finite() or amount <= 0 or amount > Decimal("999999999.99"):
            raise InvalidOperation
        amount_cents = int(amount * 100)
    except (InvalidOperation, ValueError):
        amount_cents = 0
        errors.append("Enter an amount greater than 0 and no more than 999,999,999.99.")
    try:
        transaction_date = date.fromisoformat(raw_date)
    except ValueError:
        transaction_date = None
        errors.append("Choose a valid transaction date.")

    return {
        "kind": kind,
        "category": category,
        "description": description,
        "amount": raw_amount,
        "transaction_date": raw_date,
        "amount_cents": amount_cents,
    }, errors


def get_owned_transaction(transaction_id):
    transaction = get_db().execute(
        "SELECT * FROM transactions WHERE id = ? AND user_id = ?",
        (transaction_id, session["user_id"]),
    ).fetchone()
    if transaction is None:
        abort(404)
    return transaction


@transactions_bp.get("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    totals = get_db().execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN kind = 'income' THEN amount ELSE 0 END), 0) AS income,
            COALESCE(SUM(CASE WHEN kind = 'expense' THEN amount ELSE 0 END), 0) AS expenses
        FROM transactions WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()
    recent = get_db().execute(
        "SELECT * FROM transactions WHERE user_id = ? "
        "ORDER BY transaction_date DESC, id DESC LIMIT 6",
        (user_id,),
    ).fetchall()
    monthly = get_db().execute(
        """
        SELECT substr(transaction_date, 1, 7) AS month,
               SUM(CASE WHEN kind = 'income' THEN amount ELSE 0 END) AS income,
               SUM(CASE WHEN kind = 'expense' THEN amount ELSE 0 END) AS expenses
        FROM transactions
        WHERE user_id = ? AND transaction_date >= date('now', '-5 months', 'start of month')
        GROUP BY month ORDER BY month
        """,
        (user_id,),
    ).fetchall()
    return render_template(
        "dashboard.html",
        income=totals["income"] / 100,
        expenses=totals["expenses"] / 100,
        balance=(totals["income"] - totals["expenses"]) / 100,
        recent=recent,
        chart_labels=[row["month"] for row in monthly],
        chart_income=[row["income"] / 100 for row in monthly],
        chart_expenses=[row["expenses"] / 100 for row in monthly],
    )


@transactions_bp.get("/transactions")
@login_required
def transaction_list():
    conditions = ["user_id = ?"]
    values = [session["user_id"]]
    search = request.args.get("q", "").strip()[:100]
    kind = request.args.get("kind", "")
    category = request.args.get("category", "")
    month = request.args.get("month", "")

    if search:
        conditions.append("(description LIKE ? OR category LIKE ?)")
        values.extend([f"%{search}%", f"%{search}%"])
    if kind in KINDS:
        conditions.append("kind = ?")
        values.append(kind)
    if category in CATEGORIES:
        conditions.append("category = ?")
        values.append(category)
    if month:
        try:
            date.fromisoformat(f"{month}-01")
        except ValueError:
            month = ""
        else:
            conditions.append("substr(transaction_date, 1, 7) = ?")
            values.append(month)

    rows = get_db().execute(
        f"SELECT * FROM transactions WHERE {' AND '.join(conditions)} "
        "ORDER BY transaction_date DESC, id DESC",
        values,
    ).fetchall()
    return render_template(
        "transactions.html",
        transactions=rows,
        categories=CATEGORIES,
        selected_kind=kind,
        selected_category=category,
        selected_month=month,
        search=search,
    )


@transactions_bp.route("/transactions/add", methods=("GET", "POST"))
@login_required
def add_transaction():
    form = {}
    if request.method == "POST":
        form, errors = parse_transaction_form()
        if errors:
            for error in errors:
                flash(error, "error")
        else:
            database = get_db()
            database.execute(
                """
                INSERT INTO transactions
                    (user_id, kind, amount, category, description, transaction_date)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    form["kind"],
                    form["amount_cents"],
                    form["category"],
                    form["description"],
                    form["transaction_date"],
                ),
            )
            database.commit()
            flash("Transaction added.", "success")
            return redirect(url_for("transactions.transaction_list"))
    return render_template(
        "transaction_form.html", transaction=form, categories=CATEGORIES, page_title="Add transaction"
    )


@transactions_bp.route("/transactions/<int:transaction_id>/edit", methods=("GET", "POST"))
@login_required
def edit_transaction(transaction_id):
    transaction = get_owned_transaction(transaction_id)
    if request.method == "POST":
        form, errors = parse_transaction_form()
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "transaction_form.html",
                transaction=form,
                categories=CATEGORIES,
                page_title="Edit transaction",
            ), 400
        database = get_db()
        database.execute(
            """
            UPDATE transactions
            SET kind = ?, amount = ?, category = ?, description = ?, transaction_date = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                form["kind"],
                form["amount_cents"],
                form["category"],
                form["description"],
                form["transaction_date"],
                transaction_id,
                session["user_id"],
            ),
        )
        database.commit()
        flash("Transaction updated.", "success")
        return redirect(url_for("transactions.transaction_list"))
    return render_template(
        "transaction_form.html",
        transaction={
            **dict(transaction),
            "amount": f'{transaction["amount"] / 100:.2f}',
        },
        categories=CATEGORIES,
        page_title="Edit transaction",
    )


@transactions_bp.post("/transactions/<int:transaction_id>/delete")
@login_required
def delete_transaction(transaction_id):
    get_owned_transaction(transaction_id)
    database = get_db()
    database.execute(
        "DELETE FROM transactions WHERE id = ? AND user_id = ?",
        (transaction_id, session["user_id"]),
    )
    database.commit()
    flash("Transaction deleted.", "success")
    return redirect(url_for("transactions.transaction_list"))
