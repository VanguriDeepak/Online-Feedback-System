import sqlite3
import os

DATABASE = 'feedback.db'

def setup_db():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create table for feedback
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            rating INTEGER NOT NULL
        )
    ''')
    
    # Insert some dummy data
    dummy_data = [
        ('Alice Smith', 'The interface is very user-friendly but it could be faster.', 4),
        ('Bob Jones', 'I had a hard time finding the login button.', 2),
        ('Charlie Brown', 'Excellent service! Everything works perfectly.', 5),
        ('Diana Prince', 'It keeps logging me out after 5 minutes.', 1),
        ('Evan Wright', 'Good overall, but I want more features in the dashboard.', 3)
    ]
    
    cursor.executemany('''
        INSERT INTO feedback (name, message, rating)
        VALUES (?, ?, ?)
    ''', dummy_data)
    
    conn.commit()
    conn.close()
    print("Database seeded successfully with dummy feedback data!")

if __name__ == '__main__':
    setup_db()
