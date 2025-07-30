from datetime import datetime, timedelta, date
from flask import abort
from dateutil.parser import parse

from app.persistence import SQLAlchemyRepository
from app.models.user import User
from app.models.host import Host
from app.models.place import Place
from app.models.amenity import Amenity
from app.models.booking import Booking
from app.models.review import Review
from app.database import db


class HBnBFacade:
    def __init__(self):
        self.user_repo = SQLAlchemyRepository(User)
        self.host_repo = SQLAlchemyRepository(Host)
        self.place_repo = SQLAlchemyRepository(Place)
        self.amenity_repo = SQLAlchemyRepository(Amenity)
        self.booking_repo = SQLAlchemyRepository(Booking)
        self.review_repo = SQLAlchemyRepository(Review)

    # ---- Users ----
    def create_user(self, data):
        user = User(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            is_admin=data.get("is_admin", False),
        )
        user.set_password(data["password"])
        self.user_repo.add(user)
        return user

    def get_user(self, uid):
        return self.user_repo.get(uid)

    def list_users(self):
        return self.user_repo.get_all() + self.host_repo.get_all()

    def get_user_by_email(self, email):
        return next(
            (u for u in self.list_users() if u.email.lower() == email.lower()), None
        )

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
        return len(self.list_users()) == 0

    # ---- Hosts ----
    def create_host(self, data):
        host = Host(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            is_admin=data.get("is_admin", False),
        )
        host.set_password(data["password"])
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
        seen = set()
        return [
            p
            for p in self.list_places()
            if getattr(p, "host", None)
            and p.host.id == hid
            and not (p.id in seen or seen.add(p.id))
        ]

    def get_host_by_email(self, email):
        return next(
            (h for h in self.list_hosts() if h.email.lower() == email.lower()), None
        )

    # ---- Places ----
    def create_place(self, data):
        lat = float(data.pop("latitude", 0.0) or 0.0)
        lon = float(data.pop("longitude", 0.0) or 0.0)
        host_id = data.pop("host_id", None)
        if not host_id:
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
    def create_booking(self, data):
        user = self.get_user(data["user_id"])
        place = self.get_place(data["place_id"])

        start = data.get("start_date")
        if start is None:
            raise TypeError("start_date is required and cannot be None")
        start = start if isinstance(start, date) else parse(str(start)).date()

        end = data.get("end_date")
        if end is None:
            raise TypeError("end_date is required and cannot be None")
        end = end if isinstance(end, date) else parse(str(end)).date()

        for existing in self.list_bookings():
            if (
                existing.place
                and existing.place.id == place.id
                and existing.status not in ["declined", "cancelled"]
            ):
                if start < existing.end_date and end > existing.start_date:
                    abort(
                        400,
                        f"Place {place.id} is already booked from {existing.start_date} to {existing.end_date}",
                    )

        days = (end - start).days
        total_price = place.price * days

        booking = Booking(
            user=user,
            place=place,
            guest_count=data["guest_count"],
            start_date=start,
            end_date=end,
            total_price=total_price,
            status="pending",
        )
        self.booking_repo.add(booking)

        return booking

    def update_booking(self, bid, data):
        booking = self.get_booking(bid)
        if not booking:
            return None

        if "start_date" in data:
            start = data["start_date"]
            if start is None:
                raise TypeError("start_date cannot be None")
            data["start_date"] = (
                start if isinstance(start, date) else parse(str(start)).date()
            )

        if "end_date" in data:
            end = data["end_date"]
            if end is None:
                raise TypeError("end_date cannot be None")
            data["end_date"] = end if isinstance(end, date) else parse(str(end)).date()

        for k, v in data.items():
            setattr(booking, k, v)
        return booking

    def delete_booking(self, bid):
        self.booking_repo.delete(bid)

    def get_booking(self, bid):
        return self.booking_repo.get(bid)

    def list_bookings(self):
        return self.booking_repo.get_all()

    def get_user_bookings(self, uid):
        user = self.get_user(uid)
        return [b for b in self.list_bookings() if b.user.id == uid] if user else None

    def list_bookings_for_place(self, pid):
        place = self.get_place(pid)
        return [b for b in self.list_bookings() if b.place.id == pid] if place else None


    def notify_host_booking_cancelled(self, booking):
        """
        Notify the host when a booking is cancelled.
        You can log, send an email, or trigger any other type of notification.
        """
        host = booking.place.host
        # Example: Notify the host by sending an email, logging, etc.
        print(f"Booking {booking.id} has been cancelled. Notify host {host.first_name} {host.last_name}.")

        # You can send an email to the host or create a notification if needed
        # For example, you can use an email service or a task queue here to handle notifications.


    def notify_guest_booking_status(self, booking, status):
        """
        Notify the guest when the status of their booking changes (accepted, declined, etc.)
        """
        guest = booking.user  # The user who made the booking
        place = booking.place
        subject = f"Your booking for {place.title} has been {status}"
        body = f"Dear {guest.first_name},\n\nYour booking for {place.title} from {booking.start_date} to {booking.end_date} has been {status}."

        # For demonstration, we print it. Replace with actual notification logic.
        print(f"Notify guest {guest.first_name} {guest.last_name}: {subject}\n{body}")

        # If you're using email, you can integrate Flask-Mail or another email service here
        # Example:
        # send_email(guest.email, subject, body)


    # ---- Reviews ----
    def create_review(self, data):
        booking_obj = self.get_booking(data.pop("booking_id"))
        if not booking_obj:
            raise ValueError("Booking not found")
        if booking_obj.review:
            raise ValueError("This booking already has a review")

        review_obj = booking_obj.user.leave_review(
            booking_obj, data.get("text"), data.get("rating")
        )
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

   
   

facade = HBnBFacade()
