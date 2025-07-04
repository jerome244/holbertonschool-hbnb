"""
user.py: Defines the User model with name, email, admin flag, and booking management.

This module provides the User class, inheriting from BaseModel, enforcing type and
value constraints on first name, last name, email, and is_admin flag, and managing
associated bookings and review creation.
"""

from .base import BaseModel
import re
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .booking import Booking


class User(BaseModel):
    """
    Model representing an application user.

    Attributes:
        __first_name (str): User's first name.
        __last_name (str): User's last name.
        __email (str): User's email address.
        __password (str): User's password hash.
        __is_admin (bool): Admin status flag.
        __bookings (list): List of Booking instances made by the user.
    """

    def __init__(self, first_name, last_name, email, password, is_admin=False, **kwargs):
        """
        Initialize a new User instance.

        Validates types and lengths for names, email format, and password, sets admin flag,
        and initializes an empty bookings list.

        Args:
            first_name (str): User's first name, max length 50.
            last_name (str): User's last name, max length 50.
            email (str): User's email address in valid format.
            password (str): Plaintext password, min length 8.
            is_admin (bool, optional): Admin privilege flag. Defaults to False.
            **kwargs: Additional keyword args passed to BaseModel.
        """
        super().__init__(**kwargs)

        # --------- Init first_name --------- #
        if not isinstance(first_name, str):
            raise TypeError("First name must be of type str")
        if len(first_name) > 50:
            raise ValueError("First name length must not exceed 50 characters")
        self.__first_name = first_name

        # --------- Init last_name --------- #
        if not isinstance(last_name, str):
            raise TypeError("Last name must be of type str")
        if len(last_name) > 50:
            raise ValueError("Last name length must not exceed 50 characters")
        self.__last_name = last_name

        # --------- Init email --------- #
        email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not isinstance(email, str):
            raise TypeError("Email must be of type str")
        if not email_regex.match(email):
            raise ValueError("Email must have valid mail address format")
        self.__email = email

        # --------- Init password (hashed) --------- #
        self.hash_password(password)

        # --------- Init is_admin --------- #
        if not isinstance(is_admin, bool):
            raise TypeError("Is Admin must be of type bool")
        self.__is_admin = is_admin

        # --------- Init bookings --------- #
        self.__bookings = []

    def hash_password(self, password):
        """
        Hashes the password before storing it.
        """
        from app import bcrypt
        if not isinstance(password, str):
            raise TypeError("Password must be a string")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.__password = pw_hash
        self.update_date = datetime.now()

    def verify_password(self, password):
        """
        Verifies if the provided password matches the hashed password.
        """
        from app import bcrypt
        return bcrypt.check_password_hash(self.__password, password)

    @property
    def password(self):
        """
        Prevent direct access to the password hash.
        """
        raise AttributeError("Password hash is write-only.")

    @password.setter
    def password(self, pw_hash):
        """
        Store a pre-hashed password string.
        """
        self.hash_password(pw_hash)

    # ----------------------- first_name ----------------------- #
    @property
    def first_name(self):
        """
        Get the user's first name.
        """
        return self.__first_name

    @first_name.setter
    def first_name(self, first_name):
        """
        Update the user's first name with validation.
        """
        if not isinstance(first_name, str):
            raise TypeError("First name must be of type str")
        if len(first_name) > 50:
            raise ValueError("First name length must not exceed 50 characters")
        self.__first_name = first_name
        self.update_date = datetime.now()

    # ------------------------ last_name ------------------------ #
    @property
    def last_name(self):
        """
        Get the user's last name.
        """
        return self.__last_name

    @last_name.setter
    def last_name(self, last_name):
        """
        Update the user's last name with validation.
        """
        if not isinstance(last_name, str):
            raise TypeError("Last name must be of type str")
        if len(last_name) > 50:
            raise ValueError("Last name length must not exceed 50 characters")
        self.__last_name = last_name
        self.update_date = datetime.now()

    # -------------------------- email -------------------------- #
    @property
    def email(self):
        """
        Get the user's email address.
        """
        return self.__email

    @email.setter
    def email(self, email):
        """
        Update the user's email with validation.
        """
        email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not isinstance(email, str):
            raise TypeError("Email must be of type str")
        if not email_regex.match(email):
            raise ValueError("Email must have valid mail address format")
        self.__email = email
        self.update_date = datetime.now()

    # ------------------------ is_admin ------------------------ #
    @property
    def is_admin(self):
        """
        Get the admin status flag.
        """
        return self.__is_admin

    @is_admin.setter
    def is_admin(self, admin):
        """
        Update the admin status with validation.
        """
        if not isinstance(admin, bool):
            raise TypeError("Is Admin must be of type bool")
        self.__is_admin = admin
        self.update_date = datetime.now()

    # ------------------------ bookings ------------------------ #
    @property
    def bookings(self):
        """
        Get all bookings made by the user.
        """
        return self.__bookings

    def add_booking(self, booking):
        """
        Associate a Booking with this user.
        """
        from .booking import Booking

        if not isinstance(booking, Booking):
            raise TypeError("booking must be a Booking instance")
        self.__bookings.append(booking)

    def leave_review(self, booking, text, rating):
        """
        Leave a review for a completed booking.
        """
        from .review import Review

        if booking not in self.__bookings:
            raise Exception("User cannot review a booking they did not make.")
        if getattr(booking, "review", None):
            raise Exception("Booking already has a review.")
        Review(booking, text, rating)
