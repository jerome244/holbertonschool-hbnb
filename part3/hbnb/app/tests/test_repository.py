# app/tests/test_repository.py

from app.persistence.sqlalchemy_repository import SQLAlchemyRepository
from app.models.user import User

def test_add_and_get_user(user_repo, db_session):
    # create a new user
    u = User(
        first_name="Foo",
        last_name="Bar",
        email="foo@bar.com",
        password="secretpw"
    )
    user_repo.add(u)

    # fetch by id
    fetched = user_repo.get(u.id)
    assert fetched is not None
    assert fetched.email == "foo@bar.com"

def test_update_user(user_repo, db_session):
    u = User(
        first_name="Xavier",
        last_name="Y",
        email="x@y.com",
        password="password1"
    )
    user_repo.add(u)

    user_repo.update(u.id, {"email": "new@z.com"})
    updated = user_repo.get(u.id)
    assert updated.email == "new@z.com"

def test_delete_user(user_repo, db_session):
    u = User(
        first_name="Del",
        last_name="User",
        email="del@me.com",
        password="deletepw"
    )
    user_repo.add(u)
    uid = u.id

    user_repo.delete(uid)
    assert user_repo.get(uid) is None

def test_get_all_and_by_attribute(user_repo, db_session):
    u1 = User(
        first_name="A",
        last_name="One",
        email="a@a.com",
        password="password1"
    )
    u2 = User(
        first_name="B",
        last_name="Two",
        email="b@b.com",
        password="password2"
    )
    user_repo.add(u1)
    user_repo.add(u2)

    all_users = user_repo.get_all()
    assert len(all_users) == 2

    by_email = user_repo.get_by_attribute("email", "b@b.com")
    assert by_email.id == u2.id
