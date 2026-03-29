from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = 'feedback.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Member 4: Display feedback page (admin side)
@app.route('/admin')
def admin_dashboard():
    try:
        conn = get_db_connection()
        # Fetch all feedbacks from the database
        feedbacks = conn.execute('SELECT * FROM feedbacks ORDER BY id DESC').fetchall()
        conn.close()
    except sqlite3.OperationalError:
        # If database or table is missing, show an empty list
        feedbacks = []
        
    return render_template('dashboard.html', feedbacks=feedbacks)

# Member 4: Delete feedback feature
@app.route('/admin/delete/<int:feedback_id>', methods=['POST'])
def delete_feedback(feedback_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM feedbacks WHERE id = ?', (feedback_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

# A dummy route so you can test if the website is running
@app.route('/')
def index():
    return "<h1>Online Feedback System</h1><p>Go to <a href='/admin'>/admin</a> to view Member 4's Display Feedback Dashboard.</p>"

if __name__ == '__main__':
    app.run(debug=True, port=5001)
