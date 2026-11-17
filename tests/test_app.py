import re
import tempfile
import unittest
from pathlib import Path

from expense_tracker import create_app


class ExpenseTrackerTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-secret",
                "DATABASE": str(Path(self.temp_dir.name) / "test.sqlite3"),
            }
        )
        self.client = self.app.test_client()
        self.register()

    def tearDown(self):
        self.temp_dir.cleanup()

    def csrf_token(self, path):
        response = self.client.get(path)
        match = re.search(rb'name="csrf_token" value="([^"]+)', response.data)
        self.assertIsNotNone(match)
        return match.group(1).decode()

    def register(self):
        token = self.csrf_token("/auth/register")
        return self.client.post(
            "/auth/register",
            data={
                "csrf_token": token,
                "username": "sample_user",
                "email": "sample@example.com",
                "password": "password123",
            },
            follow_redirects=True,
        )

    def add_expense(self, description="Lunch", amount="12.34"):
        token = self.csrf_token("/transactions/add")
        return self.client.post(
            "/transactions/add",
            data={
                "csrf_token": token,
                "kind": "expense",
                "amount": amount,
                "category": "Food",
                "description": description,
                "transaction_date": "2026-11-16",
            },
            follow_redirects=True,
        )

    def test_registration_dashboard_and_monthly_report(self):
        response = self.add_expense()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Lunch", response.data)
        self.assertIn(b"12.34", self.client.get("/dashboard").data)
        report = self.client.get("/reports?month=2026-11")
        self.assertEqual(report.status_code, 200)
        self.assertIn(b"Food", report.data)

    def test_user_can_log_out_and_log_back_in(self):
        token = self.csrf_token("/dashboard")
        logged_out = self.client.post(
            "/auth/logout", data={"csrf_token": token}, follow_redirects=True
        )
        self.assertIn(b"Log in", logged_out.data)

        token = self.csrf_token("/auth/login")
        logged_in = self.client.post(
            "/auth/login",
            data={
                "csrf_token": token,
                "identity": "sample@example.com",
                "password": "password123",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Good day", logged_in.data)

    def test_transaction_can_be_searched_edited_and_deleted(self):
        self.add_expense()
        results = self.client.get("/transactions?q=Lunch&kind=expense")
        self.assertIn(b"Lunch", results.data)
        self.assertIn(b"Edit", self.client.get("/transactions").data)

        with self.client.session_transaction() as session:
            user_id = session["user_id"]
        with self.app.app_context():
            from expense_tracker.db import get_db

            row = get_db().execute(
                "SELECT id FROM transactions WHERE user_id = ?", (user_id,)
            ).fetchone()
            transaction_id = row["id"]

        token = self.csrf_token(f"/transactions/{transaction_id}/edit")
        updated = self.client.post(
            f"/transactions/{transaction_id}/edit",
            data={
                "csrf_token": token,
                "kind": "income",
                "amount": "20.00",
                "category": "Other",
                "description": "Refund",
                "transaction_date": "2026-11-17",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Refund", updated.data)
        token = self.csrf_token("/transactions")
        deleted = self.client.post(
            f"/transactions/{transaction_id}/delete",
            data={"csrf_token": token},
            follow_redirects=True,
        )
        self.assertIn(b"No transactions found", deleted.data)

    def test_invalid_amount_is_rejected(self):
        response = self.add_expense(amount="-1")
        self.assertIn(b"Enter an amount greater than 0", response.data)
        self.assertIn(b"No transactions found", self.client.get("/transactions").data)

    def test_post_without_csrf_token_is_rejected(self):
        response = self.client.post("/auth/logout")
        self.assertEqual(response.status_code, 400)

    def test_transactions_require_login(self):
        anonymous = self.app.test_client()
        response = anonymous.get("/transactions")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login", response.location)


if __name__ == "__main__":
    unittest.main()
