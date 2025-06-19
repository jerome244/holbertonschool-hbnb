<<<<<<< HEAD
from app.persistence.repository import InMemoryRepository
=======
from datetime import datetime, timedelta
from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.host import Host
from app.models.place import Place
from app.models.amenity import Amenity
from app.models.booking import Booking
from app.models.review import Review

>>>>>>> devJerome

class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()
<<<<<<< HEAD
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    # Placeholder method for creating a user
    def create_user(self, user_data):
        # Logic will be implemented in later tasks
        pass

    # Placeholder method for fetching a place by ID
    def get_place(self, place_id):
        # Logic will be implemented in later tasks
        pass
=======
        self.host_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()
        self.booking_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()

    # ---- Users ----
    def create_user(self, data):
        user = User(**data)
        self.user_repo.add(user)
        return user

    def get_user(self, uid):
        return self.user_repo.get(uid)

    def list_users(self):
        return self.user_repo.get_all()

    def update_user(self, uid, data):
        user = self.get_user(uid)
        if not user:
            return None
        for k, v in data.items():
            setattr(user, k, v)
        return user

    def delete_user(self, uid):
        self.user_repo.delete(uid)

    # ---- Hosts ----
    def create_host(self, data):
        host = Host(**data)
        self.host_repo.add(host)
        return host

    def get_host(self, hid):
        return self.host_repo.get(hid)

    def list_hosts(self):
        return self.host_repo.get_all()

    def update_host(self, hid, data):
        host = self.get_host(hid)
        if not host:
            return None
        for k, v in data.items():
            setattr(host, k, v)
        return host

    def delete_host(self, hid):
        self.host_repo.delete(hid)

    def get_host_owned_places(self, hid):
        host = self.get_host(hid)
        if not host:
            return None
        owned = [
            p
            for p in self.list_places()
            if getattr(p, "host", None) and p.host.id == hid
        ]
        seen = set()
        unique = []
        for p in owned:
            if p.id not in seen:
                seen.add(p.id)
                unique.append(p)
        return unique

    # ---- Places ----
    def create_place(self, data):
        lat = float(data.pop("latitude", 0.0) or 0.0)
        lon = float(data.pop("longitude", 0.0) or 0.0)
        host_id = data.pop("host_id", None)
        if host_id is None:
            raise ValueError("Missing required field: host_id")
        host = self.get_host(host_id)
        if not host:
            return None

        title = data.get("title")
        for existing in self.list_places():
            if (
                getattr(existing, "host", None)
                and existing.host.id == host_id
                and existing.title == title
            ):
                return None

        place = Place(host=host, latitude=lat, longitude=lon, **data)
        self.place_repo.add(place)
        return place

    def get_place(self, pid):
        return self.place_repo.get(pid)

    def list_places(self):
        return self.place_repo.get_all()

    def update_place(self, pid, data):
        place = self.get_place(pid)
        if not place:
            return None
        for k, v in data.items():
            setattr(place, k, v)
        return place

    def delete_place(self, pid):
        place = self.get_place(pid)
        if not place:
            return None
        self.place_repo.delete(pid)
        return place

    # ---- Amenities ----
    def create_amenity(self, data):
        amenity = Amenity(**data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, aid):
        return self.amenity_repo.get(aid)

    def list_amenities(self):
        return self.amenity_repo.get_all()

    def delete_amenity(self, aid):
        self.amenity_repo.delete(aid)

    # ---- Bookings ----
    def create_booking(self, data):
        user = self.get_user(data["user_id"])
        place = self.get_place(data["place_id"])

        checkin = data["checkin_date"]
        if isinstance(checkin, str):
            checkin = datetime.fromisoformat(checkin)

        booking = Booking(
            user=user,
            place=place,
            guest_count=data["guest_count"],
            checkin_date=checkin,
            night_count=data["night_count"],
        )
        self.booking_repo.add(booking)
        return booking

    def get_booking(self, bid):
        return self.booking_repo.get(bid)

    def list_bookings(self):
        return self.booking_repo.get_all()

    def delete_booking(self, bid):
        self.booking_repo.delete(bid)

    def get_user_bookings(self, uid):
        user = self.get_user(uid)
        if not user:
            return None
        return [b for b in self.list_bookings() if b.user.id == uid]

    # ---- Reviews ----
    def create_review(self, data):
        booking_obj = self.get_booking(data.pop("booking_id"))
        if not booking_obj:
            raise ValueError("Booking not found")
        # swap text & rating so Review.__init__(self, booking, text, rating) receives correctly
        booking_obj.user.leave_review(
            booking_obj,
            data.get("text"),  # becomes the review text
            data.get("rating"),  # becomes the numeric rating
        )
        review_obj = booking_obj.review
        self.review_repo.add(review_obj)
        return review_obj

    def get_review(self, rid):
        return self.review_repo.get(rid)

    def list_reviews(self):
        return self.review_repo.get_all()

    def delete_review(self, rid):
        self.review_repo.delete(rid)
>>>>>>> devJerome
