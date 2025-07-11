"""
booking.py: Defines the Booking model with validation, pricing, and review linkage.

This module provides the Booking class inheriting from BaseModel, enforcing
type and value constraints on guest count, dates, and linking to Place and User.
"""

from .base import BaseModel
from datetime import datetime, timedelta
from .user import User

# Check place for circular import
from .place import Place
from typing import TYPE_CHECKING


class Booking(BaseModel):
    """
    Model representing a booking of a place by a user.

    Attributes:
        __place (Place): The Place instance being booked.
        __guest_count (int): Number of guests for the booking.
        __checkin_date (datetime): The check-in date and time.
        __night_count (int): Number of nights to stay.
        __user (User): The User who made the booking.
        __total_price (float): Computed total price of the booking.
        __checkout_date (datetime): Computed check-out date and time.
        __rating: The rating given by the user (if any).
        __review: The Review instance linked to this booking (if any).
    """

    def __init__(self, guest_count, checkin_date, night_count, place, user, **kwargs):
        """
        Initialize a new Booking instance.

        Validates types and business rules, links booking to place and user,
        and computes pricing and checkout date.

        Args:
            guest_count (int): Number of guests.
            checkin_date (datetime): Check-in datetime; must be >= today.
            night_count (int): Number of nights; must be > 0.
            place (Place): Place being booked; must be a Place instance.
            user (User): User making the booking; must be a User instance.
            **kwargs: Additional keyword args passed to BaseModel.
        """
        super().__init__(**kwargs)

        # ---------- Init place ---------- #
        if not isinstance(place, Place):
            TypeError("Place must be of type Place")
        else:
            self.__place = place
            place.add_booking(self)

        # ---------- Init capacity ---------- #
        if guest_count > self.__place.capacity:
            raise ValueError(
                f"Number of guests exceeds {self.__place.title}'s capacity"
            )
        else:
            self.__guest_count = guest_count

        # ---------- Init checkin_date ---------- #
        if not isinstance(checkin_date, datetime):
            raise TypeError("Checkin_date must be datetime format")
        elif checkin_date.date() < datetime.today().date():
            raise ValueError("Checkin_date must be later than today")
        else:
            self.checkin_date = checkin_date

        # ---------- Init night_count ---------- #
        if not isinstance(night_count, int):
            raise TypeError("Number of nights stayed must be integer")
        if night_count <= 0:
            raise ValueError("Number of nights stayed must be greater than 0")
        else:
            self.__night_count = night_count

        # ---------- Init user ---------- #
        if not isinstance(user, User):
            TypeError("user must be of type User")
        else:
            self.__user = user

        self.__total_price = self.night_count * self.__place.price
        self.__checkout_date = self.checkin_date + timedelta(days=self.night_count)
        self.__rating = None
        self.__review = None

        user.add_booking(self)

    # ----------------------- Place ----------------------- #
    @property
    def place(self):
        """
        The Place instance associated with this booking.

        Returns:
            Place: The booked place.
        """
        return self.__place

    @place.setter
    def place(self, place):
        """
        Update the Place for this booking.

        Args:
            place (Place): New Place instance.

        Raises:
            TypeError: If place is not a Place instance.
        """
        if not isinstance(place, Place):
            TypeError("Place must be of type Place")
        self.__place = place
        self.update_date = datetime.now()

    # ----------------------- guest count ----------------------- #
    @property
    def guest_count(self):
        """
        Number of guests for this booking.

        Returns:
            int: Guest count.
        """
        return self.__guest_count

    @guest_count.setter
    def guest_count(self, guest_count):
        """
        Update the guest count for this booking.

        Args:
            guest_count (int): New guest count; must not exceed place capacity.

        Raises:
            ValueError: If guest_count > place.capacity.
        """
        if guest_count > self.__place.capacity:
            raise ValueError(
                f"Number of guests exceeds {self.__place.title}'s capacity"
            )
        self.__guest_count = guest_count
        self.update_date = datetime.now()

    # ----------------------- checkin ----------------------- #
    @property
    def checkin_date(self):
        """
        The check-in datetime for this booking.

        Returns:
            datetime: Check-in datetime.
        """
        return self.__checkin_date

    @checkin_date.setter
    def checkin_date(self, checkin_date):
        """
        Update the check-in datetime.

        Args:
            checkin_date (datetime): New check-in; must be >= today.

        Raises:
            TypeError: If not a datetime.
            ValueError: If date is in the past.
        """
        if not isinstance(checkin_date, datetime):
            raise TypeError("Checkin_date must be datetime format")
        elif checkin_date.date() < datetime.today().date():
            raise ValueError("Checkin_date must be later than today")
        self.__checkin_date = checkin_date
        self.update_date = datetime.now()

    # ----------------------- night count ----------------------- #
    @property
    def night_count(self):
        """
        Number of nights for this booking.

        Returns:
            int: Night count.
        """
        return self.__night_count

    @night_count.setter
    def night_count(self, night_count):
        """
        Update the number of nights.

        Args:
            night_count (int): New night count; must be > 0.

        Raises:
            TypeError: If not an int.
            ValueError: If <= 0.
        """
        if not isinstance(night_count, int):
            raise TypeError("Number of nights stayed must be integer")
        if night_count <= 0:
            raise ValueError("Number of nights stayed must be greater than 0")
        self.__night_count = night_count
        self.update_date = datetime.now()

    # ------------------------- user ------------------------- #
    @property
    def user(self):
        """
        The User who made this booking.

        Returns:
            User: Booking owner.
        """
        return self.__user

    @user.setter
    def user(self, user):
        """
        Update the booking’s user.

        Args:
            user (User): New user instance.

        Raises:
            TypeError: If not a User.
        """
        if not isinstance(user, User):
            TypeError("user must be of type User")
        self.__user = user

    # ----------------------- total price ----------------------- #
    @property
    def total_price(self):
        """
        Computed total price for this booking (guest_count × price × nights).

        Returns:
            float: Total booking price.
        """
        return self.__total_price

    # ----------------------- checkout ----------------------- #
    @property
    def checkout_date(self):
        """
        Computed checkout datetime based on check-in and night_count.

        Returns:
            datetime: Checkout datetime.
        """
        return self.__checkout_date

    # ----------------------- rating ----------------------- #
    @property
    def rating(self):
        """
        Rating given by the user for this booking.

        Returns:
            float or None: Rating value if set.
        """
        return self.__rating

    # ----------------------- review ----------------------- #
    @property
    def review(self):
        """
        Review object linked to this booking.

        Returns:
            Review or None: Review instance if created.
        """
        return self.__review

    @review.setter
    def review(self, review):
        """
        Associate a Review with this booking.

        Args:
            review (Review): Review to link.

        Raises:
            ValueError: If a review is already associated.
        """
        if self.review:
            raise ValueError("This Booking already has a review")
        self.__review = review
        self.update_date = datetime.now()
