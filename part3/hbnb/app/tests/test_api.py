# tests/test_api.py
import pytest
import app.api.v1.users     # Ensure your @ns.route handlers are registered
import app.api.v1.bookings
from app import create_app, db

@pytest.fixture(scope="module")
def client():
    app = create_app()
    app.config['TESTING']                 = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="module")
def auth_token(client):
    # 1) Seed an admin user directly via the facade
    app = client.application
    with app.app_context():
        from app.services.facade import HBnBFacade
        HBnBFacade().create_user({
            "first_name": "Auth",
            "last_name":  "User",
            "email":      "auth.user@example.com",
            "password":   "authpass",
            "is_admin":   True
        })
    # 2) Log in to get an admin JWT
    res = client.post(
        '/api/v1/auth/login',
        json={"email": "auth.user@example.com", "password": "authpass"}
    )
    assert res.status_code == 200
    return res.get_json()['access_token']

@pytest.mark.api
class TestUserAPI:
    def test_get_users_empty(self, client, auth_token):
        headers = {'Authorization': f'Bearer {auth_token}'}
        res = client.get('/api/v1/users/users', headers=headers)
        assert res.status_code == 200
        users = res.get_json()
        # Only the seeded admin is present initially
        assert isinstance(users, list)
        assert len(users) == 1
        assert users[0]['email'] == "auth.user@example.com"
        assert users[0]['is_admin'] is True

    def test_post_user(self, client, auth_token):
        headers = {'Authorization': f'Bearer {auth_token}'}
        payload = {
            "first_name": "Test",
            "last_name":  "User",
            "email":      "test.user@example.com",
            "password":   "testpass"
        }
        res = client.post('/api/v1/users/users', json=payload, headers=headers)
        assert res.status_code == 201
        data = res.get_json()
        assert data['email'] == payload['email']
        assert data['is_admin'] is False
        assert 'id' in data

    def test_get_users_after_post(self, client, auth_token):
        headers = {'Authorization': f'Bearer {auth_token}'}
        res = client.get('/api/v1/users/users', headers=headers)
        assert res.status_code == 200
        emails = [u['email'] for u in res.get_json()]
        assert "auth.user@example.com" in emails
        assert "test.user@example.com" in emails
