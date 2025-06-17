from base import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # from user import Host
    from amenity import Amenity
    from review import Review


class Place(BaseModel):
    def __init__(self, name, description, capacity, price_per_night, address, host, **kwargs):
        super().__init__(**kwargs)
        self.__name = name
        self.__description = description
        self.__capacity = capacity
        self.__price_per_night = price_per_night
        self.__address = address
        self.__host = host
        if hasattr(host, "add_place"):
            host.add_place(self)

        self.__amenities = []
        self.__reviews = []

    # ----------------------- name ----------------------- #
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        if not isinstance(name, str):
            raise TypeError("Name must be of type string")
        if not (2 <= len(name) <= 32):
            raise ValueError("Name length must be between 2 and 32 characters")
        self.__name = name

    # ----------------------- description ----------------------- #
    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, description):
        if not isinstance(description, str):
            raise TypeError("Description must be of type string")
        if not (2 <= len(description) <= 1024):
            raise ValueError("Description length must be between 2 and 1024 characters")
        self.__description = description

    # ----------------------- capacity ----------------------- #
    @property
    def capacity(self):
        return self.__capacity

    @capacity.setter
    def capacity(self, capacity):
        if not isinstance(capacity, int):
            raise TypeError("Capacity must be of type int")
        if not (1 <= capacity <= 64):
            raise ValueError("Capacity must be between 1 and 64")
        self.__capacity = capacity

    # ----------------------- price per night ----------------------- #
    @property
    def price_per_night(self):
        return self.__price_per_night

    @price_per_night.setter
    def price_per_night(self, price_per_night):
        if not isinstance(price_per_night, int):
            raise TypeError("Price per night must be of type int")
        if not (1 <= price_per_night <= 9999):
            raise ValueError("Price per night must be between 1 and 9999")
        self.__price_per_night = price_per_night

    # ----------------------- address ----------------------- #
    @property
    def address(self):
        return self.__address

    @address.setter
    def address(self, address):
        if not isinstance(address, str):
            raise TypeError("Address must be of type string")
        if not (2 <= len(address) <= 1024):
            raise ValueError("Address length must be between 2 and 1024 characters")
        self.__address = address

    # ----------------------- host ----------------------- #
    @property
    def host(self):
        return self.__host

    # ----------------------- Methods ----------------------- #
    def add_amenities(self, amenity):
        from amenity import Amenity
        if not isinstance(amenity, Amenity):
            raise TypeError("Must add an Amenity instance")
        self.__amenities.append(amenity)

    def add_review(self, review):
        from review import Review
        if not isinstance(review, Review):
            raise TypeError("Must add a Review instance")
        self.__reviews.append(review)

    def get_average_rating(self):
        if not self.__reviews:
            raise AttributeError("No review found in reviews")
        total = 0
        for review in self.__reviews:
            total += review.rating
        return total / len(self.__reviews)
