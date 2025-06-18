from datetime import datetime
from app.persistence.repository import InMemoryRepository
from app.models.user     import User
from app.models.host     import Host
from app.models.place    import Place
from app.models.amenity  import Amenity
from app.models.booking  import Booking
from app.models.review   import Review

class HBnBFacade:
    def __init__(self):
        self.user_repo    = InMemoryRepository()
        self.host_repo    = InMemoryRepository()
        self.place_repo   = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()
        self.booking_repo = InMemoryRepository()
        self.review_repo  = InMemoryRepository()

    # ---- Users ----
    def create_user(self, data):
        user = User(**data)
        self.user_repo.add(user)
        return user

    def get_user(self, uid):    return self.user_repo.get(uid)
    def list_users(self):       return self.user_repo.get_all()
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

    def get_host(self, hid):    return self.host_repo.get(hid)
    def list_hosts(self):       return self.host_repo.get_all()
    def update_host(self, hid, data):
        host = self.get_host(hid)
        if not host:
            return None
        for k, v in data.items():
            setattr(host, k, v)
        return host
    def delete_host(self, hid):
        self.host_repo.delete(hid)

    # ---- Places ----
    def create_place(self, data):
        host = self.get_host(data.pop('host_id'))
        place = Place(host=host, **data)
        self.place_repo.add(place)
        return place

    def get_place(self, pid):   return self.place_repo.get(pid)
    def list_places(self):      return self.place_repo.get_all()
    def update_place(self, pid, data):
        place = self.get_place(pid)
        if not place:
            return None
        for k, v in data.items():
            setattr(place, k, v)
        return place
    def delete_place(self, pid):
        self.place_repo.delete(pid)

    # ---- Amenities ----
    def create_amenity(self, data):
        amenity = Amenity(**data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, aid):    return self.amenity_repo.get(aid)
    def list_amenities(self):       return self.amenity_repo.get_all()
    def delete_amenity(self, aid):  self.amenity_repo.delete(aid)

    # ---- Bookings ----
    def create_booking(self, data):
        # Extract required fields
        guest_count   = data.pop('guest_count')
        checkin_input = data.pop('checkin_date')
        night_count   = data.pop('night_count')

        # Parse check-in date
        if isinstance(checkin_input, str):
            try:
                iso_str = checkin_input
                if iso_str.endswith('Z'):
                    iso_str = iso_str[:-1] + '+00:00'
                checkin_date = datetime.fromisoformat(iso_str)
            except (ValueError, TypeError):
                raise TypeError("Checkin_date must be datetime format")
        elif isinstance(checkin_input, datetime):
            checkin_date = checkin_input
        else:
            raise TypeError("Checkin_date must be datetime format")

        # Lookup relationships
        user  = self.get_user(data.pop('user_id'))
        place = self.get_place(data.pop('place_id'))

        # Construct and persist
        booking_obj = Booking(
            guest_count,
            checkin_date,
            night_count,
            place,
            user,
            **data
        )
        self.booking_repo.add(booking_obj)
        return booking_obj

    def get_booking(self, bid):    return self.booking_repo.get(bid)
    def list_bookings(self):       return self.booking_repo.get_all()
    def update_booking(self, bid, data):
        booking_obj = self.get_booking(bid)
        if not booking_obj:
            return None
        for k, v in data.items():
            setattr(booking_obj, k, v)
        return booking_obj
    def delete_booking(self, bid): self.booking_repo.delete(bid)

    # ---- Reviews ----
    def create_review(self, data):
        booking_id = data.pop('booking_id')
        rating     = data.pop('rating', None)
        text       = data.pop('text', None)

        booking_obj = self.get_booking(booking_id)
        if not booking_obj:
            raise ValueError("Booking not found")

        # Delegate to model
        booking_obj.user.leave_review(booking_obj, rating, text)
        review_obj = booking_obj.review

        # Persist review
        self.review_repo.add(review_obj)
        return review_obj

    def get_review(self, rid):     return self.review_repo.get(rid)
    def list_reviews(self):        return self.review_repo.get_all()
    def update_review(self, rid, data):
        review_obj = self.get_review(rid)
        if not review_obj:
            return None
        for k, v in data.items():
            setattr(review_obj, k, v)
        return review_obj
    def delete_review(self, rid):  self.review_repo.delete(rid)
