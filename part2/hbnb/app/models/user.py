from base import BaseModel
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from booking import Booking


class User(BaseModel):
    def __init__(self, first_name, last_name, email, phone, password, **kwargs):
        super().__init__(**kwargs)
        self.__first_name = first_name
        self.__last_name = last_name
        self.__email = email
        self.__phone = phone
        self.__password = password
        self.__bookings = []

    # ----------------------- First name ------------------------ #
    @property
    def first_name(self):
        return self.__first_name

    @first_name.setter
    def first_name(self, first_name):
        if not isinstance(first_name, str):
            raise TypeError("First name must be of type str")
        if not (2 <= len(first_name) <= 16):
            raise ValueError("First name length must be between 2 and 16 characters")
        self.__first_name = first_name

    # ------------------------ Last name ------------------------ #
    @property
    def last_name(self):
        return self.__last_name

    @last_name.setter
    def last_name(self, last_name):
        if not isinstance(last_name, str):
            raise TypeError("Last name must be of type str")
        if not (2 <= len(last_name) <= 16):
            raise ValueError("Last name length must be between 2 and 16 characters")
        self.__last_name = last_name

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

    # -------------------------- Phone -------------------------- #
    @property
    def phone(self):
        return self.__phone

    @phone.setter
    def phone(self, phone):
        phone_regex = re.compile(r'^\+\d{1,3}[-\s]?\d{1,4}([-\s]?\d{2,5}){1,4}$')
        if not isinstance(phone, str):
            raise TypeError("Phone number must be of type str")
        if not phone_regex.match(phone):
            raise ValueError("Phone number must have valid format")
        self.__phone = phone

    # ----------------------- First name ------------------------ #

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, password):
        if not isinstance(password, str):
            raise TypeError("Password must be of type str")
        if not (2 <= len(password) <= 16):
            raise ValueError("Password length must be between 8 and 32 characters")
        self.__password = password

    # -------------------------- Methods -------------------------- #
    def booking(self, booking):
        from booking import Booking
        if not isinstance(booking, Booking):
            raise TypeError("booking must be a Booking instance")
        self.__bookings.append(booking)
