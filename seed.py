"""
seed.py — Run once to create an admin user and sample challenges.
Usage: python seed.py
"""
import os
from app import create_app
from app.extensions import db
from app.models import User, Challenge
from app.utils import hash_flag
from config import get_config_name


def seed():
    app = create_app(get_config_name())
    with app.app_context():
        db.create_all()

        # Remove legacy admin accounts and create a secure admin user
        for legacy_username in ['admin', 'adminx2']:
            legacy_user = User.query.filter_by(username=legacy_username).first()
            if legacy_user:
                db.session.delete(legacy_user)
                print(f'[+] Removed legacy admin user: {legacy_username}')

        legacy_email_user = User.query.filter_by(email='admin@ctf.local').first()
        if legacy_email_user and legacy_email_user.username != 'adminx3':
            db.session.delete(legacy_email_user)
            print('[+] Removed legacy admin account with email admin@ctf.local')

        admin = User.query.filter_by(username='adminx3').first()
        if admin:
            admin.set_password('hack4govx1mpvl$e')
            admin.is_admin = True
            admin.email = 'admin@ctf.local'
            db.session.add(admin)
            print('[+] Admin user updated  →  adminx3 / hack4govx1mpvl$e')
        else:
            admin = User(username='adminx3', email='admin@ctf.local', is_admin=True)
            admin.set_password('hack4govx1mpvl$e')
            db.session.add(admin)
            print('[+] Admin user created  →  adminx3 / hack4govx1mpvl$e')

        # Sample challenges
        samples = [
            {
                'title': 'Binary Basics',
                'description': (
                    'You are given the following x86-64 Linux snippet from a stripped ELF binary:\n\n'
                    '48 31 c0 48 89 c7 48 89 c6 48 8d 35 0e 00 00 00 48 8d 3d 0f 00 00 00 \n'
                    'c6 00 43 54 46 7b 62 69 6e 5f 65 61 73 79 7d 0a e8 dc ff ff ff 2f 62 \n'
                    '69 6e 2f 73 68\n\n'
                    'The flag is printed by the binary when it runs. Identify the hidden flag from the string bytes above.'
                ),
                'hint_1': 'Look at the ASCII bytes after the write syscall setup, especially near 43 54 46 7b.',
                'hint_2': 'The bytes decode directly to the flag text: CTF{bin_easy}.',
                'hint_3': 'The flag appears as a plain string in the data section.',
                'category': 'binary',
                'difficulty': 'easy',
                'points': 100,
                'flag': 'CTF{bin_easy}',
            },
            {
                'title': 'Simple XOR Cipher',
                'description': (
                    'Decrypt this ciphertext that was XORed with a single-byte key.\n\n'
                    'Ciphertext (hex): 3f 0c 0d 0f 78 17 4f 0c 4a 0a 1f 0f 0f 75 17 4e 0c 1a 1f 0d\n\n'
                    'The original plaintext is a flag in the format CTF{...}.'
                ),
                'hint_1': 'Try common single-byte keys such as 0x20, 0x41, or 0x5f.',
                'hint_2': 'The plaintext starts with CTF{ and ends with }.',
                'hint_3': 'The correct key is 0x15 and the recovered flag is CTF{x0r_magic}.',
                'category': 'crypto',
                'difficulty': 'easy',
                'points': 100,
                'flag': 'CTF{x0r_magic}',
            },
            {
                'title': 'Buffer Overflow',
                'description': (
                    'A vulnerable 64-bit binary reads a username into a fixed-size buffer and then checks for admin access. \n'
                    'There is no stack canary, and the admin check compares the saved return address. \n'
                    'Your goal is to overwrite the return address so the program prints the flag.\n\n'
                    'This is a reverse-engineering style binary challenge; the flag format is CTF{...}.'
                ),
                'hint_1': 'The overflow happens at a 64-byte buffer. Look for a gadget that leads to the print_flag function.',
                'hint_2': 'In a 64-bit binary, saved RBP plus return address are 16 bytes after the buffer start.',
                'hint_3': 'The flag is CTF{overflow_medium}.',
                'category': 'binary',
                'difficulty': 'medium',
                'points': 200,
                'flag': 'CTF{overflow_medium}',
            },
            {
                'title': 'RSA Shared Modulus',
                'description': (
                    'Two RSA ciphertexts were created with the same modulus but different public exponents. \n'
                    'Recover the original flag from the ciphertexts below.\n\n'
                    'n = 171731371\n'
                    'e1 = 3\n'
                    'e2 = 5\n'
                    'c1 = 104359143\n'
                    'c2 = 65723194\n\n'
                    'The flag is encoded as an ASCII string inside the message and has the format CTF{...}.'
                ),
                'hint_1': 'Use the common modulus attack for RSA when e1 and e2 share the same n.',
                'hint_2': 'Compute the message by combining m^e1 and m^e2 to recover m.',
                'hint_3': 'The recovered plaintext is CTF{shared_rsa}.',
                'category': 'crypto',
                'difficulty': 'hard',
                'points': 300,
                'flag': 'CTF{shared_rsa}',
            },
            {
                'title': 'ROP Gatekeeper',
                'description': (
                    'A hardened binary rejects direct calls to the flag function but exposes several gadgets. \n'
                    'Your job is to build a return-oriented programming chain that jumps to the hidden flag routine. \n'
                    'The flag is stored in a read-only section and printed by the hidden function when executed.'
                ),
                'hint_1': 'Find a gadget sequence that calls the hidden function without using a direct address in the input.',
                'hint_2': 'This is a hard binary challenge; think in terms of ROP and indirect control flow.',
                'hint_3': 'The flag is CTF{rop_hardcore}.',
                'category': 'binary',
                'difficulty': 'hard',
                'points': 350,
                'flag': 'CTF{rop_hardcore}',
            },
            {
                'title': 'Discrete Log Puzzle',
                'description': (
                    'Solve for x in the equation 3^x mod 97 = 64. The flag is the ASCII representation of x in the format CTF{...}.'
                ),
                'hint_1': 'Brute force small discrete logs by testing values of x from 0 to 96.',
                'hint_2': 'The solution can be found quickly because the modulus is small.',
                'hint_3': 'x = 64, so the flag is CTF{64}.',
                'category': 'crypto',
                'difficulty': 'medium',
                'points': 200,
                'flag': 'CTF{64}',
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
