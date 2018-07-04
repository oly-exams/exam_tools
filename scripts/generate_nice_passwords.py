#!/usr/bin/env python3

"""
Simple module to create passwords that do not contain certain characters.
"""

import sys
import secrets

BLOCKED_CHARACTERS = '0O1Il-_'

def generate_password(num_bytes=6):
    pwd_candidate = secrets.token_urlsafe(num_bytes)
    while any(char in pwd_candidate for char in BLOCKED_CHARACTERS):
        pwd_candidate = secrets.token_urlsafe(num_bytes)
    return pwd_candidate

if __name__ == '__main__':
    try:
        num_pwd = int(sys.argv[1])
    except (IndexError, TypeError):
        print('usage: ./generate_nice_passwords.py num_passwords [num_bytes]')
        sys.exit()
    try:
        num_bytes = int(sys.argv[2])
    except IndexError:
        num_bytes = 6
    for _ in range(num_pwd):
        print(generate_password(num_bytes=num_bytes))
