#!/usr/bin/python3

"""
    A function to generate an hash compatible
    with werkzeug password check function.
"""

from werkzeug.security import generate_password_hash, check_password_hash

def make_hash(password, test_password):

    hashed = generate_password_hash(password)
    print(f"Original password: {password}")
    print(f"Hashed password: {hashed}")

    is_hashed = check_password_hash(hashed, test_password)

    if is_hashed:
        print("test_password and hashed are matching")
    else:
        print("test_password and hashed are not matching")

if __name__ == "__main__":

    original_password = "admin1234"
    input_password = "admin1234"

    make_hash(original_password, input_password)
