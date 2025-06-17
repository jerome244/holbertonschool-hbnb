from .base import BaseModel
import re
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from booking import Booking

EMAIL_REGEX = r'^[^@]+@[^@]+\.[^@]+$'


class User(BaseModel):
    """
    User model:
      - id, created_at, updated_at inherited from BaseModel
      - first_name, last_name, email, is_admin with validation
      - bookings relationship
    """
    def __init__(self, first_name, last_name, email, is_admin=False, **kwargs):
        super().__init__(**kwargs)
        # use setters for validation
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        # initialize empty bookings list
        self.__bookings = []

    # --------------- first_name ---------------
    @property
    def first_name(self):
        return self.__first_name

    @first_name.setter
    def first_name(self, value):
        if not isinstance(value, str):
            raise TypeError("first_name must be a string")
        self.__first_name = value

    # --------------- last_name ---------------
    @property
    def last_name(self):
        return self.__last_name

    @last_name.setter
    def last_name(self, value):
        if not isinstance(value, str):
            raise TypeError("last_name must be a string")
        self.__last_name = value

    # --------------- email ---------------
    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        if not isinstance(value, str):
            raise TypeError("email must be a string")
        if not re.match(EMAIL_REGEX, value):
            raise ValueError("email must be a valid email address")
        self.__email = value

    # --------------- is_admin ---------------
    @property
    def is_admin(self):
        return self.__is_admin

    @is_admin.setter
    def is_admin(self, value):
        if not isinstance(value, bool):
            raise TypeError("is_admin must be a boolean")
        self.__is_admin = value

    # ---------------- Bookings ----------------
    @property
    def bookings(self):
        """Return list of Booking instances linked to this user."""
        return self.__bookings

    def add_booking(self, booking):
        from booking import Booking
        if not isinstance(booking, Booking):
            raise TypeError("booking must be a Booking instance")
        self.__bookings.append(booking)
