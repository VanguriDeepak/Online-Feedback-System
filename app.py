"""
app.py — Flask application for the Student Task Manager.

Routes:
    GET  /                          → Home (redirect to tasks)
    POST /add_user                  → Register a new user
    POST /add_task                  → Create a new task
    GET  /tasks                     → View all tasks (optional ?user_id=)
    POST /update_task/<id>          → Update task status
    POST /delete_task/<id>          → Delete a task
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for
from database import init_db, add_user, add_task, fetch_tasks, update_task_status, delete_task
import sqlite3

app = Flask(__name__)

# Initialise the database when the app starts
init_db()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    """Redirect to the tasks page."""
    return redirect(url_for("view_tasks"))


@app.route("/add_user", methods=["POST"])
def register_user():
    """Register a new user."""
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    try:
        user_id = add_user(username, password)
        return jsonify({"message": "User created successfully.", "user_id": user_id}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists."}), 409


@app.route("/add_task", methods=["POST"])
def create_task():
    """Add a new task for a user."""
    user_id  = request.form.get("user_id")
    title    = request.form.get("title")
    deadline = request.form.get("deadline")

    if not user_id or not title:
        return jsonify({"error": "user_id and title are required."}), 400

    task_id = add_task(int(user_id), title, deadline)
    return redirect(url_for("view_tasks"))


@app.route("/tasks")
def view_tasks():
    """Display tasks. Pass ?user_id=N to filter by user."""
    user_id = request.args.get("user_id", type=int)
    tasks = fetch_tasks(user_id)
    return render_template("tasks.html", tasks=tasks, filter_user=user_id)


@app.route("/update_task/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    """Toggle task status between Pending and Completed."""
    new_status = request.form.get("status", "Completed")
    update_task_status(task_id, new_status)
    return redirect(url_for("view_tasks"))


@app.route("/delete_task/<int:task_id>", methods=["POST"])
def remove_task(task_id):
    """Delete a task."""
    delete_task(task_id)
    return redirect(url_for("view_tasks"))


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
