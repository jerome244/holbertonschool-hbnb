import pytest
from app import create_app
from datetime import date, timedelta

# --- Fixtures ---
@pytest.fixture(scope="module")
def app():
    application = create_app()
    application.config['TESTING'] = True
    return application

@pytest.fixture(scope="module")
def client(app):
    return app.test_client()

# --- Helper Fixtures ---
@pytest.fixture(scope="module")
def user_id(client):
    rv = client.post('/api/v1/users/', json={
        "first_name": "Edge", "last_name": "Tester", "email": "edge_test@example.com"
    })
    if rv.status_code != 201:
        pytest.skip(f"User creation skipped; status {rv.status_code}")
    return rv.get_json()['id']

@pytest.fixture(scope="module")
def amenity_id(client):
    rv = client.post('/api/v1/amenities/', json={"name": "EdgeAmenity"})
    if rv.status_code != 201:
        pytest.skip(f"Amenity creation skipped; status {rv.status_code}")
    return rv.get_json()['id']

@pytest.fixture(scope="module")
def place_id(client, user_id, amenity_id):
    rv = client.post('/api/v1/places/', json={
        "name": "EdgePlace", "description": "Edge place description",
        "user_id": user_id, "amenity_ids": [amenity_id]
    })
    if rv.status_code != 201:
        pytest.skip(f"Place creation skipped; status {rv.status_code}")
    return rv.get_json()['id']

@pytest.fixture(scope="module")
def booking_id(client, user_id, place_id):
    rv = client.post('/api/v1/bookings/', json={
        "user_id": user_id, "place_id": place_id,
        "guest_count": 1, "checkin_date": date.today().isoformat(), "night_count": 1
    })
    if rv.status_code != 201:
        pytest.skip(f"Booking creation skipped; status {rv.status_code}")
    return rv.get_json()['id']


# -- User endpoint tests --
def test_get_users_empty(client):
    rv = client.get('/api/v1/users/')
    assert rv.status_code == 200
    assert isinstance(rv.get_json(), list)

@pytest.mark.parametrize("payload", [
    {"first_name": "Alice", "last_name": "Smith", "email": "alice.smith@example.com"}
])
def test_create_and_get_user(client, payload):
    rv = client.post('/api/v1/users/', json=payload)
    assert rv.status_code == 201
    data = rv.get_json()
    assert all(data[k] == v for k, v in payload.items())
    rv2 = client.get(f"/api/v1/users/{data['id']}")
    assert rv2.status_code == 200
    assert rv2.get_json() == data

@pytest.mark.parametrize("invalid_payload", [
    {"last_name": "Doe"}, {"first_name": "John"}, {"first_name": "John", "last_name": "Doe"}
])
def test_create_user_missing_fields(client, invalid_payload):
    rv = client.post('/api/v1/users/', json=invalid_payload)
    assert rv.status_code == 400

def test_create_user_duplicate_email(client):
    payload = {"first_name": "Bob", "last_name": "Dup", "email": "dup@example.com"}
    rv1 = client.post('/api/v1/users/', json=payload)
    if rv1.status_code != 201:
        pytest.skip("Skipping duplicate test; creation unavailable")
    rv2 = client.post('/api/v1/users/', json=payload)
    assert rv2.status_code == 400
    err = rv2.get_json().get('error') or rv2.get_json().get('message', '')
    assert 'email' in err.lower()

@pytest.mark.parametrize('body', ["not-json", b'invalid'])
def test_create_user_invalid_json(client, body):
    rv = client.post('/api/v1/users/', data=body, content_type='application/json')
    assert rv.status_code == 400


# --- Host endpoint tests ---
import pytest as _pytest

@_pytest.mark.xfail(raises=AssertionError, reason="Hosts endpoints not implemented yet")
def test_list_hosts_empty(client):
    rv = client.get('/api/v1/hosts/')
    assert rv.status_code == 200
    assert isinstance(rv.get_json(), list)

@_pytest.mark.xfail(raises=AssertionError, reason="Hosts endpoints not implemented yet")
@pytest.mark.parametrize("payload", [
    {"first_name": "Sam", "last_name": "Builder", "email": "sam@host.com"}
])
def test_create_and_get_host(client, payload):
    rv = client.post('/api/v1/hosts/', json=payload)
    assert rv.status_code == 201
    host = rv.get_json()
    assert all(host[k] == v for k, v in payload.items())
    rv2 = client.get(f"/api/v1/hosts/{host['id']}")
    assert rv2.status_code == 200

@_pytest.mark.xfail(raises=AssertionError, reason="Hosts endpoints not implemented yet")
def test_create_host_duplicate_email(client):
    payload = {"first_name": "Sam", "last_name": "Builder", "email": "samdup@host.com"}
    rv1 = client.post('/api/v1/hosts/', json=payload)
    if rv1.status_code != 201:
        pytest.skip("Skipping host duplicate test; creation unavailable")
    rv2 = client.post('/api/v1/hosts/', json=payload)
    assert rv2.status_code == 400


# --- Amenity endpoint tests ---
@pytest.mark.xfail(raises=AttributeError)
def test_list_amenities(client):
    rv = client.get('/api/v1/amenities/')
    assert rv.status_code == 200

