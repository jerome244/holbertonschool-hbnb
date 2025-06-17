# tests/test_users.py
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()

def test_create_and_get_user(client):
    # Create a user
    resp = client.post(
        "/api/v1/users/",
        json={"first_name":"Alice","last_name":"Smith","email":"alice@example.com"}
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["first_name"] == "Alice"
    user_id = data["id"]

    # Retrieve the same user
    resp2 = client.get(f"/api/v1/users/{user_id}")
    assert resp2.status_code == 200
    assert resp2.get_json()["email"] == "alice@example.com"

def test_missing_fields_returns_400(client):
    # Missing last_name and email
    resp = client.post("/api/v1/users/", json={"first_name":"Bob"})
    assert resp.status_code == 400
    assert b"Missing fields" in resp.data

def test_list_users(client):
    # Ensure endpoint returns a list (even if empty)
    resp = client.get("/api/v1/users/")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

def test_update_user(client):
    # Create one first
    post = client.post("/api/v1/users/", json={
        "first_name":"U","last_name":"P","email":"u.p@example.com"
    })
    uid = post.get_json()["id"]
    # Update
    resp = client.patch(f"/api/v1/users/{uid}", json={"first_name":"Updated"})
    assert resp.status_code == 200
    assert resp.get_json()["first_name"] == "Updated"

def test_delete_user(client):
    # Create then delete
    post = client.post("/api/v1/users/", json={
        "first_name":"D","last_name":"E","email":"d.e@example.com"
    })
    uid = post.get_json()["id"]
    resp = client.delete(f"/api/v1/users/{uid}")
    assert resp.status_code == 204
    # Now 404 if you fetch again
    resp2 = client.get(f"/api/v1/users/{uid}")
    assert resp2.status_code == 404
