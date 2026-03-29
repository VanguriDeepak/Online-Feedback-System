import sqlite3

# This script creates a database 'feedback.db' with some initial data 
# so Member 4 can test that the display feature works.

connection = sqlite3.connect('feedback.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Insert dummy data
cur.execute("INSERT INTO feedbacks (name, message, rating) VALUES (?, ?, ?)",
            ('Alice Smith', 'The website is really easy to use!', 5))

cur.execute("INSERT INTO feedbacks (name, message, rating) VALUES (?, ?, ?)",
            ('Bob Johnson', 'I had some issues finding what I needed.', 3))

cur.execute("INSERT INTO feedbacks (name, message, rating) VALUES (?, ?, ?)",
            ('Charlie Brown', 'Great service entirely. The staff was super helpful. Keep it up!', 5))

cur.execute("INSERT INTO feedbacks (name, message, rating) VALUES (?, ?, ?)",
            ('David Lee', 'The login page gave me an error once, but overall fine.', 4))

connection.commit()
connection.close()

print("Database seeded successfully. You can now run the app.")
