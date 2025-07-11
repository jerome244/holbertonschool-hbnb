import pytest
from werkzeug.security import generate_password_hash, check_password_hash

@pytest.fixture
def password():
    return "CorrectHorseBatteryStaple!"

def test_generate_and_verify(password):
    h = generate_password_hash(password)
    assert isinstance(h, str) and len(h) > 0
    assert check_password_hash(h, password)

def test_verify_fails_for_wrong_password(password):
    h = generate_password_hash(password)
    assert not check_password_hash(h, password + "typo")