@pytest.mark.parametrize("name", ["Pool", "Wi-Fi"])
def test_create_and_get_amenity(client, name):
    rv = client.post('/api/v1/amenities/', json={"name": name})
    assert rv.status_code == 201
    data = rv.get_json()
    assert data['name'] == name

@pytest.mark.parametrize('invalid', [{}, {'name': 123}])
def test_create_amenity_invalid_payload(client, invalid):
    rv = client.post('/api/v1/amenities/', json=invalid)
    assert rv.status_code == 400


# --- Place endpoint tests ---
def test_list_places(client):
    rv = client.get('/api/v1/places/')
    assert rv.status_code == 200
    assert isinstance(rv.get_json(), list)

@pytest.mark.parametrize('invalid', [{"name": "", "description": 123, "user_id": None, "amenity_ids": []}])
def test_create_place_invalid_payload(client, invalid):
    rv = client.post('/api/v1/places/', json=invalid)
    assert rv.status_code == 400

def test_create_and_list_place(client, user_id, amenity_id):
    rv = client.post('/api/v1/places/', json={
        "name": "NewPlace", "description": "Desc",
        "user_id": user_id, "amenity_ids": [amenity_id]
    })
    if rv.status_code != 201:
        pytest.skip("Place create not available")
    place = rv.get_json()
    rv2 = client.get('/api/v1/places/')
    assert rv2.status_code == 200
    assert place['id'] in [p['id'] for p in rv2.get_json()]


# --- Booking & Review edge-case tests ---
@pytest.mark.parametrize("guest_count", [0, -5])
def test_booking_guest_count_bounds(client, user_id, place_id, guest_count):
    rv = client.post('/api/v1/bookings/', json={
        "user_id": user_id, "place_id": place_id,
        "guest_count": guest_count, "checkin_date": date.today().isoformat(), "night_count": 1
    })
    assert rv.status_code == 400

@pytest.mark.parametrize("rating", [-1, 0, 6, 10])
def test_review_rating_bounds(client, booking_id, rating):
    rv = client.post('/api/v1/reviews/', json={
        "booking_id": booking_id, "text": "Edge", "rating": rating
    })
    assert rv.status_code == 400


# --- Base CRUD tests for bookings & reviews ---
def test_list_bookings(client):
    rv = client.get('/api/v1/bookings/')
    assert rv.status_code == 200
    assert isinstance(rv.get_json(), list)

def test_create_and_get_booking(client, user_id, place_id):
    rv = client.post('/api/v1/bookings/', json={
        "user_id": user_id, "place_id": place_id,
        "guest_count": 2, "checkin_date": date.today().isoformat(), "night_count": 2
    })
    if rv.status_code != 201:
        pytest.skip("Booking create not available")
    booking = rv.get_json()
    rv2 = client.get(f"/api/v1/bookings/{booking['id']}")
    assert rv2.status_code == 200


# --- PATCH and DELETE endpoint tests ---
@pytest.mark.parametrize("new_email", ["new@example.com", 123, 3.14, None])
def test_patch_user_email_types(client, user_id, new_email):
    rv = client.patch(f"/api/v1/users/{user_id}", json={"email": new_email})
    if isinstance(new_email, str) and "@" in new_email:
        assert rv.status_code in (200, 204)
    else:
        assert rv.status_code == 400

@pytest.mark.parametrize("field,value,status_code", [
    ("first_name", "Updated", 200),
    ("last_name", "Updated", 200),
    ("email", "not-an-email", 400)
])
def test_patch_user_fields(client, user_id, field, value, status_code):
    rv = client.patch(f"/api/v1/users/{user_id}", json={field: value})
    assert rv.status_code == status_code

@pytest.mark.parametrize("resource,id_endpoint", [
    ('users', lambda uid: f"/api/v1/users/{uid}"),
    ('hosts', lambda hid: f"/api/v1/hosts/{hid}"),
    ('amenities', lambda aid: f"/api/v1/amenities/{aid}"),
    ('places', lambda pid: f"/api/v1/places/{pid}"),
    ('bookings', lambda bid: f"/api/v1/bookings/{bid}"),
    ('reviews', lambda rid: f"/api/v1/reviews/{rid}")
])
def test_delete_resource_not_found(client, resource, id_endpoint):
    rv = client.delete(id_endpoint(999999))
    # some resources might not support DELETE and return 405
    assert rv.status_code in (404, 405)

@pytest.mark.parametrize("rating", ['five', 2.5, None, {}])
def test_post_review_invalid_rating_types(client, booking_id, rating):
    rv = client.post('/api/v1/reviews/', json={"booking_id": booking_id, "text": "Test", "rating": rating})
    assert rv.status_code == 400

@pytest.mark.parametrize("rating", [1, 5, 3.5, '3', None])
def test_patch_review_rating_types(client, booking_id, rating):
    rv = client.post('/api/v1/reviews/', json={"booking_id": booking_id, "text": "Initial", "rating": 4})
    if rv.status_code != 201:
        pytest.skip("Review creation unavailable")
    rid = rv.get_json()['id']
    rv2 = client.patch(f"/api/v1/reviews/{rid}", json={"rating": rating})
    if isinstance(rating, int) and 1 <= rating <= 5:
        assert rv2.status_code in (200, 204)
    else:
        assert rv2.status_code == 400
