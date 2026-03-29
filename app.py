import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'super-secret-key-for-admin'  # Required for flash messages

DATABASE = 'feedback.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    # Redirect directly to admin dashboard for Member 4's task.
    return redirect(url_for('admin_feedback'))

@app.route('/admin/feedback')
def admin_feedback():
    conn = get_db_connection()
    # Fetch all feedback entries
    feedbacks = conn.execute('SELECT * FROM feedback ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('dashboard.html', feedbacks=feedbacks)

@app.route('/admin/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    conn = get_db_connection()
    # Check if feedback exists
    feedback = conn.execute('SELECT * FROM feedback WHERE id = ?', (feedback_id,)).fetchone()
    
    if feedback is None:
        flash('Feedback not found!', 'danger')
        conn.close()
        return redirect(url_for('admin_feedback'))
        
    conn.execute('DELETE FROM feedback WHERE id = ?', (feedback_id,))
    conn.commit()
    conn.close()
    
    flash('Feedback successfully deleted!', 'success')
    return redirect(url_for('admin_feedback'))

if __name__ == '__main__':
    # Running in debug mode for testing
    app.run(debug=True, port=5000)
