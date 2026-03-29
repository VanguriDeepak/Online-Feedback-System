"""Flask backend for the Online Feedback System.

This app provides:
- Public feedback submission endpoint and home page
- Admin authentication and dashboard
- Session-based access control with timeout
- JSON responses for AJAX requests and redirects for form posts
"""

from __future__ import annotations

import os
import time
from datetime import datetime
from datetime import timedelta
from functools import wraps
from typing import Any

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    render_template_string,
    request,
    session,
    url_for,
)

from database import (
    add_feedback,
    delete_feedback,
    get_all_feedback,
    get_average_rating,
    get_feedback_count,
    init_db,
    verify_admin,
)


def create_app() -> Flask:
    """Application factory for the feedback system backend."""
    app = Flask(__name__)

    # Use environment value when provided; fallback is for local development.
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-in-production")
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

    # Ensure database schema and default admin exist on startup.
    init_db()

    def wants_json_response() -> bool:
        """Detect whether request expects a JSON response (typically AJAX/API calls)."""
        if request.is_json:
            return True

        requested_with = request.headers.get("X-Requested-With", "")
        if requested_with.lower() == "xmlhttprequest":
            return True

        accept = request.accept_mimetypes
        return accept["application/json"] >= accept["text/html"]

    def parse_feedback_payload() -> tuple[str, str, int]:
        """Extract and validate feedback input from JSON or form payload."""
        if request.is_json:
            data: dict[str, Any] = request.get_json(silent=True) or {}
            name = str(data.get("name", "")).strip()
            message = str(data.get("message", "")).strip()
            rating_raw = data.get("rating", "")
        else:
            name = request.form.get("name", "").strip()
            message = request.form.get("message", "").strip()
            rating_raw = request.form.get("rating", "")

        if not name:
            raise ValueError("Name is required.")
        if not message:
            raise ValueError("Message is required.")

        try:
            rating = int(rating_raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("Rating must be an integer between 1 and 5.") from exc

        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5.")

        return name, message, rating

    def admin_required(view_func):
        """Protect admin routes by requiring an authenticated session."""

        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if not session.get("admin_logged_in"):
                if wants_json_response():
                    return jsonify({"success": False, "error": "Authentication required."}), 401
                flash("Please log in as admin.", "error")
                return redirect(url_for("admin_login_page"))
            return view_func(*args, **kwargs)

        return wrapped_view

    @app.before_request
    def enforce_admin_session_timeout() -> Any:
        """Expire authenticated admin session after inactivity period."""
        if not session.get("admin_logged_in"):
            return None

        now = int(time.time())
        last_activity = session.get("last_activity", now)
        timeout_seconds = int(app.permanent_session_lifetime.total_seconds())

        if now - int(last_activity) > timeout_seconds:
            session.clear()
            if wants_json_response():
                return jsonify({"success": False, "error": "Session expired. Please log in again."}), 401
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for("admin_login_page"))

        session["last_activity"] = now
        return None

    @app.get("/")
    def home() -> Any:
        """Render feedback form home page."""
        try:
            recent_feedback = get_all_feedback()[:3]
        except Exception:
            recent_feedback = []

        return render_template(
            "index.html",
            recent_feedback=recent_feedback,
            current_year=datetime.now().year,
        )

    @app.get("/admin")
    def admin_login_page() -> Any:
        """Render admin login page."""
        return render_template("admin_login.html")

    @app.post("/admin/login")
    def admin_login():
        """Authenticate admin and create session."""
        if request.is_json:
            payload = request.get_json(silent=True) or {}
            username = str(payload.get("username", "")).strip()
            password = str(payload.get("password", ""))
            remember_me = bool(payload.get("remember_me", False))
        else:
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            remember_me = request.form.get("remember_me") in {"1", "true", "on", "yes"}

        if not username or not password:
            message = "Username and password are required."
            if wants_json_response():
                return jsonify({"success": False, "error": message}), 400
            flash(message, "error")
            return redirect(url_for("admin_login_page"))

        try:
            authenticated = verify_admin(username, password)
        except Exception as exc:
            message = f"Login failed due to a server error: {exc}"
            if wants_json_response():
                return jsonify({"success": False, "error": message}), 500
            flash(message, "error")
            return redirect(url_for("admin_login_page"))

        if not authenticated:
            message = "Invalid admin credentials."
            if wants_json_response():
                return jsonify({"success": False, "error": message}), 401
            flash(message, "error")
            return redirect(url_for("admin_login_page"))

        session.permanent = remember_me
        session["admin_logged_in"] = True
        session["admin_username"] = username
        session["last_activity"] = int(time.time())

        if wants_json_response():
            return jsonify({"success": True, "message": "Login successful."})

        flash("Login successful.", "success")
        return redirect(url_for("admin_dashboard"))

    @app.get("/admin/dashboard")
    @admin_required
    def admin_dashboard() -> Any:
        """Display all feedback records on the protected admin dashboard."""
        try:
            feedback_list = get_all_feedback()
            feedback_count = get_feedback_count()
            average_rating = get_average_rating()
        except Exception as exc:
            message = f"Could not load dashboard data: {exc}"
            if wants_json_response():
                return jsonify({"success": False, "error": message}), 500
            flash(message, "error")
            return redirect(url_for("admin_login_page"))

        if wants_json_response():
            return jsonify(
                {
                    "success": True,
                    "data": {
                        "feedback": feedback_list,
                        "count": feedback_count,
                        "average_rating": average_rating,
                    },
                }
            )

        return render_template(
            "admin_dashboard.html",
            feedback_list=feedback_list,
            feedback_count=feedback_count,
            average_rating=average_rating,
            admin_username=session.get("admin_username", "admin"),
        )

    @app.post("/submit-feedback")
    def submit_feedback():
        """Submit new feedback with server-side validation."""
        try:
            name, message_text, rating = parse_feedback_payload()
            feedback_id = add_feedback(name, message_text, rating)
        except ValueError as exc:
            error_message = str(exc)
            if wants_json_response():
                return jsonify({"success": False, "error": error_message}), 400
            flash(error_message, "error")
            return redirect(url_for("home"))
        except Exception as exc:
            error_message = f"Unable to save feedback: {exc}"
            if wants_json_response():
                return jsonify({"success": False, "error": error_message}), 500
            flash(error_message, "error")
            return redirect(url_for("home"))

        success_message = "Feedback submitted successfully."
        if wants_json_response():
            return jsonify(
                {
                    "success": True,
                    "message": success_message,
                    "feedback_id": feedback_id,
                }
            )

        flash(success_message, "success")
        return redirect(url_for("home"))

    @app.post("/admin/delete/<int:id>")
    @admin_required
    def admin_delete_feedback(id: int):
        """Delete a feedback record by its ID (protected route)."""
        try:
            deleted = delete_feedback(id)
        except ValueError as exc:
            message = str(exc)
            if wants_json_response():
                return jsonify({"success": False, "error": message}), 400
            flash(message, "error")
            return redirect(url_for("admin_dashboard"))
        except Exception as exc:
            message = f"Delete operation failed: {exc}"
            if wants_json_response():
                return jsonify({"success": False, "error": message}), 500
            flash(message, "error")
            return redirect(url_for("admin_dashboard"))

        if not deleted:
            message = "Feedback not found."
            if wants_json_response():
                return jsonify({"success": False, "error": message}), 404
            flash(message, "error")
            return redirect(url_for("admin_dashboard"))

        if wants_json_response():
            return jsonify({"success": True, "message": "Feedback deleted successfully."})

        flash("Feedback deleted successfully.", "success")
        return redirect(url_for("admin_dashboard"))

    @app.get("/admin/logout")
    def admin_logout():
        """Clear admin session and redirect to login."""
        session.clear()
        if wants_json_response():
            return jsonify({"success": True, "message": "Logged out successfully."})
        flash("Logged out successfully.", "success")
        return redirect(url_for("admin_login_page"))

    @app.errorhandler(404)
    def not_found(error):
        """Return user-friendly 404 for browser and JSON for API/AJAX."""
        del error  # Not used directly; kept for Flask handler signature.
        if wants_json_response():
            return jsonify({"success": False, "error": "Resource not found."}), 404

        return (
            render_template_string(
                """
                <!doctype html>
                <html>
                <head><title>404 Not Found</title></head>
                <body>
                    <h1>404 - Page Not Found</h1>
                    <p>The page you are looking for does not exist.</p>
                    <p><a href="{{ url_for('home') }}">Go to Home</a></p>
                </body>
                </html>
                """
            ),
            404,
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
