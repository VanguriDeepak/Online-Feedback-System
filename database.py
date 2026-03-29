"""SQLite database module for an Online Feedback System.

This module provides schema initialization, feedback CRUD helpers,
and admin authentication with bcrypt password hashing.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import bcrypt


DB_PATH = Path(__file__).resolve().parent / "feedback_system.db"


def _get_connection() -> sqlite3.Connection:
    """Create and return a SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _validate_feedback_input(name: str, message: str, rating: int) -> None:
    """Validate feedback payload before writing to the database."""
    if not isinstance(name, str):
        raise ValueError("Name must be a string.")
    if not isinstance(message, str):
        raise ValueError("Message must be a string.")

    name = name.strip()
    message = message.strip()

    if not name:
        raise ValueError("Name is required.")
    if len(name) > 100:
        raise ValueError("Name must be at most 100 characters.")

    if not message:
        raise ValueError("Message is required.")

    if not isinstance(rating, int):
        raise ValueError("Rating must be an integer.")
    if rating < 1 or rating > 5:
        raise ValueError("Rating must be between 1 and 5.")


def _validate_admin_input(username: str, password: str) -> None:
    """Validate admin credentials before verification."""
    if not isinstance(username, str) or not username.strip():
        raise ValueError("Username is required.")
    if not isinstance(password, str) or not password:
        raise ValueError("Password is required.")
    if len(username.strip()) > 50:
        raise ValueError("Username must be at most 50 characters.")


def _hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def init_db() -> None:
    """Create required tables and ensure a default admin account exists."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    message TEXT NOT NULL,
                    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS admin (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL
                )
                """
            )

            # Seed default admin only if it does not already exist.
            cursor.execute("SELECT id FROM admin WHERE username = ?", ("admin",))
            admin_row = cursor.fetchone()
            if admin_row is None:
                password_hash = _hash_password("admin123")
                cursor.execute(
                    "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
                    ("admin", password_hash),
                )

            conn.commit()
    except sqlite3.Error as exc:
        raise RuntimeError(f"Database initialization failed: {exc}") from exc


def add_feedback(name: str, message: str, rating: int) -> int:
    """Insert a feedback entry and return the inserted row ID."""
    _validate_feedback_input(name, message, rating)

    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO feedback (name, message, rating) VALUES (?, ?, ?)",
                (name.strip(), message.strip(), rating),
            )
            conn.commit()
            return int(cursor.lastrowid)
    except sqlite3.Error as exc:
        raise RuntimeError(f"Failed to add feedback: {exc}") from exc


def get_all_feedback() -> list[dict[str, Any]]:
    """Return all feedback rows ordered by most recent first."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, name, message, rating, created_at
                FROM feedback
                ORDER BY created_at DESC, id DESC
                """
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        raise RuntimeError(f"Failed to fetch feedback: {exc}") from exc


def delete_feedback(feedback_id: int) -> bool:
    """Delete feedback by ID. Returns True if a row was deleted."""
    if not isinstance(feedback_id, int) or feedback_id <= 0:
        raise ValueError("Feedback ID must be a positive integer.")

    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM feedback WHERE id = ?", (feedback_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as exc:
        raise RuntimeError(f"Failed to delete feedback: {exc}") from exc


def verify_admin(username: str, password: str) -> bool:
    """Validate admin credentials using bcrypt hash verification."""
    _validate_admin_input(username, password)

    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT password_hash FROM admin WHERE username = ?",
                (username.strip(),),
            )
            row = cursor.fetchone()
            if row is None:
                return False

            stored_hash = row["password_hash"]
            return bcrypt.checkpw(
                password.encode("utf-8"),
                stored_hash.encode("utf-8"),
            )
    except sqlite3.Error as exc:
        raise RuntimeError(f"Admin verification failed: {exc}") from exc


def get_feedback_count() -> int:
    """Return total number of feedback entries."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS total FROM feedback")
            row = cursor.fetchone()
            return int(row["total"]) if row is not None else 0
    except sqlite3.Error as exc:
        raise RuntimeError(f"Failed to get feedback count: {exc}") from exc


def get_average_rating() -> float:
    """Return average rating rounded to 2 decimals; 0.0 when no rows exist."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT AVG(rating) AS avg_rating FROM feedback")
            row = cursor.fetchone()
            avg = row["avg_rating"] if row is not None else None
            return round(float(avg), 2) if avg is not None else 0.0
    except sqlite3.Error as exc:
        raise RuntimeError(f"Failed to get average rating: {exc}") from exc


if __name__ == "__main__":
    init_db()
