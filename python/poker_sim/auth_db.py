"""
PokerID user storage with SQLite. Prevents duplicate emails.
"""
import sqlite3
import uuid
from pathlib import Path
from typing import Optional

import bcrypt

DB_PATH = Path(__file__).resolve().parent.parent / "poker_users.db"


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    """Create users table if not exists."""
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                username TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email)")


def register(email: str, password: str, username: str) -> dict:
    """
    Register a new user. Username required. Raises ValueError if email already exists.
    Returns { id, email, name }.
    """
    init_db()
    email = email.strip().lower()
    name = (username or "").strip()
    if not name:
        raise ValueError("Display name is required")
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user_id = str(uuid.uuid4())

    with _conn() as c:
        try:
            c.execute(
                "INSERT INTO users (id, email, password_hash, username) VALUES (?, ?, ?, ?)",
                (user_id, email, password_hash, name.strip()),
            )
        except sqlite3.IntegrityError:
            raise ValueError("Email already registered")

    return {"id": user_id, "email": email, "name": name}


def login(email: str, password: str) -> Optional[dict]:
    """
    Verify credentials. Returns { id, email, name } or None if invalid.
    """
    init_db()
    email = email.strip().lower()

    with _conn() as c:
        row = c.execute(
            "SELECT id, email, password_hash, username FROM users WHERE email = ?",
            (email,),
        ).fetchone()

    if not row:
        return None
    if not bcrypt.checkpw(password.encode("utf-8"), row["password_hash"].encode("utf-8")):
        return None

    name = row["username"] or row["email"].split("@")[0]
    return {"id": row["id"], "email": row["email"], "name": name}


def update_username(user_id: str, new_username: str) -> dict:
    """Update username. Returns updated user dict."""
    init_db()
    new_username = (new_username or "").strip()
    if not new_username:
        raise ValueError("Username cannot be empty")
    with _conn() as conn:
        cur = conn.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, user_id))
        if cur.rowcount == 0:
            raise ValueError("User not found")
        row = conn.execute("SELECT id, email, username FROM users WHERE id = ?", (user_id,)).fetchone()
    name = row["username"] or row["email"].split("@")[0]
    return {"id": row["id"], "email": row["email"], "name": name}


def update_password(user_id: str, current_password: str, new_password: str) -> None:
    """Update password. Verifies current password first."""
    init_db()
    if len(new_password) < 6:
        raise ValueError("Password must be at least 6 characters")
    with _conn() as c:
        row = c.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        raise ValueError("User not found")
    if not bcrypt.checkpw(current_password.encode("utf-8"), row["password_hash"].encode("utf-8")):
        raise ValueError("Current password is incorrect")
    new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    with _conn() as conn:
        cur = conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
        if cur.rowcount == 0:
            raise ValueError("User not found")
