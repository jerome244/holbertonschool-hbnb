"""
facade.py: Provides a unified interface (facade) to application repositories and models.

The HBnBFacade class wraps repository operations for users, hosts, places, amenities,
bookings, and reviews, coordinating data persistence and business logic.
"""

from datetime import datetime, timedelta
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
        """
        Initialize all in-memory repositories for each model.
        """
        self.user_repo = InMemoryRepository()
        self.host_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()
        self.booking_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()

    # ---- Users ----

    def create_user(self, data):
        """
        Create a new user and add to the repository.

        Args:
            data (dict): User attributes.
        Returns:
            User: The newly created User instance.
        """
        user = User(**data)
        self.user_repo.add(user)
        return user

    def get_user(self, uid):
        """
        Retrieve a User by ID.

        Args:
            uid (str): User unique identifier.
        Returns:
            User or None: The User instance if found.
        """
        return self.user_repo.get(uid)

    def list_users(self):
        """
        List all users in the repository.

        Returns:
            list: All User instances.
        """
        return self.user_repo.get_all()

    def update_user(self, uid, data):
        """
        Update attributes of an existing user.

        Args:
            uid (str): User unique identifier.
            data (dict): Fields to update.
        Returns:
            User or None: Updated User or None if not found.
        """
        user = self.get_user(uid)
        if not user:
            return None
        for k, v in data.items():
            setattr(user, k, v)
        return user

    def delete_user(self, uid):
        """
        Delete a user by ID.

        Args:
            uid (str): User unique identifier.
        """
        self.user_repo.delete(uid)

    # ---- Hosts ----

    def create_host(self, data):
        """
        Create a new host and add to the repository.

        Args:
            data (dict): Host attributes.
        Returns:
            Host: The newly created Host instance.
        """
        host = Host(**data)
        self.host_repo.add(host)
        return host

    def get_host(self, hid):
        """
        Retrieve a Host by ID.

        Args:
            hid (str): Host unique identifier.
        Returns:
            Host or None: The Host instance if found.
        """
        return self.host_repo.get(hid)

    def list_hosts(self):
        """
        List all hosts in the repository.

        Returns:
            list: All Host instances.
        """
        return self.host_repo.get_all()

    def update_host(self, hid, data):
        """
        Update attributes of an existing host.

        Args:
            hid (str): Host unique identifier.
            data (dict): Fields to update.
        Returns:
            Host or None: Updated Host or None if not found.
        """
        host = self.get_host(hid)
        if not host:
            return None
        for k, v in data.items():
            setattr(host, k, v)
        return host

    def delete_host(self, hid):
        """
        Delete a host by ID.

        Args:
            hid (str): Host unique identifier.
        """
        self.host_repo.delete(hid)

    def get_host_owned_places(self, hid):
        """
        List unique places owned by a given host.

        Args:
            hid (str): Host unique identifier.
        Returns:
            list or None: List of Place instances or None if host not found.
        """
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
        """
        Create a new place, ensuring valid host and unique title.

        Args:
            data (dict): Place attributes including host_id, latitude, longitude.
        Returns:
            Place or None: The newly created Place or None if invalid.
        """
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
        """
        Retrieve a Place by ID.

        Args:
            pid (str): Place unique identifier.
        Returns:
            Place or None: The Place instance if found.
        """
        return self.place_repo.get(pid)

    def list_places(self):
        """
        List all places in the repository.

        Returns:
            list: All Place instances.
        """
        return self.place_repo.get_all()

    def update_place(self, pid, data):
        """
        Update attributes of an existing place.

        Args:
            pid (str): Place unique identifier.
            data (dict): Fields to update.
        Returns:
            Place or None: Updated Place or None if not found.
        """
        place = self.get_place(pid)
        if not place:
            return None
        for k, v in data.items():
            setattr(place, k, v)
        return place

    def delete_place(self, pid):
        """
        Delete a place by ID.

        Args:
            pid (str): Place unique identifier.
        Returns:
            Place or None: Deleted Place or None if not found.
        """
        place = self.get_place(pid)
        if not place:
            return None
        self.place_repo.delete(pid)
        return place

    # ---- Amenities ----

    def create_amenity(self, data):
        """
        Create a new amenity and add to the repository.

        Args:
            data (dict): Amenity attributes.
        Returns:
            Amenity: The newly created Amenity instance.
        """
        amenity = Amenity(**data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, aid):
        """
        Retrieve an Amenity by ID.

        Args:
            aid (str): Amenity unique identifier.
        Returns:
            Amenity or None: The Amenity instance if found.
        """
        return self.amenity_repo.get(aid)

    def list_amenities(self):
        """
        List all amenities in the repository.

        Returns:
            list: All Amenity instances.
        """
        return self.amenity_repo.get_all()

    def delete_amenity(self, aid):
        """
        Delete an amenity by ID.

        Args:
            aid (str): Amenity unique identifier.
        """
        self.amenity_repo.delete(aid)

    # ---- Bookings ----

    def create_booking(self, data):
        """
        Create a new booking, parsing checkin date and validating user/place.

        Args:
            data (dict): Booking attributes including user_id, place_id, checkin_date, night_count.
        Returns:
            Booking: The newly created Booking instance.
        """
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
        """
        Retrieve a Booking by ID.

        Args:
            bid (str): Booking unique identifier.
        Returns:
            Booking or None: The Booking instance if found.
        """
        return self.booking_repo.get(bid)

    def list_bookings(self):
        """
        List all bookings in the repository.

        Returns:
            list: All Booking instances.
        """
        return self.booking_repo.get_all()

    def delete_booking(self, bid):
        """
        Delete a booking by ID.

        Args:
            bid (str): Booking unique identifier.
        """
        self.booking_repo.delete(bid)

    def get_user_bookings(self, uid):
        """
        List bookings for a specific user.

        Args:
            uid (str): User unique identifier.
        Returns:
            list or None: Booking list or None if user not found.
        """
        user = self.get_user(uid)
        if not user:
            return None
        return [b for b in self.list_bookings() if b.user.id == uid]

    # ---- Reviews ----

    def create_review(self, data):
        """
        Create a new review linked to a booking.

        Args:
            data (dict): Review attributes including booking_id, text, rating.
        Returns:
            Review: The newly created Review instance.
        """
        booking_obj = self.get_booking(data.pop("booking_id"))
        if not booking_obj:
            raise ValueError("Booking not found")
        booking_obj.user.leave_review(
            booking_obj,
            data.get("text"),
            data.get("rating"),
        )
        review_obj = booking_obj.review
        self.review_repo.add(review_obj)
        return review_obj

    def get_review(self, rid):
        """
        Retrieve a Review by ID.

        Args:
            rid (str): Review unique identifier.
        Returns:
            Review or None: The Review instance if found.
        """
        return self.review_repo.get(rid)

    def list_reviews(self):
        """
        List all reviews in the repository.

        Returns:
            list: All Review instances.
        """
        return self.review_repo.get_all()

    def delete_review(self, rid):
        """
        Delete a review by ID.

        Args:
            rid (str): Review unique identifier.
        """
        self.review_repo.delete(rid)
