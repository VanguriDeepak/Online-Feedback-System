"""
database.py — SQLite helper module for the Online Feedback System.
Author: Member 3 (Database)

Provides:
    • get_connection()       – returns a reusable DB connection
    • init_db()              – creates the feedbacks table if not exists
    • add_feedback()         – insert a new feedback entry
    • fetch_all_feedbacks()  – retrieve all feedback records
    • fetch_feedback_by_id() – retrieve a single feedback by id
    • delete_feedback()      – remove a feedback entry by id
"""

import sqlite3
import os

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feedback.db')


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------
def get_connection():
    """Return a sqlite3 connection with Row factory for dict-like access."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn


# ---------------------------------------------------------------------------
# Initialise database (create table)
# ---------------------------------------------------------------------------
def init_db():
    """Create the feedbacks table if it does not already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedbacks (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT    NOT NULL,
            message TEXT    NOT NULL,
            rating  INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5)
        );
    """)

    conn.commit()
    conn.close()
    print("[✓] Database initialised — feedbacks table ready.")


# ---------------------------------------------------------------------------
# CRUD Functions
# ---------------------------------------------------------------------------

# ── 1. Add Feedback ─────────────────────────────────────────────────────
def add_feedback(name: str, message: str, rating: int) -> int:
    """
    Insert a new feedback entry and return its id.
    Rating must be between 1 and 5.
    """
    if not (1 <= rating <= 5):
        raise ValueError("Rating must be between 1 and 5.")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO feedbacks (name, message, rating) VALUES (?, ?, ?)",
        (name, message, rating),
    )
    conn.commit()
    feedback_id = cursor.lastrowid
    conn.close()
    return feedback_id


# ── 2. Fetch All Feedbacks ──────────────────────────────────────────────
def fetch_all_feedbacks() -> list:
    """Return all feedback entries as a list of dicts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedbacks ORDER BY id DESC")
    feedbacks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return feedbacks


# ── 3. Fetch Single Feedback by ID ─────────────────────────────────────
def fetch_feedback_by_id(feedback_id: int) -> dict:
    """Return a single feedback entry as a dict, or None if not found."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedbacks WHERE id = ?", (feedback_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ── 4. Delete Feedback ─────────────────────────────────────────────────
def delete_feedback(feedback_id: int) -> bool:
    """
    Delete a feedback entry by its id.
    Returns True if a row was actually deleted, False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM feedbacks WHERE id = ?", (feedback_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# ---------------------------------------------------------------------------
# Quick self-test  (run this file directly to seed & verify)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Remove old DB for a clean demo
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    init_db()

    # Insert sample feedbacks
    add_feedback("Alice Smith", "The website is really easy to use!", 5)
    add_feedback("Bob Johnson", "I had some issues finding what I needed.", 3)
    add_feedback("Charlie Brown", "Great service entirely. The staff was super helpful!", 5)
    add_feedback("David Lee", "The login page gave me an error once, but overall fine.", 4)
    add_feedback("Eva Martinez", "Average experience. Could improve the response time.", 3)
    add_feedback("Frank White", "Absolutely loved the clean interface and fast performance!", 5)
    print("[+] 6 sample feedbacks inserted.\n")

    # Fetch and display all
    print("── All Feedbacks ──")
    for fb in fetch_all_feedbacks():
        stars = "⭐" * fb["rating"]
        print(f"  #{fb['id']}  {fb['name']}  {stars}")
        print(f"       \"{fb['message']}\"\n")

    # Fetch single feedback
    print("── Fetch Feedback #2 ──")
    fb = fetch_feedback_by_id(2)
    if fb:
        print(f"  {fb['name']} — Rating: {fb['rating']}/5")
        print(f"  \"{fb['message']}\"\n")

    # Delete feedback #3
    result = delete_feedback(3)
    print(f"── Delete Feedback #3 → {'Success' if result else 'Not Found'} ──\n")

    # Final state
    print("── Remaining Feedbacks ──")
    for fb in fetch_all_feedbacks():
        print(f"  #{fb['id']}  {fb['name']}  {'⭐' * fb['rating']}")
