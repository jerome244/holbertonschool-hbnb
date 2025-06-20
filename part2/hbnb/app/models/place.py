"""
place.py: Defines the Place model with validation, amenities, reviews, and bookings management.

This module provides the Place class, inheriting from BaseModel, enforcing type and value
constraints on attributes and managing associated amenities, reviews, and bookings.
"""

from datetime import datetime
from .host import Host
from .base import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    """
    Check for circular import to validate types.
    """
    from amenity import Amenity
    from review import Review


class Place(BaseModel):
    """
    Model representing a place listing.

    Attributes:
        __title (str): Title of the place.
        __capacity (int): Maximum number of guests.
        __price (float): Price per night.
        __latitude (float): Latitude coordinate.
        __longitude (float): Longitude coordinate.
        __host (Host): Owner of the place.
        __description (str): Description text.
        __amenities (list): List of associated Amenity instances.
        __reviews (list): List of associated Review instances.
        __bookings (list): List of associated Booking instances.
    """

    def __init__(
        self,
        title,
        capacity,
        price,
        latitude,
        longitude,
        host,
        description="",
        **kwargs
    ):
        """
        Initialize a new Place instance.

        Validates types and value ranges, registers with host, and initializes
        empty lists for amenities, reviews, and bookings.

        Args:
            title (str): Title of the place, max length 100.
            capacity (int): Number of guests, between 1 and 64.
            price (int or float): Price per night, non-negative.
            latitude (float): Latitude, between -90.0 and 90.0.
            longitude (float): Longitude, between -180.0 and 180.0.
            host (Host): Host instance owning the place.
            description (str, optional): Description text, length 2–1024.
            **kwargs: Additional keyword args passed to BaseModel.
        """
        super().__init__(**kwargs)

        # ------------ Init title ------------#
        if not isinstance(title, str):
            raise TypeError("Name must be of type string")
        elif len(title) > 100:
            raise ValueError("Title length must not exceed 100 characters")
        else:
            self.__title = title

        # ------------ Init capacity ------------#
        if not isinstance(capacity, int):
            raise TypeError("Capacity must be of type int")
        if capacity < 1 or capacity > 64:
            raise ValueError("Capacity must be between 1 and 64")
        else:
            self.__capacity = capacity

        # ------------ Init price ------------#
        if not isinstance(price, (int, float)):
            raise TypeError("Price must be of type int or float")
        if price < 0:
            raise ValueError("Price must be a positive number")
        else:
            self.__price = price

        # ------------ Init latitude ------------#
        if not isinstance(latitude, float):
            raise TypeError("Latitude must be of type float")
        if latitude < -90.0 or latitude > 90.0:
            raise ValueError("Latitude length must be between -90 and 90 degres")
        else:
            self.__latitude = latitude

        # ------------ Init longitude ------------#
        if not isinstance(longitude, float):
            raise TypeError("Longitude must be of type float")
        if longitude < -180.0 or longitude > 180.0:
            raise ValueError("Longitude length must be between -180 and 180 degres")
        else:
            self.__longitude = longitude

        # ------------ Init host ------------#
        if hasattr(host, "add_place") and isinstance(host, Host):
            host.add_place(self)
        self.__host = host

        # ------------ Init description ------------#
        if not isinstance(description, str):
            raise TypeError("Description must be of type string")
        if len(description) < 3 or len(description) > 1024:
            raise ValueError("Description length must be between 2 and 1024 characters")
        else:
            self.__description = description

        # ------------ Init amenities ------------#
        self.__amenities = []

        # ------------ Init reviews ------------#
        self.__reviews = []

        # ------------ Init bookings ------------#
        self.__bookings = []

    # ----------------------- title ----------------------- #
    @property
    def title(self):
        """
        Get the place title.

        Returns:
            str: Title of the place.
        """
        return self.__title

    @title.setter
    def title(self, title):
        """
        Update the place title with validation.

        Args:
            title (str): New title, max length 100.

        Raises:
            TypeError: If title not a string.
            ValueError: If title length exceeds 100.
        """
        if not isinstance(title, str):
            raise TypeError("Name must be of type string")
        if len(title) > 100:
            raise ValueError("Title length must not exceed 100 characters")
        self.__title = title
        self.update_date = datetime.now()

    # ----------------------- description ----------------------- #
    @property
    def description(self):
        """
        Get the place description.

        Returns:
            str: Description text.
        """
        return self.__description

    @description.setter
    def description(self, description):
        """
        Update the place description with validation.

        Args:
            description (str): New description, length 2–1024.

        Raises:
            TypeError: If description not a string.
            ValueError: If length outside 2–1024.
        """
        if not isinstance(description, str):
            raise TypeError("Description must be of type string")
        if len(description) < 2 or len(description) > 1024:
            raise ValueError("Description length must be between 2 and 1024 characters")
        self.__description = description
        self.update_date = datetime.now()

    # ----------------------- capacity ----------------------- #
    @property
    def capacity(self):
        """
        Get the place capacity.

        Returns:
            int: Capacity (max guests).
        """
        return self.__capacity

    @capacity.setter
    def capacity(self, capacity):
        """
        Update the place capacity with validation.

        Args:
            capacity (int): New capacity, between 1 and 64.

        Raises:
            TypeError: If capacity not an int.
            ValueError: If outside 1–64.
        """
        if not isinstance(capacity, int):
            raise TypeError("Capacity must be of type int")
        if capacity < 1 or capacity > 64:
            raise ValueError("Capacity must be between 1 and 64")
        self.__capacity = capacity
        self.update_date = datetime.now()

    # ----------------------- price per night ----------------------- #
    @property
    def price(self):
        """
        Get the nightly price for the place.

        Returns:
            float: Price per night.
        """
        return self.__price

    @price.setter
    def price(self, price):
        """
        Update the nightly price with validation.

        Args:
            price (int or float): New price, must be non-negative.

        Raises:
            TypeError: If price not int or float.
            ValueError: If price negative.
        """
        if not isinstance(price, (int, float)):
            raise TypeError("Price must be of type int or float")
        if price < 0:
            raise ValueError("Price must be a positive number")
        self.__price = price
        self.update_date = datetime.now()

    # ----------------------- latitude ----------------------- #
    @property
    def latitude(self):
        """
        Get the latitude coordinate.

        Returns:
            float: Latitude of the place.
        """
        return self.__latitude

    @latitude.setter
    def latitude(self, latitude):
        """
        Update the latitude with validation.

        Args:
            latitude (float): New latitude, between -90 and 90.

        Raises:
            TypeError: If latitude not float.
            ValueError: If outside valid range.
        """
        if not isinstance(latitude, float):
            raise TypeError("Latitude must be of type float")
        if latitude < -90.0 or latitude > 90.0:
            raise ValueError("Latitude length must be between -90 and 90 degres")
        self.__latitude = latitude
        self.update_date = datetime.now()

    # ----------------------- longitude ----------------------- #
    @property
    def longitude(self):
        """
        Get the longitude coordinate.

        Returns:
            float: Longitude of the place.
        """
        return self.__longitude

    @longitude.setter
    def longitude(self, longitude):
        """
        Update the longitude with validation.

        Args:
            longitude (float): New longitude, between -180 and 180.

        Raises:
            TypeError: If longitude not float.
            ValueError: If outside valid range.
        """
        if not isinstance(longitude, float):
            raise TypeError("Longitude must be of type float")
        if longitude < -180.0 or longitude > 180.0:
            raise ValueError("Longitude length must be between -180 and 180 degres")
        self.__longitude = longitude
        self.update_date = datetime.now()

    # ----------------------- host ----------------------- #
    @property
    def host(self):
        """
        Get the host of the place.

        Returns:
            Host: Host instance who owns the place.
        """
        return self.__host

    # ----------------------- Amenities ----------------------- #
    @property
    def amenities(self):
        """
        Get associated amenities.

        Returns:
            list: List of Amenity instances.
        """
        return self.__amenities

    def add_amenity(self, amenity):
        """
        Associate an Amenity with this place.

        Args:
            amenity (Amenity): Amenity instance to add.

        Raises:
            TypeError: If amenity not an Amenity instance.
        """
        from amenity import Amenity

        if not isinstance(amenity, Amenity):
            raise TypeError("Must add an Amenity instance")
        self.__amenities.append(amenity)
        self.update_date = datetime.now()

    # ----------------------- Reviews ----------------------- #
    @property
    def reviews(self):
        """
        Get associated reviews.

        Returns:
            list: List of Review instances.
        """
        return self.__reviews

    def add_review(self, review):
        """
        Associate a Review with this place.

        Args:
            review (Review): Review instance to add.

        Raises:
            TypeError: If review not a Review instance.
        """
        from review import Review

        if not isinstance(review, Review):
            raise TypeError("Must add a Review instance")
        self.__reviews.append(review)
        self.update_date = datetime.now()

    # ----------------------- Methods ----------------------- #
    def get_average_rating(self):
        """
        Calculate the average rating from all reviews.

        Returns:
            float: Average of review.rating, or 0 if no reviews.
        """
        if not self.__reviews:
            return 0
        total = 0
        for review in self.__reviews:
            total += review.rating
        return total / len(self.__reviews)

    def add_booking(self, booking):
        """
        Associate a Booking with this place.

        Args:
            booking: Booking instance to add.
        """
        if booking not in self.__bookings:
            self.__bookings.append(booking)
