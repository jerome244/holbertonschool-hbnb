from datetime import datetime
<<<<<<< HEAD
from host import Host
from base import BaseModel
=======
from .host import Host
from .base import BaseModel
>>>>>>> devJerome
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    """
    Check for circular import /!\
    """
    # Used to validate host type
    from amenity import Amenity
    from review import Review


class Place(BaseModel):
<<<<<<< HEAD
    def __init__(self, title, capacity, price, latitude, longitude, host, description="", **kwargs):
        super().__init__(**kwargs)

        #------------ Init title ------------#
        if not isinstance(title, str):
            raise TypeError("Name must be of type string")
        elif len(title) > 100:
            raise ValueError("Title length must not exceed 100 characters")
        else:
            self.__title = title

        #------------ Init capacity ------------#
        if not isinstance(capacity, int):
            raise TypeError("Capacity must be of type int")
        if capacity < 1 or capacity > 64:
            raise ValueError("Capacity must be between 1 and 64")
        else:
            self.__capacity = capacity

        #------------ Init price ------------#
        if not isinstance(price, (int, float)):
            raise TypeError("Price must be of type int or float")
        if price < 0:
            raise ValueError("Price must be a positive number")
        else:
            self.__price = price

        #------------ Init latitude ------------#
        if not isinstance(latitude, float):
            raise TypeError("Latitude must be of type float")
        if latitude < -90.0 or latitude > 90.0:
            raise ValueError("Latitude length must be between -90 and 90 degres")
        else:
            self.__latitude = latitude

        #------------ Init longitude ------------#
        if longitude < -180.0 or longitude > 180.0:
            raise ValueError("Longitude length must be between -180 and 180 degres")
        else:
            self.__longitude = longitude

        #------------ Init host ------------#
        if hasattr(host, "add_place"):
            host.add_place(self)
        self.__host = host

        #------------ Init description ------------#
        if not isinstance(description, str):
            raise TypeError("Description must be of type string")
        if len(description) < 3 or len(description) > 1024:
            raise ValueError("Description length must be between 2 and 1024 characters")
        else:
            self.__description = description

        #------------ Init amenities ------------#
        self.__amenities = []

        #------------ Init reviews ------------#
        self.__reviews = []

    # ----------------------- title ----------------------- #
=======
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
        super().__init__(**kwargs)
        self.__title = title
        self.__capacity = capacity
        self.__price = price
        self.__latitude = latitude
        self.__longitude = longitude
        if not isinstance(host, Host):
            raise TypeError("host must be an instance of the Host class")
        self.__host = host
        if hasattr(host, "add_place"):
            host.add_place(self)
        self.__description = description

        self.__amenities = []
        self.__reviews = []

    # ----------------------- name ----------------------- #
>>>>>>> devJerome
    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title):
        if not isinstance(title, str):
            raise TypeError("Name must be of type string")
        if len(title) > 100:
            raise ValueError("Title length must not exceed 100 characters")
        self.__title = title
<<<<<<< HEAD
        self.update_date = datetime.now()
=======
>>>>>>> devJerome

    # ----------------------- description ----------------------- #
    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, description):
        if not isinstance(description, str):
            raise TypeError("Description must be of type string")
<<<<<<< HEAD
        if len(description) < 2 or len(description) > 1024:
=======
        if not (2 <= len(description) <= 1024):
>>>>>>> devJerome
            raise ValueError("Description length must be between 2 and 1024 characters")
        self.__description = description
        self.update_date = datetime.now()

    # ----------------------- capacity ----------------------- #
    @property
    def capacity(self):
        return self.__capacity

    @capacity.setter
    def capacity(self, capacity):
        if not isinstance(capacity, int):
            raise TypeError("Capacity must be of type int")
<<<<<<< HEAD
        if capacity < 1 or capacity > 64:
=======
        if not (1 <= capacity <= 64):
>>>>>>> devJerome
            raise ValueError("Capacity must be between 1 and 64")
        self.__capacity = capacity
        self.update_date = datetime.now()

    # ----------------------- price per night ----------------------- #
    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, price):
        if not isinstance(price, (int, float)):
            raise TypeError("Price must be of type int or float")
        if price < 0:
            raise ValueError("Price must be a positive number")
        self.__price = price
        self.update_date = datetime.now()

    # ----------------------- latitude ----------------------- #
    @property
    def latitude(self):
        return self.__latitude

    @latitude.setter
    def latitude(self, latitude):
        if not isinstance(latitude, float):
            raise TypeError("Latitude must be of type float")
<<<<<<< HEAD
        if latitude < -90.0 or latitude > 90.0:
=======
        if latitude < -90.0 and latitude > 90.0:
>>>>>>> devJerome
            raise ValueError("Latitude length must be between -90 and 90 degres")
        self.__latitude = latitude
        self.update_date = datetime.now()

    # ----------------------- longitude ----------------------- #

    @property
    def longitude(self):
        return self.__longitude

    @longitude.setter
    def longitude(self, longitude):
        if not isinstance(longitude, float):
            raise TypeError("Longitude must be of type float")
<<<<<<< HEAD
        if longitude < -180.0 or longitude > 180.0:
=======
        if longitude < -180.0 and longitude > 180.0:
>>>>>>> devJerome
            raise ValueError("Longitude length must be between -180 and 180 degres")
        self.__longitude = longitude
        self.update_date = datetime.now()

<<<<<<< HEAD

=======
>>>>>>> devJerome
    # ----------------------- host ----------------------- #

    @property
    def host(self):
        return self.__host

    # ----------------------- Amenities ----------------------- #

    @property
    def amenities(self):
        return self.__amenities

<<<<<<< HEAD
 # ----------------------- Reviews ----------------------- #
=======
    # ----------------------- Reviews ----------------------- #
>>>>>>> devJerome

    @property
    def reviews(self):
        return self.__reviews

    # ----------------------- Methods ----------------------- #

    def add_amenity(self, amenity):
        from amenity import Amenity
<<<<<<< HEAD
=======

>>>>>>> devJerome
        if not isinstance(amenity, Amenity):
            raise TypeError("Must add an Amenity instance")
        self.__amenities.append(amenity)
        self.update_date = datetime.now()

    def add_review(self, review):
        from review import Review
<<<<<<< HEAD
=======

>>>>>>> devJerome
        if not isinstance(review, Review):
            raise TypeError("Must add a Review instance")
        self.__reviews.append(review)
        self.update_date = datetime.now()

    def get_average_rating(self):
        if not self.__reviews:
            return 0
        total = 0
        for review in self.__reviews:
            total += review.rating
        return total / len(self.__reviews)
