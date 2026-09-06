import sqlite3
from werkzeug.security import generate_password_hash

DATABASE_PATH = 'spendly.db'

def get_db():
    """
    Opens connection to spendly.db, sets row_factory to sqlite3.Row,
    and enables foreign key constraints.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """
    Creates users and expenses tables using CREATE TABLE IF NOT EXISTS.
    """
    conn = get_db()
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    date TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
            """)
    finally:
        conn.close()

def seed_db():
    """
    Inserts a demo user and sample expenses if the database is empty.
    """
    conn = get_db()
    try:
        with conn:
            # Check if users table already contains data
            user_exists = conn.execute("SELECT 1 FROM users LIMIT 1").fetchone()
            if user_exists:
                return

            # Insert demo user
            demo_password = generate_password_hash("demo123")
            cursor = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ("Demo User", "demo@spendly.com", demo_password)
            )
            user_id = cursor.lastrowid

            # Generate 8 sample expenses
            # Spread dates across current month (using a few sample dates)
            sample_expenses = [
                (user_id, 12.50, "Food", "2026-09-01", "Lunch at cafe"),
                (user_id, 45.00, "Transport", "2026-09-02", "Fuel refill"),
                (user_id, 80.00, "Bills", "2026-09-03", "Electricity bill"),
                (user_id, 25.00, "Health", "2026-09-04", "Pharmacy"),
                (user_id, 60.00, "Entertainment", "2026-09-05", "Movie ticket"),
                (user_id, 120.00, "Shopping", "2026-09-06", "Grocery shopping"),
                (user_id, 10.00, "Other", "2026-09-07", "Parking fee"),
                (user_id, 15.00, "Food", "2026-09-08", "Dinner"),
            ]

            conn.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                sample_expenses
            )
    finally:
        conn.close()
