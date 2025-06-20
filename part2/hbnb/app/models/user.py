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
        __is_admin (bool): Admin status flag.
        __bookings (list): List of Booking instances made by the user.
    """

    def __init__(self, first_name, last_name, email, is_admin=False, **kwargs):
        """
        Initialize a new User instance.

        Validates types and lengths for names and email format, sets admin flag,
        and initializes an empty bookings list.

        Args:
            first_name (str): User's first name, max length 50.
            last_name (str): User's last name, max length 50.
            email (str): User's email address in valid format.
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

        # --------- Init is_admin --------- #
        if not isinstance(is_admin, bool):
            raise TypeError("Is Admin must be of type bool")
        self.__is_admin = is_admin

        # --------- Init bookings --------- #
        self.__bookings = []

    # ----------------------- first_name ----------------------- #
    @property
    def first_name(self):
        """
        Get the user's first name.

        Returns:
            str: First name.
        """
        return self.__first_name

    @first_name.setter
    def first_name(self, first_name):
        """
        Update the user's first name with validation.

        Args:
            first_name (str): New first name, max length 50.

        Raises:
            TypeError: If first_name is not a string.
            ValueError: If first_name length exceeds 50.
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

        Returns:
            str: Last name.
        """
        return self.__last_name

    @last_name.setter
    def last_name(self, last_name):
        """
        Update the user's last name with validation.

        Args:
            last_name (str): New last name, max length 50.

        Raises:
            TypeError: If last_name is not a string.
            ValueError: If last_name length exceeds 50.
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

        Returns:
            str: Email.
        """
        return self.__email

    @email.setter
    def email(self, email):
        """
        Update the user's email with validation.

        Args:
            email (str): New email in valid format.

        Raises:
            TypeError: If email is not a string.
            ValueError: If email format is invalid.
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

        Returns:
            bool: True if user is admin, else False.
        """
        return self.__is_admin

    @is_admin.setter
    def is_admin(self, admin):
        """
        Update the admin status with validation.

        Args:
            admin (bool): New admin status.

        Raises:
            TypeError: If admin is not a boolean.
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

        Returns:
            list: List of Booking instances.
        """
        return self.__bookings

    # -------------------------- methods -------------------------- #
    def add_booking(self, booking):
        """
        Associate a Booking with this user.

        Args:
            booking (Booking): Booking instance to add.

        Raises:
            TypeError: If booking is not a Booking instance.
        """
        from .booking import Booking

        if not isinstance(booking, Booking):
            raise TypeError("booking must be a Booking instance")
        self.__bookings.append(booking)

    def leave_review(self, booking, text, rating):
        """
        Leave a review for a completed booking.

        Validates that the user made the booking and that no review exists yet,
        then creates a Review instance.

        Args:
            booking (Booking): Booking instance to review.
            text (str): Review text.
            rating (int): Rating between 1 and 5.

        Raises:
            Exception: If booking was not made by the user or review already exists.
        """
        from .review import Review

        if booking not in self.__bookings:
            raise Exception("User cannot review a booking they did not make.")
        if getattr(booking, "review", None):
            raise Exception("Booking already has a review.")
        Review(booking, text, rating)
