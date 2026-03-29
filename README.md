# Online Feedback System - Member 4's Part

**Feature**: Display Feedback Page (Admin Dashboard)

## Overview
This repository contains the code for Member 4's portion of the Online Feedback System. It implements the admin dashboard where all submitted feedbacks are displayed, and provides the functionality for an admin to delete a feedback.

## Features Implemented
* A beautiful, responsive admin dashboard to view feedbacks (Grid card layout).
* Display feedback details: Name, Star Rating, and Message.
* Delete functionality allowing admins to remove specific feedback entries from the database.
* Sample seeding script so you can test it without needing Member 1 and Member 2's code right away.

## Quick Start

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Seed the database (Creates the `feedback.db` file and inserts dummy data):
   ```bash
   python seed.py
   ```

3. Run the Flask application:
   ```bash
   python app.py
   ```

4. View the dashboard:
   Open your browser and navigate to `http://127.0.0.1:5001/admin` to see the results of Member 4's work!

## GitHub Instructions (For Member 4 & 5)
If you want to push this to your GitHub repository:

1. Create a new repository on GitHub.
2. Link it to this folder:
   ```bash
   git remote add origin https://github.com/your-username/your-repo-name.git
   git branch -M main
   git push -u origin main
   ```
