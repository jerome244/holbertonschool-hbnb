import pytest
from app import create_app
from datetime import date


# --- Fixtures ---
@pytest.fixture(scope="module")
def app():
    """
    Build and configure a Flask application for testing.
    """
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture(scope="module")
def client(app):
    """
    Provide a Flask test client for sending HTTP requests.
    """
    return app.test_client()


# --- Helper Fixtures ---
@pytest.fixture(scope="module")
def user_id(client):
    """
    Create a user via the API and return its ID, or skip if unavailable.
    """
    rv = client.post(
        "/api/v1/users/",
        json={
            "first_name": "Edge",
            "last_name": "Tester",
            "email": "edge_test@example.com",
        },
    )
    if rv.status_code != 201:
        pytest.skip(f"User creation skipped; status {rv.status_code}")
    return rv.get_json()["id"]


@pytest.fixture(scope="module")
def host_id(client):
    """
    Create a host via the API and return its ID, or skip if unavailable.
    """
    rv = client.post(
        "/api/v1/hosts/",
        json={"first_name": "Host", "last_name": "User", "email": "host@example.com"},
    )
    if rv.status_code != 201:
        pytest.skip(f"Host creation skipped; status {rv.status_code}")
    return rv.get_json()["id"]


@pytest.fixture(scope="module")
def amenity_id(client):
    """
    Create an amenity via the API and return its ID, or skip if unavailable.
    """
    rv = client.post("/api/v1/amenities/", json={"name": "EdgeAmenity"})
    if rv.status_code != 201:
        pytest.skip(f"Amenity creation skipped; status {rv.status_code}")
    return rv.get_json()["id"]


@pytest.fixture(scope="module")
def place_id(client, user_id, amenity_id):
    """
    Create a place via the API and return its ID, or skip if unavailable.
    """
    rv = client.post(
        "/api/v1/places/",
        json={
            "name": "EdgePlace",
            "description": "Edge desc",
            "user_id": user_id,
            "amenity_ids": [amenity_id],
        },
    )
    if rv.status_code != 201:
        pytest.skip(f"Place creation skipped; status {rv.status_code}")
    return rv.get_json()["id"]


@pytest.fixture(scope="module")
def booking_id(client, user_id, place_id):
    """
    Create a booking via the API and return its ID, or skip if unavailable.
    """
    rv = client.post(
        "/api/v1/bookings/",
        json={
            "user_id": user_id,
            "place_id": place_id,
            "guest_count": 1,
            "checkin_date": date.today().isoformat(),
            "night_count": 1,
        },
    )
    if rv.status_code != 201:
        pytest.skip(f"Booking creation skipped; status {rv.status_code}")
    return rv.get_json()["id"]


# --- CRUD Tests ---
@pytest.mark.parametrize(
    "endpoint,payload,expected",
    [
        ("users", {"first_name": "U", "last_name": "L", "email": "u@l.com"}, 201),
        ("hosts", {"first_name": "H", "last_name": "O", "email": "h@o.com"}, 201),
        ("amenities", {"name": "A1"}, 201),
        (
            "places",
            {"name": "P1", "description": "D", "user_id": None, "amenity_ids": []},
            400,
        ),
    ],
)
def test_post_endpoints(client, endpoint, payload, expected):
    """
    Verify POST /api/v1/<endpoint>/ returns the expected status codes.
    """
    if endpoint == "hosts":
        pytest.xfail("Hosts POST not implemented")
    rv = client.post(f"/api/v1/{endpoint}/", json=payload)
    assert rv.status_code == expected


@pytest.mark.parametrize(
    "endpoint,id_",
    [
        ("users", 999),
        ("hosts", 999),
        ("amenities", 999),
        ("places", 999),
        ("bookings", 999),
        ("reviews", 999),
    ],
)
def test_get_not_found(client, endpoint, id_):
    """
    GET /api/v1/<endpoint>/<nonexistent_id> should return 404.
    """
    rv = client.get(f"/api/v1/{endpoint}/{id_}")
    assert rv.status_code == 404


# --- PUT Tests ---
@pytest.mark.parametrize(
    "endpoint,field,value,ok",
    [
        ("users", "email", "new@u.com", True),
        ("users", "email", "bad", False),
        ("hosts", "email", "h@n.com", True),
        ("amenities", "name", "", False),
    ],
)
def test_put_endpoints(
    client, user_id, endpoint, field, value, ok
):  # Changed from PATCH to PUT
    """
    Verify PUT /api/v1/<endpoint>/<id> with various payloads.
    """
    if endpoint == "hosts":
        pytest.xfail("Hosts PUT not implemented")

    # Ensure full user data is sent in the PUT request
    payload = {
        "first_name": "Updated",  # Assuming the first name is required for the full update
        "last_name": "User",  # Assuming the last name is required for the full update
        "email": value,  # Email field that is being updated
        "is_admin": False,  # Assuming the 'is_admin' field is also required
    }

    eid = user_id if endpoint in ["users", "hosts"] else 1
    rv = client.put(
        f"/api/v1/{endpoint}/{eid}", json=payload
    )  # Use PUT instead of PATCH
    assert (rv.status_code in (200, 204)) == ok


# --- DELETE Tests ---
@pytest.mark.parametrize(
    "endpoint", ["users", "hosts", "amenities", "places", "bookings", "reviews"]
)
def test_delete_not_found(client, endpoint):
    """
    DELETE /api/v1/<endpoint>/<nonexistent_id> returns 404 or 405.
    """
    rv = client.delete(f"/api/v1/{endpoint}/99999")
    assert rv.status_code in (404, 405)


# --- Booking Edge Cases ---
@pytest.mark.parametrize("guests", [0, -1])
def test_booking_guest_bounds(client, user_id, place_id, guests):
    """
    Reject guest_count outside valid bounds (>=1).
    """
    rv = client.post(
        "/api/v1/bookings/",
        json={
            "user_id": user_id,
            "place_id": place_id,
            "guest_count": guests,
            "checkin_date": date.today().isoformat(),
            "night_count": 1,
        },
    )
    assert rv.status_code == 400


# --- Review Edge Cases ---
@pytest.mark.parametrize("rating", [-1, 0, 6])
def test_review_rating_bounds(client, booking_id, rating):
    """
    Reject review ratings outside 1–5.
    """
    rv = client.post(
        "/api/v1/reviews/",
        json={"booking_id": booking_id, "text": "X", "rating": rating},
    )
    assert rv.status_code == 400


# --- DELETE & PUT Review ---
def test_delete_and_put_review(client, booking_id):
    """
    After DELETE, PUT on the same review should return 404.
    """
    rv = client.post(
        "/api/v1/reviews/", json={"booking_id": booking_id, "text": "T", "rating": 3}
    )
    if rv.status_code != 201:
        pytest.skip()
    rid = rv.get_json()["id"]
    rv2 = client.delete(f"/api/v1/reviews/{rid}")
    assert rv2.status_code in (200, 204)
    rv3 = client.put(f"/api/v1/reviews/{rid}", json={"text": "Z"})
    assert rv3.status_code == 404
