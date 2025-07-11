import pytest
from datetime import datetime
from app import create_app, db
from app.models.user import User

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

class TestUserModel:
    def test_user_creation(self):
        # Create with a password (non-nullable)
        u = User(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="supersecret"
        )
        # Before saving, id is None
        assert u.id is None

        db.session.add(u)
        db.session.commit()
        # After commit, id should be a non-empty string (UUID)
        assert isinstance(u.id, str)
        assert len(u.id) > 0
        # Timestamps set
        assert isinstance(u.created_at, datetime)
        assert isinstance(u.updated_at, datetime)
        # Verify fields persisted correctly
        fetched = User.query.get(u.id)
        assert fetched.email == "john.doe@example.com"
        assert fetched.first_name == "John"
