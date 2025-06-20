import pytest
from datetime import datetime, timedelta
from app.services.facade import HBnBFacade
from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.host import Host
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.booking import Booking
from app.models.review import Review

# --- Repository Tests ---
def test_inmemory_repository_crud():
    repo = InMemoryRepository()
    class Dummy:
        def __init__(self, id, value):
            self.id = id
            self.value = value
    d1 = Dummy('1', 'a')
    d2 = Dummy('2', 'b')
    repo.add(d1)
    repo.add(d2)
    assert repo.get('1') is d1
    assert set(o.id for o in repo.get_all()) == {'1', '2'}
    d1.value = 'aa'
    assert repo.get('1').value == 'aa'
    repo.delete('1')
    assert repo.get('1') is None

# --- Facade Tests ---
@pytest.fixture
def facade():
    return HBnBFacade()

# User CRUD
def test_facade_user_crud(facade):
    data = {'first_name': 'Alice', 'last_name': 'Liddell', 'email': 'alice@example.com'}
    user = facade.create_user(data)
    assert isinstance(user, User)
    uid = user.id
    fetched = facade.get_user(uid)
    assert fetched.email == data['email']
    facade.update_user(uid, {'first_name': 'Al'})
    assert facade.get_user(uid).first_name == 'Al'
    all_users = facade.list_users()
    assert any(u.id == uid for u in all_users)
    facade.delete_user(uid)
    assert facade.get_user(uid) is None

# Host CRUD
def test_facade_host_crud(facade):
    data = {'first_name': 'Bob', 'last_name': 'Builder', 'email': 'bob@build.com'}
    host = facade.create_host(data)
    hid = host.id
    assert facade.get_host(hid).email == data['email']
    facade.update_host(hid, {'last_name': 'Construct'})
    assert facade.get_host(hid).last_name == 'Construct'
    all_hosts = facade.list_hosts()
    assert any(h.id == hid for h in all_hosts)
    facade.delete_host(hid)
    assert facade.get_host(hid) is None

# Amenity CRUD
def test_facade_amenity_crud(facade):
    data = {'name': 'Wi-Fi'}
    amenity = facade.create_amenity(data)
    aid = amenity.id
    assert facade.get_amenity(aid).name == 'Wi-Fi'
    all_amenities = facade.list_amenities()
    assert any(a.id == aid for a in all_amenities)
    facade.delete_amenity(aid)
    assert facade.get_amenity(aid) is None

# Place CRUD
def test_facade_place_crud(facade):
    host = facade.create_host({'first_name':'H','last_name':'Test','email':'h@test.com'})
    hid = host.id
    data = {
        'host_id': hid,
        'title': 'MyPlace',
        'description': 'Desc',
        'latitude': 10.0,
        'longitude': 20.0,
        'capacity': 2,
        'price': 100.0
    }
    place = facade.create_place(data)
    pid = place.id
    assert facade.get_place(pid).title == 'MyPlace'
    facade.update_place(pid, {'title': 'NewTitle'})
    assert facade.get_place(pid).title == 'NewTitle'
    all_places = facade.list_places()
    assert any(p.id == pid for p in all_places)
    deleted = facade.delete_place(pid)
    assert deleted.id == pid and facade.get_place(pid) is None

# Booking CRUD
def test_facade_booking_crud(facade):
    user = facade.create_user({'first_name':'X','last_name':'Y','email':'x@y.com'})
    host = facade.create_host({'first_name':'A','last_name':'B','email':'a@b.com'})
    place = facade.create_place({
        'host_id': host.id,
        'title': 'T',
        'description': 'Desc',
        'latitude': 0.0,
        'longitude': 0.0,
        'capacity': 1,
        'price': 50.0
    })
    data = {
        'user_id': user.id,
        'place_id': place.id,
        'guest_count': 1,
        'checkin_date': datetime.now().isoformat(),
        'night_count': 2
    }
    booking = facade.create_booking(data)
    bid = booking.id
    assert isinstance(facade.get_booking(bid), Booking)
    all_b = facade.list_bookings()
    assert any(b.id == bid for b in all_b)
    facade.delete_booking(bid)
    assert facade.get_booking(bid) is None

# Review CRUD
def test_facade_review_crud(facade):
    user = facade.create_user({'first_name':'R','last_name':'U','email':'r@u.com'})
    host = facade.create_host({'first_name':'H','last_name':'R','email':'h@r.com'})
    place = facade.create_place({
        'host_id': host.id,
        'title': 'T2',
        'description': 'Desc',
        'latitude': 0.0,
        'longitude': 0.0,
        'capacity': 1,
        'price': 75.0
    })
    booking = facade.create_booking({
        'user_id': user.id,
        'place_id': place.id,
        'guest_count': 1,
        'checkin_date': datetime.now().isoformat(),
        'night_count': 1
    })
    review = facade.create_review({'booking_id': booking.id, 'text': 'Good', 'rating': 5})
    rid = review.id
    assert isinstance(facade.get_review(rid), Review)
    all_rev = facade.list_reviews()
    assert any(r.id == rid for r in all_rev)
    facade.delete_review(rid)
    assert facade.get_review(rid) is None

# --- Model Class Integrity ---
def test_classes_model_integrity():
    u = User(first_name='A', last_name='B', email='a@b.com')
    assert hasattr(u, 'id') and u.email == 'a@b.com'
    h = Host(first_name='H', last_name='O', email='h@o.com')
    assert hasattr(h, 'id') and h.email == 'h@o.com'
    a = Amenity(name='TestAmenity')
    assert hasattr(a, 'id') and a.name == 'TestAmenity'
    p = Place(
        title='P1',
        capacity=1,
        price=10.0,
        latitude=1.0,
        longitude=2.0,
        host=h,
        description='Desc'
    )
    assert isinstance(p, Place) and p.capacity == 1 and p.price == 10.0
    b = Booking(user=u, place=p, guest_count=1, checkin_date=datetime.now(), night_count=2)
    assert isinstance(b, Booking) and b.guest_count == 1
    r = Review(booking=b, text='x', rating=4)
    assert isinstance(r, Review) and r.rating == 4
