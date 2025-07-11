# tests/test_repository.py
import pytest
from app import create_app, db
from app.models.user import User
from app.persistence.sqlalchemy_repository import SQLAlchemyRepository as Repository

@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config['TESTING']                 = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture(autouse=True)
def ctx(app):
    with app.app_context():
        yield

@pytest.fixture
def repo():
    return Repository(User)

class TestRepository:
    def test_add_and_get_user(self, repo):
        u = User(first_name="Alice", last_name="Smith", email="alice@example.com", password="pw")
        repo.add(u)
        fetched = repo.get(u.id)
        assert fetched is not None
        assert fetched.email == "alice@example.com"

    def test_get_all_and_delete_user(self, repo):
        u1 = User(first_name="Bob", last_name="Jones", email="bob@example.com", password="pw")
        u2 = User(first_name="Carol", last_name="King", email="carol@example.com", password="pw")
        repo.add(u1)
        repo.add(u2)
        all_users = repo.get_all()
        emails = [u.email for u in all_users]
        assert "bob@example.com" in emails and "carol@example.com" in emails

        repo.delete(u1.id)
        remaining = repo.get_all()
        assert all(u.email != "bob@example.com" for u in remaining)

    def test_update_user(self, repo):
        u = User(first_name="Dave", last_name="Brown", email="dave@example.com", password="pw")
        repo.add(u)
        # perform update
        repo.update(u.id, {"last_name": "White"})
        # fetch back to verify
        fetched = repo.get(u.id)
        assert fetched is not None
        assert fetched.last_name == "White"

    def test_get_by_attribute(self, repo):
        u = User(first_name="Eve", last_name="Black", email="eve@example.com", password="pw")
        repo.add(u)
        found = repo.get_by_attribute("email", "eve@example.com")
        assert found is not None
        assert found.id == u.id
