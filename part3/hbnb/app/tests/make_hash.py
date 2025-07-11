#!/usr/bin/python3

from werkzeug.security import generate_password_hash, check_password_hash
from sys import argv

def make_hash():
    """
        A function to generate an hash compatible
        with werkzeug password check function.
        argv[1] : Password to generate hash for and to test.
    """
    password = argv[1]
    hashed = generate_password_hash(password)
    print(f"Original password: {password}")
    print(f"Hashed password: {hashed}")

    is_hashed = check_password_hash(hashed, password)

    if is_hashed:
        print("test_password and hashed are matching")
    else:
        print("test_password and hashed are not matching")

if __name__ == "__main__":

    make_hash()
