<<<<<<< HEAD
# Expense Tracker

A beginner-friendly expense tracker built with Flask, SQLite, HTML, CSS, and JavaScript. It supports account registration, private transaction records, search and filters, a dashboard, and monthly reports with charts.

## Project structure

```text
expense-tracker/
|-- expense_tracker/
|   |-- __init__.py          # Creates and configures the Flask application
|   |-- auth.py              # Registration, login, logout, and form protection
|   |-- db.py                # SQLite connection and database tables
|   |-- reports.py           # Monthly summaries and chart data
|   |-- transactions.py      # Dashboard and transaction CRUD/search
|   |-- static/
|   |   |-- css/style.css    # Responsive styles
|   |   `-- js/app.js        # Small interface interactions
|   `-- templates/           # HTML pages
|-- instance/                # Created automatically; holds the SQLite database
|-- .env.example
|-- .gitignore
|-- requirements.txt
|-- run.py
`-- README.md
```

## Run it in VS Code (Windows)

1. Open this project folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use the VS Code Command Prompt terminal and run:
   `.venv\Scripts\activate.bat`.

4. Install Flask:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Set a secret key for this terminal session. Replace the sample with a long random value:

   ```powershell
   $env:FLASK_SECRET_KEY = "put-a-long-random-secret-here"
   ```

6. Start the website:

   ```powershell
   python run.py
   ```

7. Open the local URL printed by Flask (usually `http://127.0.0.1:5000`) in your browser and create an account.

The SQLite database and its tables are created automatically in `instance/` the first time the app starts. Keep the terminal open while you use the app; press **Ctrl+C** to stop it.

## Features

- Register and sign in with a username or email; passwords are stored as secure hashes.
- Dashboard totals show all-time income, expenses, and balance.
- Add, edit, and delete transactions. Amounts are stored as integer cents to avoid common decimal rounding errors.
- Income and expense types, seven categories, and transaction dates.
- Search by description/category and filter by type, category, or month.
- Monthly income/expense totals, category breakdown, and daily spending chart.
- Responsive layout for desktop and mobile.
- User-specific database queries and CSRF protection for submitted forms.

## GitHub setup

Git is available in the VS Code terminal. To publish your project:

1. Create a new, empty repository on GitHub (do not add a README there, since this folder already has one).
2. From this folder, run:

   ```powershell
   git init
   git add .
   git commit -m "Build expense tracker application"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
   git push -u origin main
   ```

Replace the remote URL with your own. The local database, virtual environment, and `.env` file are excluded by `.gitignore`; never commit passwords, secret keys, or personal transaction data.

## Beginner module guide

1. **Database (`db.py`)** — creates the users and transactions tables and opens a SQLite connection when needed.
2. **Authentication (`auth.py`)** — validates account forms, hashes passwords, manages the login session, and protects POST forms.
3. **Transactions (`transactions.py`)** — checks form data and implements the dashboard and add/edit/delete/search/filter routes.
4. **Reports (`reports.py`)** — calculates totals for a selected month and prepares data for the charts.
5. **Templates and static files** — render the pages (`templates/`), apply responsive styling (`static/css/`), and enhance the interface (`static/js/`).

For a real public deployment, configure a strong secret key, use HTTPS, and choose a production-ready hosting setup.
=======
# expense_tracker7
>>>>>>> b962b1639776b2e1462e1fba5f0cce48031579c9
