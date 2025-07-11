# app/tests/conftest.py

import os
import pytest
from app import create_app, db
from app.persistence.sqlalchemy_repository import SQLAlchemyRepository
from app.models.user import User
from app.services.facade import HBnBFacade

@pytest.fixture(scope="session")
def app(tmp_path_factory):
    """Create a Flask app configured for testing with a temp SQLite DB."""
    # Force development mode so create_app picks up the right config
    os.environ["FLASK_ENV"] = "development"

    # Build a temporary sqlite file
    db_path = tmp_path_factory.mktemp("data") / "test.db"
    db_uri = f"sqlite:///{db_path}"

    # Create the app and override config
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": db_uri,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    # Initialize the schema once for the session
    with app.app_context():
        db.create_all()

    yield app

    # Teardown: delete the sqlite file
    try:
        os.remove(db_path)
    except OSError:
        pass

@pytest.fixture
def db_session(app):
    """Provide a transactional scope around a series of operations."""
    with app.app_context():
        yield db.session
        db.session.remove()
        db.drop_all()
        db.create_all()

@pytest.fixture
def user_repo(db_session):
    return SQLAlchemyRepository(User)

@pytest.fixture
def facade():
    return HBnBFacade()
