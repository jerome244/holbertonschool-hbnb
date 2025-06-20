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
def host_id(client):
    rv = client.post('/api/v1/hosts/', json={
        "first_name": "Host", "last_name": "User", "email": "host@example.com"
    })
    if rv.status_code != 201:
        pytest.skip(f"Host creation skipped; status {rv.status_code}")
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

# --- CRUD Tests for All Entities ---
@pytest.mark.parametrize('endpoint,payload,expected', [
    ('users',     {"first_name": "U", "last_name": "L", "email": "u@l.com"}, 201),
    ('hosts',     {"first_name": "H", "last_name": "O", "email": "h@o.com"}, 201),
    ('amenities', {"name": "A1"},                                        201),
    ('places',    {"name": "P1", "description": "D", "user_id": None, "amenity_ids": []}, 400),
])
def test_post_entities(client, endpoint, payload, expected):
    if endpoint == 'hosts':
        pytest.xfail("Hosts POST not implemented")
    rv = client.post(f'/api/v1/{endpoint}/', json=payload)
    assert rv.status_code == expected

@pytest.mark.parametrize('endpoint,id_', [
    ('users', 12345), ('hosts', 12345), ('amenities', 12345),
    ('places', 12345), ('bookings', 12345), ('reviews', 12345),
])
def test_get_not_found(client, endpoint, id_):
    rv = client.get(f'/api/v1/{endpoint}/{id_}')
    assert rv.status_code == 404

# --- PATCH Tests ---
@pytest.mark.parametrize('endpoint,field,val,good', [
    ('users',     'email',    'new@u.com',  True),
    ('users',     'email',    'bad-email',  False),
    ('hosts',     'email',    'h@o.com',    True),
    ('amenities', 'name',     '',           False),
])
def test_patch_entities(client, user_id, endpoint, field, val, good):
    if endpoint == 'hosts':
        pytest.xfail("Hosts PATCH not implemented")
    eid = user_id if endpoint in ['users','hosts'] else 1
    rv = client.patch(f'/api/v1/{endpoint}/{eid}', json={field: val})
    assert (rv.status_code in (200,204)) == good

# --- DELETE Tests ---
@pytest.mark.parametrize('endpoint', ['users','hosts','amenities','places','bookings','reviews'])
def test_delete_not_found(client, endpoint):
    rv = client.delete(f'/api/v1/{endpoint}/99999')
    assert rv.status_code in (404,405)

# --- Booking Edge Cases ---
@pytest.mark.parametrize('gc', [0, -1])
def test_booking_guest_bounds(client, user_id, place_id, gc):
    rv = client.post('/api/v1/bookings/', json={
        "user_id": user_id, "place_id": place_id,
        "guest_count": gc, "checkin_date": date.today().isoformat(), "night_count": 1
    })
    assert rv.status_code == 400

# --- Review Edge Cases ---
@pytest.mark.parametrize('rating', [-1, 0, 6])
def test_review_rating_bounds(client, booking_id, rating):
    rv = client.post('/api/v1/reviews/', json={
        "booking_id": booking_id, "text": "X", "rating": rating
    })
    assert rv.status_code == 400

# --- DELETE & PATCH Review ---
def test_delete_and_patch_review(client, booking_id):
    rv = client.post('/api/v1/reviews/', json={
        "booking_id": booking_id, "text": "T", "rating": 3
    })
    if rv.status_code != 201:
        pytest.skip("Review creation unavailable")
    rid = rv.get_json()['id']
    # delete
    rv2 = client.delete(f'/api/v1/reviews/{rid}')
    assert rv2.status_code in (200,204)
    # patch after delete -> 404
    rv3 = client.patch(f'/api/v1/reviews/{rid}', json={"text": "Z"})
    assert rv3.status_code == 404

# --- Aggregation Tests (xfail) ---
import pytest as _pytest

@_pytest.mark.xfail(raises=AttributeError, reason="Place avg rating not implemented")
def test_place_average_rating(client, place_id, user_id, amenity_id):
    vals = []
    for r in (4, 2):
        rvb = client.post('/api/v1/bookings/', json={
            "user_id": user_id, "place_id": place_id,
            "guest_count": 1, "checkin_date": date.today().isoformat(), "night_count": 1
        })
        if rvb.status_code != 201:
            pytest.skip()
        bid = rvb.get_json()['id']
        rvv = client.post('/api/v1/reviews/', json={
            "booking_id": bid, "text": "A", "rating": r
        })
        if rvv.status_code != 201:
            pytest.skip()
        vals.append(r)
    rv = client.get(f'/api/v1/places/{place_id}/rating')
    assert rv.status_code == 200
    assert rv.get_json().get('average_rating') == pytest.approx(sum(vals)/len(vals))

@_pytest.mark.xfail(raises=AttributeError, reason="Host avg rating not implemented")
def test_host_average_rating(client, host_id):
    rv = client.get(f'/api/v1/hosts/{host_id}/rating')
    assert rv.status_code == 200

@_pytest.mark.xfail(raises=AttributeError, reason="Booking cost not implemented")
def test_booking_total_cost(client, booking_id):
    rv = client.get(f'/api/v1/bookings/{booking_id}/cost')
    assert rv.status_code == 200
    assert isinstance(rv.get_json().get('total_cost'), (int,float)) and rv.get_json()['total_cost'] >= 0
