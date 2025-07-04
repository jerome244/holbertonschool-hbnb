
"""
facade.py: Provides a unified interface (facade) to application repositories and models.

The HBnBFacade class wraps repository operations for users, hosts, places, amenities,
bookings, and reviews, coordinating data persistence and business logic.
"""

from datetime import datetime, timedelta
from flask import abort
from dateutil.parser import parse
from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.host import Host
from app.models.place import Place
from app.models.amenity import Amenity
from app.models.booking import Booking
from app.models.review import Review


class HBnBFacade:
    """
    Facade for the HBnB application, managing repository interactions.

    Attributes:
        user_repo: Repository for User objects.
        host_repo: Repository for Host objects.
        place_repo: Repository for Place objects.
        amenity_repo: Repository for Amenity objects.
        booking_repo: Repository for Booking objects.
        review_repo: Repository for Review objects.
    """

    def __init__(self):
        self.user_repo = InMemoryRepository()
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
        users_list = self.user_repo.get_all() + self.host_repo.get_all()
        return users_list

    def get_user_by_email(self, email: str):
        for u in self.list_users():
            if u.email.lower() == email.lower():
                return u
        return None

    def update_user(self, uid, data):
        user = self.get_user(uid)
        if not user:
            return None
        for k, v in data.items():
            setattr(user, k, v)
        return user

    def delete_user(self, uid):
        self.user_repo.delete(uid)

    def is_first_user(self):
        users_list = self.user_repo.get_all() + self.host_repo.get_all()
        is_first = len(users_list) == 0
        return is_first

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
        owned = [p for p in self.list_places() if getattr(p, "host", None) and p.host.id == hid]
        seen = set()
        unique = []
        for p in owned:
            if p.id not in seen:
                seen.add(p.id)
                unique.append(p)
        return unique

    def get_host_by_email(self, email: str):
        for h in self.list_hosts():
            if h.email.lower() == email.lower():
                return h
        return None

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
            if getattr(existing, "host", None) and existing.host.id == host_id and existing.title == title:
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

    def update_amenity(self, aid, data):
        amenity = self.get_amenity(aid)
        if not amenity:
            return None
        for k, v in data.items():
            setattr(amenity, k, v)
        return amenity

    def delete_amenity(self, aid):
        self.amenity_repo.delete(aid)

    # ---- Bookings ----

    def get_booking(self, bid):
        return self.booking_repo.get(bid)

    def list_bookings(self):
        return self.booking_repo.get_all()

    def create_booking(self, data):
        user = self.get_user(data["user_id"])
        place = self.get_place(data["place_id"])

        # Parse checkin_date
        checkin = data.get("checkin_date")
        if isinstance(checkin, str):
            try:
                checkin = datetime.fromisoformat(checkin)
            except ValueError:
                try:
                    checkin = parse(checkin)
                except Exception:
                    raise TypeError("checkin_date must be a valid ISO or recognizable datetime string")
        if not isinstance(checkin, datetime):
            raise TypeError("checkin_date must be a datetime object or valid ISO string")

        data["checkin_date"] = checkin
        # Compute end date
        end_date = checkin + timedelta(days=data.get("night_count", 0))

        # Enforce no overlap
        for existing in self.list_bookings():
            if existing.place.id != place.id:
                continue
            existing_start = existing.checkin_date
            existing_end = existing_start + timedelta(days=existing.night_count)
            if checkin < existing_end and end_date > existing_start:
                abort(400, f"Place {place.id} is already booked from {existing_start.date()} to {existing_end.date()}")

        # No conflict → create booking
        booking = Booking(
            user=user,
            place=place,
            guest_count=data["guest_count"],
            checkin_date=checkin,
            night_count=data["night_count"],
        )
        self.booking_repo.add(booking)
        return booking

    def update_booking(self, bid, data):
        booking = self.get_booking(bid)
        if not booking:
            return None

        checkin = data.get("checkin_date")
        if checkin:
            if isinstance(checkin, str):
                try:
                    checkin = datetime.fromisoformat(checkin)
                except ValueError:
                    try:
                        checkin = parse(checkin)
                    except Exception:
                        raise TypeError("checkin_date must be a valid ISO or recognizable datetime string")
            if not isinstance(checkin, datetime):
                raise TypeError("checkin_date must be a datetime object or valid ISO string")
            data["checkin_date"] = checkin

        for k, v in data.items():
            setattr(booking, k, v)
        return booking

    def delete_booking(self, bid):
        self.booking_repo.delete(bid)

    def get_user_bookings(self, uid):
        user = self.get_user(uid)
        if not user:
            return None
        return [b for b in self.list_bookings() if b.user.id == uid]

    # Alias for API compatibility
    def get_all_bookings(self):
        return self.list_bookings()

    # ---- Reviews ----

    def create_review(self, data):
        booking_obj = self.get_booking(data.pop("booking_id"))
        if not booking_obj:
            raise ValueError("Booking not found")
        booking_obj.user.leave_review(booking_obj, data.get("text"), data.get("rating"))
        review_obj = booking_obj.review
        self.review_repo.add(review_obj)
        return review_obj

    def get_review(self, rid):
        return self.review_repo.get(rid)

    def list_reviews(self):
        return self.review_repo.get_all()

    def update_review(self, rid, data):
        review = self.get_review(rid)
        if not review:
            return None
        for k, v in data.items():
            setattr(review, k, v)
        return review

    def delete_review(self, rid):
        self.review_repo.delete(rid)


# Global facade instance
facade = HBnBFacade()
