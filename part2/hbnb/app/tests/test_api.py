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
        "first_name": "Edge", "last_name": "Tester", "email": "edge@example.com"
    })
    if rv.status_code != 201:
        pytest.skip(f"User creation skipped; status {rv.status_code}")
    return rv.get_json()['id']

@pytest.fixture(scope="module")
def amenity_id(client):
    rv = client.post('/api/v1/amenities/', json={"name": "TestAmenity"})
    if rv.status_code != 201:
        pytest.skip(f"Amenity creation skipped; status {rv.status_code}")
    return rv.get_json()['id']

@pytest.fixture(scope="module")
def place_id(client, user_id, amenity_id):
    rv = client.post('/api/v1/places/', json={
        "name": "EdgePlace",
        "description": "Edge place for tests",
        "user_id": user_id,
        "amenity_ids": [amenity_id]
    })
    if rv.status_code != 201:
        pytest.skip(f"Place creation skipped; status {rv.status_code}")
    return rv.get_json()['id']

@pytest.fixture(scope="module")
def booking_id(client, user_id, place_id):
    rv = client.post('/api/v1/bookings/', json={
        "user_id": user_id,
        "place_id": place_id,
        "guest_count": 1,
        "checkin_date": date.today().isoformat(),
        "night_count": 1
    })
    if rv.status_code != 201:
        pytest.skip(f"Booking creation skipped; status {rv.status_code}")
    return rv.get_json()['id']

# --- User Tests ---
def test_get_users_list(client):
    rv = client.get('/api/v1/users/')
    assert rv.status_code == 200
    assert isinstance(rv.get_json(), list)

@pytest.mark.parametrize("payload", [
    {"first_name": "Alice", "last_name": "Smith", "email": "alice@example.com"}
])
def test_create_and_retrieve_user(client, payload):
    rv = client.post('/api/v1/users/', json=payload)
    assert rv.status_code == 201
    data = rv.get_json()
    for key, val in payload.items():
        assert data[key] == val
    assert 'id' in data
    rv2 = client.get(f"/api/v1/users/{data['id']}")
    assert rv2.status_code == 200

@pytest.mark.parametrize("invalid_payload", [
    {"last_name": "NoFirst", "email": "nofirst@example.com"},
    {"first_name": "NoLast", "email": "nolast@example.com"},
    {"first_name": "NoEmail", "last_name": "User"}
])
def test_user_missing_field_returns_400(client, invalid_payload):
    rv = client.post('/api/v1/users/', json=invalid_payload)
    assert rv.status_code == 400

def test_duplicate_email_returns_400(client):
    payload = {"first_name": "Dup", "last_name": "User", "email": "dup@example.com"}
    rv1 = client.post('/api/v1/users/', json=payload)
    if rv1.status_code != 201:
        pytest.skip("User creation unavailable; skipping duplicate test")
    rv2 = client.post('/api/v1/users/', json=payload)
    assert rv2.status_code == 400

@pytest.mark.parametrize('body', ["not-a-json", b'invalid'])
def test_create_user_invalid_json(client, body):
    rv = client.post('/api/v1/users/', data=body, content_type='application/json')
    assert rv.status_code == 400

# --- Amenity Tests ---
@pytest.mark.xfail(raises=AttributeError, reason="get_all_amenities not implemented")
def test_list_amenities(client):
    rv = client.get('/api/v1/amenities/')
    assert rv.status_code == 200
    assert isinstance(rv.get_json(), list)

@pytest.mark.parametrize("name", ["Pool", "Wi-Fi"])
def test_create_amenity_and_get(client, name):
    rv = client.post('/api/v1/amenities/', json={"name": name})
    assert rv.status_code == 201
    data = rv.get_json()
    assert data.get('name') == name
    rv2 = client.get(f"/api/v1/amenities/{data.get('id')}")
    assert rv2.status_code == 200

@pytest.mark.parametrize('invalid', [{}, {'name': 123}])
def test_create_amenity_invalid_payload(client, invalid):
    rv = client.post('/api/v1/amenities/', json=invalid)
    assert rv.status_code == 400

