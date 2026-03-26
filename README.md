<p align="center">
  <svg width="720" height="200" viewBox="0 0 720 200" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#00ffc6"/>
        <stop offset="50%" stop-color="#00d4ff"/>
        <stop offset="100%" stop-color="#9b5cff"/>
      </linearGradient>
      <filter id="glow">
        <feGaussianBlur stdDeviation="4" result="blur"/>
        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
      <linearGradient id="scan" x1="0" x2="0" y1="0" y2="1">
        <stop offset="0%" stop-color="rgba(0,255,198,0)"/>
        <stop offset="50%" stop-color="rgba(0,255,198,0.3)"/>
        <stop offset="100%" stop-color="rgba(0,255,198,0)"/>
      </linearGradient>
    </defs>
    <rect width="720" height="200" fill="#06090f" rx="16"/>
    <rect width="720" height="200" fill="url(#scan)">
      <animate attributeName="y" from="-200" to="200" dur="3s" repeatCount="indefinite"/>
    </rect>
    <text x="50%" y="55%" text-anchor="middle" fill="url(#g)" font-family="Share Tech Mono, monospace" font-size="54" filter="url(#glow)">CTF_PLATFORM</text>
    <text x="50%" y="78%" text-anchor="middle" fill="#6c7a89" font-family="Rajdhani, sans-serif" font-size="18" letter-spacing="4">ATTACK  ·  DEFEND  ·  LEARN</text>
  </svg>
</p>

> A kinetic Capture The Flag range built with Flask + SQLAlchemy + MySQL. Pairs nicely with synthwave and a dark terminal.

---

## 🔥 Highlights

- Challenge browser with live filtering by **category + difficulty + search** (PicoCTF vibes).
- Secure flag flow: SHA256 hashing + cooldowns + duplicate-solve guard.
- Rich admin console: create/edit/toggle/delete challenges, upload files, manage users.
- Built‑in hints with point penalties and personal accuracy stats.
- Neon UI (Rajdhani + Share Tech Mono) ready for dark dashboards.

---

## 🗂️ Stack & Layout

```
ctf_platform/
├─ app/
│  ├─ __init__.py          # App factory + DB bootstraps (auto adds new cols)
│  ├─ extensions.py        # db, login_manager, csrf
│  ├─ models.py            # User, Challenge (now with difficulty), Solve, etc.
│  ├─ utils.py             # flag hashing, uploads, categories, difficulties
│  ├─ auth/                # auth routes/forms
│  ├─ challenges/          # player routes/services (filters, hints, cooldowns)
│  ├─ scoreboard/          # leaderboard
│  ├─ admin/               # admin routes/forms/templates
│  ├─ templates/           # Jinja views (dark UI)
│  └─ static/              # css/js/assets/uploads
├─ config.py               # env profiles
├─ seed.py                 # bootstrap admin + sample challenges
├─ run.py                  # flask entry
└─ requirements.txt
```

---

## 🚀 Quickstart

```bash
python -m venv venv
source venv/bin/activate      # or venv\Scripts\activate on Windows
pip install -r requirements.txt

mysql -u root -p -e "CREATE DATABASE ctf_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

cp .env.example .env          # set DATABASE_URL + SECRET_KEY
python seed.py                # creates admin/admin1234 + sample challenges
python run.py                 # visit http://localhost:5000
```

Admin flow: log in → **Admin** tab → build challenges (category, difficulty, points, hints, attachment).  
Player flow: register → filter by vibe (web/crypto/pwn…) & difficulty → solve → climb the scoreboard.

---

## 🛡️ Security Posture

| Layer         | Mechanism                                                        |
| ------------- | ---------------------------------------------------------------- |
| Passwords     | PBKDF2-SHA256 (`generate_password_hash`)                         |
| Flags         | SHA256 digest only; constant-time compare                        |
| Abuse control | Duplicate-solve constraint; cooldown after streak of wrong flags |
| CSRF          | Flask-WTF tokens everywhere                                      |
| Uploads       | Extension allowlist + `secure_filename`                          |
| Admin         | `@admin_required` 403 gate                                       |

---

## 🧰 Operational Notes

- Difficulty column auto-migrates on start; seed script tags samples with easy/medium.
- Run `python seed.py` again if you want fresh demo data after schema tweaks.
- For production: use gunicorn/uwsgi behind nginx, rotate SECRET_KEY, harden MySQL creds.

---

### Hack the planet 🛰️

Spin it up, drop in your own challenges, and let the neon scoreboard glow. PRs welcome.\*\*\* End Patch Jiova
