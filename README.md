# Online Feedback System

A modern Flask + SQLite web application for collecting user feedback and managing it through a protected admin dashboard.

## Features

- Public feedback form with:
  - Name and message validation
  - Interactive star rating (1-5)
  - AJAX submit and live preview
- Admin authentication with bcrypt-hashed passwords
- Session-based admin access with timeout handling
- Admin dashboard with:
  - Search, sorting, pagination
  - Delete feedback with confirmation modal
  - CSV export
  - Rating distribution chart (Chart.js)
  - Light/Dark theme toggle
- SQLite database with automatic schema initialization

## Tech Stack

- Python 3.x
- Flask
- SQLite3
- bcrypt
- HTML/CSS/JavaScript
- Chart.js (CDN)
- Font Awesome (CDN)

## Project Structure

```
.
├─ app.py
├─ database.py
├─ requirements.txt
├─ templates/
│  ├─ index.html
│  ├─ admin_login.html
│  └─ admin_dashboard.html
└─ README.md
```

## Setup Instructions

1. Clone the repository

```bash
git clone <your-repo-url>
cd "Feedback System"
```

2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Run the application

```bash
python app.py
```

5. Open in browser

- Public page: http://127.0.0.1:5000/
- Admin login: http://127.0.0.1:5000/admin

## Default Admin Credentials

- Username: `admin`
- Password: `admin123`

> Change the default credentials for production use.

## Security Notes

- Passwords are stored as bcrypt hashes
- SQL operations use parameterized queries
- Server-side input validation is enabled
- Admin routes are session protected

## License

This project is for learning and demonstration purposes.
