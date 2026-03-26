"""
seed.py — Run once to create an admin user and sample challenges.
Usage: python seed.py
"""
import os
from app import create_app
from app.extensions import db
from app.models import User, Challenge
from app.utils import hash_flag


def seed():
    app = create_app(os.environ.get('FLASK_ENV', 'default'))
    with app.app_context():
        db.create_all()

        # Create admin user
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@ctf.local', is_admin=True)
            admin.set_password('admin1234')
            db.session.add(admin)
            print('[+] Admin user created  →  admin / admin1234')
        else:
            print('[*] Admin user already exists.')

        # Sample challenges
        samples = [
            {
                'title': 'Hello, World!',
                'description': 'Find the flag hidden in the page source of http://example.ctf/hello.',
                'hint_1': 'Inspect the HTML source code for the page.',
                'hint_2': 'Search for a string that looks like CTF{...}.',
                'hint_3': 'The flag is in a commented line with CTF{h3ll0_w0rld}.',
                'category': 'web',
                'difficulty': 'easy',
                'points': 50,
                'flag': 'CTF{h3ll0_w0rld}',
            },
            {
                'title': 'Caesar\'s Secret',
                'description': 'Decrypt this message: PGS{ebg13_vf_sha}.',
                'hint_1': 'The text looks like a classic substitution cipher.',
                'hint_2': 'ROT13 is often used in CTFs; apply it to the flag string.',
                'hint_3': 'PGS becomes CTF after ROT13 and the rest becomes rot13_is_fun.',
                'category': 'crypto',
                'difficulty': 'easy',
                'points': 75,
                'flag': 'CTF{rot13_is_fun}',
            },
            {
                'title': 'Magic Bytes',
                'description': 'A file has been given to you. Determine its true type by inspecting the first few bytes (magic bytes). The flag is hidden inside.\n\nFile: magic.bin (not provided in this demo)',
                'category': 'forensics',
                'difficulty': 'medium',
                'points': 100,
                'flag': 'CTF{magic_bytes_matter}',
            },
            {
                'title': 'Recon 101',
                'description': 'Find information about the domain: ctf-demo.example.com\n\nWhat is the name of the admin as listed in the WHOIS record?\nSubmit as CTF{firstname_lastname}',
                'category': 'osint',
                'difficulty': 'medium',
                'points': 125,
                'flag': 'CTF{john_doe}',
            },
        ]

        added = 0
        for s in samples:
            if not Challenge.query.filter_by(title=s['title']).first():
                ch = Challenge(
                    title=s['title'],
                    description=s['description'],
                    hint_1=s.get('hint_1'),
                    hint_2=s.get('hint_2'),
                    hint_3=s.get('hint_3'),
                    category=s['category'],
                    difficulty=s.get('difficulty', 'medium'),
                    points=s['points'],
                    flag_hash=hash_flag(s['flag']),
                )
                db.session.add(ch)
                added += 1
                print(f'[+] Challenge added: {s["title"]}  →  flag: {s["flag"]}')

        db.session.commit()
        print(f'\n✓ Seed complete. {added} challenge(s) added.')
        print('\nSample flags for testing:')
        for s in samples:
            print(f'  {s["title"]:30s}  {s["flag"]}')


if __name__ == '__main__':
    seed()
