"""
database.py — SQLite helper module for the Student Task Manager.

Provides:
    • get_connection()    – returns a reusable DB connection
    • init_db()           – creates tables if they don't exist
    • add_user()          – register a new user
    • add_task()          – create a new task for a user
    • fetch_tasks()       – get all tasks (optionally filtered by user)
    • update_task_status()– mark a task as Pending / Completed
    • delete_task()       – remove a task by its id
"""

import sqlite3
import os

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'task_manager.db')


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------
def get_connection():
    """Return a sqlite3 connection with foreign-key support enabled."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row          # rows behave like dicts
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------------------------------------------------------------------------
# Initialise database (create tables)
# ---------------------------------------------------------------------------
def init_db():
    """Create the Users and Tasks tables if they do not already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tasks (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  INTEGER NOT NULL,
            title    TEXT    NOT NULL,
            deadline TEXT,
            status   TEXT    NOT NULL DEFAULT 'Pending'
                             CHECK (status IN ('Pending', 'Completed')),
            FOREIGN KEY (user_id) REFERENCES Users (id)
                ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()
    print("[✓] Database initialised successfully.")


# ---------------------------------------------------------------------------
# CRUD Functions
# ---------------------------------------------------------------------------

# ── 1. Add User ──────────────────────────────────────────────────────────
def add_user(username: str, password: str) -> int:
    """
    Insert a new user and return their id.
    Raises sqlite3.IntegrityError if the username already exists.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Users (username, password) VALUES (?, ?)",
        (username, password),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


# ── 2. Add Task ──────────────────────────────────────────────────────────
def add_task(user_id: int, title: str, deadline: str = None, status: str = "Pending") -> int:
    """
    Insert a new task for a user and return the task id.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Tasks (user_id, title, deadline, status) VALUES (?, ?, ?, ?)",
        (user_id, title, deadline, status),
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id


# ── 3. Fetch Tasks ──────────────────────────────────────────────────────
def fetch_tasks(user_id: int = None) -> list[dict]:
    """
    Return tasks as a list of dicts.
    If user_id is provided, only that user's tasks are returned.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if user_id:
        cursor.execute("SELECT * FROM Tasks WHERE user_id = ?", (user_id,))
    else:
        cursor.execute("SELECT * FROM Tasks")

    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tasks


# ── 4. Update Task Status ───────────────────────────────────────────────
def update_task_status(task_id: int, new_status: str) -> bool:
    """
    Update the status of a task. new_status must be 'Pending' or 'Completed'.
    Returns True if a row was actually updated, False otherwise.
    """
    if new_status not in ("Pending", "Completed"):
        raise ValueError("Status must be 'Pending' or 'Completed'.")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Tasks SET status = ? WHERE id = ?",
        (new_status, task_id),
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


# ── 5. Delete Task ──────────────────────────────────────────────────────
def delete_task(task_id: int) -> bool:
    """
    Delete a task by its id.
    Returns True if a row was deleted, False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Tasks WHERE id = ?", (task_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# ---------------------------------------------------------------------------
# Quick self-test (run this file directly to seed & verify)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Reset for a clean demo
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    init_db()

    # Add sample users
    uid1 = add_user("alice",   "alice123")
    uid2 = add_user("bob",     "bob456")
    uid3 = add_user("charlie", "charlie789")
    print(f"[+] Users created  →  alice={uid1}, bob={uid2}, charlie={uid3}")

    # Add sample tasks
    add_task(uid1, "Complete Math Assignment", "2026-04-05")
    add_task(uid1, "Read Chapter 4 - DBMS",   "2026-04-02")
    add_task(uid1, "Submit Lab Report",        "2026-03-30", "Completed")
    add_task(uid2, "Prepare Presentation",     "2026-04-10")
    add_task(uid2, "Online Quiz - Python",     "2026-04-01", "Completed")
    add_task(uid3, "Group Project Meeting",    "2026-04-03")
    print("[+] Sample tasks inserted.")

    # Fetch all tasks
    print("\n── All Tasks ──")
    for t in fetch_tasks():
        print(f"   Task #{t['id']}  [{t['status']}]  {t['title']}  (due: {t['deadline']})")

    # Fetch tasks for alice only
    print("\n── Alice's Tasks ──")
    for t in fetch_tasks(user_id=uid1):
        print(f"   Task #{t['id']}  [{t['status']}]  {t['title']}")

    # Update task #1 to Completed
    update_task_status(1, "Completed")
    print("\n[~] Task #1 marked as Completed.")

    # Delete task #4
    delete_task(4)
    print("[−] Task #4 deleted.")

    # Final state
    print("\n── Final Tasks ──")
    for t in fetch_tasks():
        print(f"   Task #{t['id']}  [{t['status']}]  {t['title']}")
