# app/tests/test_facade.py

def test_create_and_get_user(facade, db_session):
    data = {
        "first_name": "Alice",
        "last_name":  "Smith",
        "email":      "alice@xyz.com",
        "password":   "alicepwd1"
    }
    user = facade.create_user(data)

    # ensure the returned object has an id and correct email
    assert user.id is not None
    assert user.email == "alice@xyz.com"

    # retrieve via facade
    fetched = facade.get_user(user.id)
    assert fetched.email == "alice@xyz.com"
