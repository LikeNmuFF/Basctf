# CTF Platform

A production-ready Capture The Flag web platform built with Flask, SQLAlchemy, and MySQL.

---

## Features

- User registration / login / logout (Flask-Login)
- Challenge browser grouped by category
- Secure flag submission (SHA256-hashed, no plain-text storage)
- Duplicate-solve prevention
- Live scoreboard ranked by score
- Admin panel: create / edit / toggle / delete challenges
- File attachment uploads per challenge
- Admin user management (grant/revoke admin)

---

## Project Structure

```
ctf_platform/
├── app/
│   ├── __init__.py          # App factory
│   ├── extensions.py        # db, login_manager
│   ├── models.py            # User, Challenge, Solve
│   ├── utils.py             # hash_flag, verify_flag, file helpers
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── challenges/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── services.py
│   ├── scoreboard/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── challenges/
│   │   ├── scoreboard/
│   │   └── admin/
│   └── static/
│       ├── css/main.css
│       ├── js/main.js
│       └── uploads/
├── config.py
├── run.py
├── seed.py
├── requirements.txt
└── .env.example
```

---

## Setup & Installation

### 1. Prerequisites

- Python 3.10+
- MySQL server running locally (or remote)

### 2. Clone / unzip the project

```bash
cd ctf_platform
```

### 3. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create the MySQL database

```sql
CREATE DATABASE ctf_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Configure environment

```bash
cp .env.example .env
# Edit .env and set your DATABASE_URL and SECRET_KEY
```

Example `.env`:
```
FLASK_ENV=development
SECRET_KEY=your-super-secret-random-string
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost/ctf_platform
```

### 7. Create tables & seed data

```bash
python seed.py
```

This creates:
- Admin account: `admin` / `admin1234`
- 4 sample challenges with flags printed to terminal

### 8. Run the application

```bash
python run.py
```

Visit: **http://localhost:5000**

---

## Usage

### Admin
1. Log in as `admin` / `admin1234`
2. Navigate to **Admin** in the navbar
3. Create challenges, manage users

### Players
1. Register an account
2. Browse challenges
3. Submit flags in the format shown (e.g., `CTF{...}`)
4. Check your rank on the Scoreboard

---

## Security Notes

| What | How |
|---|---|
| Passwords | Werkzeug `generate_password_hash` (PBKDF2-SHA256) |
| Flags | SHA256 hex digest — plain flags are **never** stored |
| Duplicate solves | Unique DB constraint on `(user_id, challenge_id)` |
| CSRF | Flask-WTF tokens on all forms |
| File uploads | Extension allowlist + `secure_filename` |
| Admin routes | `@admin_required` decorator, returns 403 for non-admins |

---

## Changing the Default Admin Password

Log in as admin, or update directly:

```python
# In a Flask shell: flask shell
from app.models import User
from app.extensions import db
u = User.query.filter_by(username='admin').first()
u.set_password('new_secure_password')
db.session.commit()
```

---

## Production Deployment Checklist

- [ ] Set `FLASK_ENV=production` in `.env`
- [ ] Change `SECRET_KEY` to a random 32+ byte string
- [ ] Change admin password immediately after first login
- [ ] Use a WSGI server: `gunicorn run:app`
- [ ] Put behind a reverse proxy (nginx) with HTTPS
- [ ] Set `SQLALCHEMY_POOL_RECYCLE` for long-running MySQL connections