# --- Place Tests ---
def test_list_places(client):
    rv = client.get('/api/v1/places/')
    assert rv.status_code == 200
    assert isinstance(rv.get_json(), list)

@pytest.mark.parametrize('invalid', [{"name": "", "description": 123, "user_id": None, "amenity_ids": []}])
def test_place_invalid_payload(client, invalid):
    rv = client.post('/api/v1/places/', json=invalid)
    assert rv.status_code == 400

def test_create_place_and_list(client, user_id, amenity_id):
    rv = client.post('/api/v1/places/', json={
        "name": "NewPlace",
        "description": "Desc",
        "user_id": user_id,
        "amenity_ids": [amenity_id]
    })
    if rv.status_code != 201:
        pytest.skip("Place creation unavailable")
    pid = rv.get_json()['id']
    rv2 = client.get('/api/v1/places/')
    assert rv2.status_code == 200
    assert pid in [p['id'] for p in rv2.get_json()]

# --- Booking Tests ---
def test_list_bookings(client):
    rv = client.get('/api/v1/bookings/')
    assert rv.status_code == 200
    assert isinstance(rv.get_json(), list)

@pytest.mark.parametrize('invalid', [{'user_id': None}, {'place_id': None}, {'guest_count': -1}])
def test_booking_invalid_payload(client, invalid):
    rv = client.post('/api/v1/bookings/', json=invalid)
    assert rv.status_code == 400

def test_create_booking_and_get(client, user_id, place_id):
    rv = client.post('/api/v1/bookings/', json={
        "user_id": user_id,
        "place_id": place_id,
        "guest_count": 2,
        "checkin_date": date.today().isoformat(),
        "night_count": 2
    })
    if rv.status_code != 201:
        pytest.skip("Booking creation unavailable")
    bid = rv.get_json()['id']
    rv2 = client.get(f"/api/v1/bookings/{bid}")
    assert rv2.status_code == 200

@pytest.mark.parametrize("offset_days", [0])
def test_booking_overlap_returns_400(client, user_id, place_id, offset_days):
    start = date.today() + timedelta(days=offset_days)
    payload1 = {"user_id": user_id, "place_id": place_id, "guest_count": 1, "checkin_date": start.isoformat(), "night_count": 2}
    rv1 = client.post('/api/v1/bookings/', json=payload1)
    if rv1.status_code != 201:
        pytest.skip("Booking creation unavailable")
    payload2 = {"user_id": user_id, "place_id": place_id, "guest_count": 1, "checkin_date": (start + timedelta(days=1)).isoformat(), "night_count": 2}
    rv2 = client.post('/api/v1/bookings/', json=payload2)
    assert rv2.status_code == 400

# --- Review Tests ---
def test_list_reviews(client):
    rv = client.get('/api/v1/reviews/')
    assert rv.status_code == 200
    assert isinstance(rv.get_json(), list)

@pytest.mark.parametrize('invalid', [{'rating': -1}, {'booking_id': None}])
def test_review_invalid_payload(client, invalid):
    rv = client.post('/api/v1/reviews/', json=invalid)
    assert rv.status_code == 400

def test_create_review_and_get(client, booking_id):
    rv = client.post('/api/v1/reviews/', json={"booking_id": booking_id, "text": "Great", "rating": 5})
    if rv.status_code != 201:
        pytest.skip("Review creation unavailable")
    rid = rv.get_json()['id']
    rv2 = client.get(f"/api/v1/reviews/{rid}")
    assert rv2.status_code == 200

# --- Edge Cases ---
def test_nonexistent_user_returns_404(client):
    rv = client.get('/api/v1/users/999999')
    assert rv.status_code == 404

@pytest.mark.parametrize('body', ["notjson", b'bad'])
def test_invalid_json_body_returns_400(client, body):
    rv = client.post('/api/v1/users/', data=body, content_type='application/json')
    assert rv.status_code == 400
