# tests/test_facade.py
import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.services.facade import HBnBFacade

@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture(autouse=True)
def app_context(app):
    # This makes sure that for *every* test, Flask's `current_app`
    # and `db.session` are bound to an application context.
    with app.app_context():
        yield

@pytest.fixture
def facade():
    # We can just instantiate the facade; every call below
    # happens inside the above app_context.
    return HBnBFacade()

class TestFacade:
    def test_create_and_get_user(self, facade):
        user = facade.create_user({
            "first_name": "Bob",
            "last_name":  "Builder",
            "email":      "bob.builder@example.com",
            "password":   "secret"
        })
        assert user.email == "bob.builder@example.com"
        fetched = facade.get_user(user.id)
        assert fetched.id == user.id
        assert fetched.email == user.email

    def test_create_host(self, facade):
        host = facade.create_host({
            "first_name": "Test",
            "last_name":  "Host",
            "email":      "host@example.com",
            "password":   "hostpass"
        })
        assert host.email == "host@example.com"
        fetched = facade.get_host(host.id)
        assert fetched.id == host.id

    def test_create_place(self, facade):
        host = facade.create_host({
            "first_name": "Place",
            "last_name":  "Owner",
            "email":      "owner@example.com",
            "password":   "ownpass"
        })
        place = facade.create_place({
            "title":       "Test Place",
            "description": "A lovely spot",
            "host_id":     host.id,
            "price":       100.0,
            "capacity":    4
        })
        assert place.title == "Test Place"
        assert place.capacity == 4
        fetched = facade.get_place(place.id)
        assert fetched.id == place.id

    def test_create_and_get_booking(self, facade):
        user = facade.create_user({
            "first_name": "Booking",
            "last_name":  "User",
            "email":      "booking.user@example.com",
            "password":   "bookpass"
        })
        host = facade.create_host({
            "first_name": "Booking",
            "last_name":  "Host",
            "email":      "bhost@example.com",
            "password":   "bhpass"
        })
        place = facade.create_place({
            "title":       "Booking Place",
            "description": "Cozy",
            "host_id":     host.id,
            "price":       50.0,
            "capacity":    2
        })
        start = datetime.utcnow() + timedelta(days=1)
        end   = start + timedelta(days=2)
        booking = facade.create_booking({
            "user_id":     user.id,
            "place_id":    place.id,
            "start_date":  start,
            "end_date":    end,
            "guest_count": 2
        })
        assert booking.user_id    == user.id
        assert booking.place_id   == place.id
        assert booking.guest_count == 2

        fetched = facade.get_booking(booking.id)
        assert fetched.id          == booking.id
        assert fetched.start_date  == booking.start_date
        assert fetched.end_date    == booking.end_date
        assert fetched.guest_count == booking.guest_count
