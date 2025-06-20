import pytest
from datetime import datetime
from app.services.facade import HBnBFacade
from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.host import Host
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.booking import Booking
from app.models.review import Review


def test_inmemory_repository_crud():
    """
    InMemoryRepository supports add, get, get_all, and delete.
    """
    repo = InMemoryRepository()

    class Dummy:
        def __init__(self, id, value):
            self.id = id
            self.value = value

    d1 = Dummy("1", "a")
    d2 = Dummy("2", "b")
    repo.add(d1)
    repo.add(d2)
    assert repo.get("1") is d1
    assert {o.id for o in repo.get_all()} == {"1", "2"}
    repo.delete("1")
    assert repo.get("1") is None


@pytest.fixture
def facade():
    """
    Provide a fresh HBnBFacade for facade‐layer tests.
    """
    return HBnBFacade()


def test_facade_user_crud(facade):
    """
    Facade.create/get/update/list/delete Users end‐to‐end.
    """
    data = {"first_name": "A", "last_name": "B", "email": "a@b.com"}
    user = facade.create_user(data)
    uid = user.id
    assert facade.get_user(uid).email == data["email"]
    facade.update_user(uid, {"first_name": "Z"})
    assert facade.get_user(uid).first_name == "Z"
    assert any(u.id == uid for u in facade.list_users())
    facade.delete_user(uid)
    assert facade.get_user(uid) is None


def test_facade_host_crud(facade):
    """
    Facade CRUD for Hosts.
    """
    d = {"first_name": "H", "last_name": "O", "email": "h@o.com"}
    host = facade.create_host(d)
    hid = host.id
    assert facade.get_host(hid).email == d["email"]
    facade.delete_host(hid)
    assert facade.get_host(hid) is None


def test_facade_amenity_crud(facade):
    """
    Facade CRUD for Amenities.
    """
    a = facade.create_amenity({"name": "Wi-Fi"})
    aid = a.id
    assert facade.get_amenity(aid).name == "Wi-Fi"
    facade.delete_amenity(aid)
    assert facade.get_amenity(aid) is None


def test_facade_place_crud(facade):
    """
    Place CRUD via facade (requires valid description).
    """
    host = facade.create_host({"first_name": "X", "last_name": "Y", "email": "x@y.com"})
    data = {
        "host_id": host.id,
        "title": "MyPlace",
        "description": "Valid description",
        "latitude": 10.0,
        "longitude": 20.0,
        "capacity": 2,
        "price": 100.0,
    }
    place = facade.create_place(data)
    pid = place.id
    assert facade.get_place(pid).title == "MyPlace"
    facade.delete_place(pid)
    assert facade.get_place(pid) is None


def test_facade_booking_crud(facade):
    """
    Booking CRUD via facade.
    """
    u = facade.create_user({"first_name": "U", "last_name": "V", "email": "u@v.com"})
    h = facade.create_host({"first_name": "H", "last_name": "O", "email": "h@o.com"})
    p = facade.create_place(
        {
            "host_id": h.id,
            "title": "Place",
            "description": "Desc",
            "latitude": 0.0,
            "longitude": 0.0,
            "capacity": 1,
            "price": 50.0,
        }
    )
    b = facade.create_booking(
        {
            "user_id": u.id,
            "place_id": p.id,
            "guest_count": 1,
            "checkin_date": datetime.now().isoformat(),
            "night_count": 2,
        }
    )
    assert isinstance(facade.get_booking(b.id), Booking)
    facade.delete_booking(b.id)
    assert facade.get_booking(b.id) is None


def test_facade_review_crud(facade):
    """
    Review CRUD via facade.
    """
    u = facade.create_user({"first_name": "R", "last_name": "U", "email": "r@u.com"})
    h = facade.create_host({"first_name": "H", "last_name": "R", "email": "h@r.com"})
    p = facade.create_place(
        {
            "host_id": h.id,
            "title": "Place2",
            "description": "Desc2",
            "latitude": 0.0,
            "longitude": 0.0,
            "capacity": 1,
            "price": 75.0,
        }
    )
    bk = facade.create_booking(
        {
            "user_id": u.id,
            "place_id": p.id,
            "guest_count": 1,
            "checkin_date": datetime.now().isoformat(),
            "night_count": 1,
        }
    )
    rvw = facade.create_review({"booking_id": bk.id, "text": "Nice", "rating": 5})
    assert isinstance(facade.get_review(rvw.id), Review)
    facade.delete_review(rvw.id)
    assert facade.get_review(rvw.id) is None
