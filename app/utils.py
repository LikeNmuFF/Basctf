import hmac
import hashlib
import os
from uuid import uuid4
from urllib.parse import urlparse

from werkzeug.utils import secure_filename
from flask import current_app


def hash_flag(flag: str) -> str:
    """Hash a flag using SHA256. Always strip whitespace before hashing."""
    return hashlib.sha256(flag.strip().encode('utf-8')).hexdigest()


def verify_flag(submitted_flag: str, stored_hash: str) -> bool:
    """Securely compare a submitted flag against stored hash."""
    submitted_hash = hash_flag(submitted_flag)
    return hmac.compare_digest(submitted_hash, stored_hash)


def allowed_file(filename: str) -> bool:
    """Check if uploaded file extension is allowed."""
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', set())
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def save_upload(file) -> str | None:
    """Save an uploaded file and return its relative path, or None on failure."""
    if file and file.filename and allowed_file(file.filename):
        original_name = secure_filename(file.filename)
        name, ext = os.path.splitext(original_name)
        unique_suffix = uuid4().hex[:12]
        filename = f'{name}_{unique_suffix}{ext}'
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return f'uploads/{filename}'
    return None


def normalize_external_link(link: str | None) -> str | None:
    """Normalize admin-provided links so bare domains still open correctly."""
    if not link:
        return None

    cleaned = link.strip()
    if not cleaned:
        return None

    parsed = urlparse(cleaned)
    if parsed.scheme:
        if parsed.scheme not in {'http', 'https'}:
            return None
        return cleaned

    return f'https://{cleaned}'


CATEGORIES = [
    ('web', 'Web'),
    ('crypto', 'Cryptography'),
    ('pwn', 'Pwn / Binary'),
    ('rev', 'Reverse Engineering'),
    ('forensics', 'Forensics'),
    ('misc', 'Miscellaneous'),
    ('osint', 'OSINT'),
    ('network', 'Networking'),
]

DIFFICULTIES = [
    ('easy', 'Easy'),
    ('medium', 'Medium'),
    ('hard', 'Hard'),
]
