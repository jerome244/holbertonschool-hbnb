from .base import BaseModel
import re
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .booking import Booking


class User(BaseModel):
    def __init__(self, first_name, last_name, email, is_admin=False, **kwargs):
        super().__init__(**kwargs)

        # --------- Init first_name --------- #
        if not isinstance(first_name, str):
            raise TypeError("First name must be of type str")
        if len(first_name) > 50:
            raise ValueError("First name length must not exceed 50 characters")
        else:
            self.__first_name = first_name

        # --------- Init last_name --------- #
        if not isinstance(last_name, str):
            raise TypeError("Last name must be of type str")
        if len(last_name) > 50:
            raise ValueError("Last name length must not exceed 50 characters")
        else:
            self.__last_name = last_name

        # --------- Init email --------- #
        email_regex = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        if not isinstance(email, str):
            raise TypeError("Email must be of type str")
        if not email_regex.match(email):
            raise ValueError("Email must have valid mail address format")
        else:
            self.email = email

        # --------- Init is_admin --------- #
        if not isinstance(is_admin, bool):
            raise TypeError("Is Admin must be of type bool")
        else:
            self.__is_admin = is_admin

        self.__bookings = []

    # ----------------------- First name ------------------------ #
    @property
    def first_name(self):
        return self.__first_name

    @first_name.setter
    def first_name(self, first_name):
        if not isinstance(first_name, str):
            raise TypeError("First name must be of type str")
        if len(first_name) > 50:
            raise ValueError("First name length must not exceed 50 characters")
        self.__first_name = first_name
        self.update_date = datetime.now()

    # ------------------------ Last name ------------------------ #
    @property
    def last_name(self):
        return self.__last_name

    @last_name.setter
    def last_name(self, last_name):
        if not isinstance(last_name, str):
            raise TypeError("Last name must be of type str")
        if len(last_name) > 50:
            raise ValueError("Last name length must not exceed 50 characters")
        self.__last_name = last_name
        self.update_date = datetime.now()

    # -------------------------- Email -------------------------- #
    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, email):
        email_regex = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        if not isinstance(email, str):
            raise TypeError("Email must be of type str")
        if not email_regex.match(email):
            raise ValueError("Email must have valid mail address format")
        self.__email = email
        self.update_date = datetime.now()

    # ------------------------ Is Admin ------------------------ #

    @property
    def is_admin(self):
        return self.__is_admin

    @is_admin.setter
    def is_admin(self, admin):
        if not isinstance(admin, bool):
            raise TypeError("Is Admin must be of type bool")
        self.is_admin = admin
        self.update_date = datetime.now()

    # ------------------------ Bookings ------------------------ #

    @property
    def bookings(self):
        return self.__bookings

    # -------------------------- Methods -------------------------- #

    def add_booking(self, booking):
        from .booking import Booking
        if not isinstance(booking, Booking):
            raise TypeError("booking must be a Booking instance")
        self.__bookings.append(booking)

    def leave_review(self, booking, rating, comment):
        from review import Review
        if booking not in self.__bookings:
            raise Exception("User cannot review a booking they did not make.")
        if booking.review:
            raise Exception("Booking already has a review.")
        Review(booking, rating, comment)
