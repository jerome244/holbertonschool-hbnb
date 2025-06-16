from datetime import datetime
from uuid import UUID
from .base import BaseModel


class Place(BaseModel):
    """
    Place – a property listing.

    Required
    --------
    name     : str  (1-128 chars)
    city_id  : UUID
    user_id  : UUID   (owner/host)

    Optional
    --------
    description      : str | None (≤1024)
    number_rooms     : int ≥0
    number_bathrooms : int ≥0
    max_guests       : int ≥0
    price_by_night   : int ≥0
    latitude         : float | None
    longitude        : float | None
    **kwargs         : id, creation_date, update_date
    """

    def __init__(
        self,
        name: str,
        city_id: UUID,
        user_id: UUID,
        description: str | None = None,
        number_rooms: int = 0,
        number_bathrooms: int = 0,
        max_guests: int = 0,
        price_by_night: int = 0,
        latitude: float | None = None,
        longitude: float | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.__name = name
        self.__city_id = city_id
        self.__user_id = user_id

        self.description = description
        self.number_rooms = number_rooms
        self.number_bathrooms = number_bathrooms
        self.max_guests = max_guests
        self.price_by_night = price_by_night
        self.latitude = latitude
        self.longitude = longitude

    # ---- core fields ----
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, v):
        if not isinstance(v, str) or not (1 <= len(v) <= 128):
            raise ValueError("name must be 1-128 chars")
        self.update_date = datetime.now()
        self.__name = v

    @property
    def city_id(self):
        return self.__city_id

    @city_id.setter
    def city_id(self, v):
        if not isinstance(v, UUID):
            raise TypeError("city_id must be UUID")
        self.update_date = datetime.now()
        self.__city_id = v

    @property
    def user_id(self):
        return self.__user_id

    @user_id.setter
    def user_id(self, v):
        if not isinstance(v, UUID):
            raise TypeError("user_id must be UUID")
        self.update_date = datetime.now()
        self.__user_id = v

    # ---- optional simple strs ----
    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, v):
        if v is not None:
            if not isinstance(v, str) or len(v) > 1024:
                raise ValueError("description ≤1024 chars or None")
        self.update_date = datetime.now()
        self.__description = v

    # ---- numeric helpers ----
    def _ensure_non_neg_int(self, field, val):
        if not isinstance(val, int) or val < 0:
            raise ValueError(f"{field} must be int ≥0")

    @property
    def number_rooms(self):
        return self.__number_rooms

    @number_rooms.setter
    def number_rooms(self, v):
        self._ensure_non_neg_int("number_rooms", v)
        self.update_date = datetime.now()
        self.__number_rooms = v

    @property
    def number_bathrooms(self):
        return self.__number_bathrooms

    @number_bathrooms.setter
    def number_bathrooms(self, v):
        self._ensure_non_neg_int("number_bathrooms", v)
        self.update_date = datetime.now()
        self.__number_bathrooms = v

    @property
    def max_guests(self):
        return self.__max_guests

    @max_guests.setter
    def max_guests(self, v):
        self._ensure_non_neg_int("max_guests", v)
        self.update_date = datetime.now()
        self.__max_guests = v

    @property
    def price_by_night(self):
        return self.__price_by_night

    @price_by_night.setter
    def price_by_night(self, v):
        self._ensure_non_neg_int("price_by_night", v)
        self.update_date = datetime.now()
        self.__price_by_night = v

    # ---- latitude / longitude ----
    @property
    def latitude(self):
        return self.__latitude

    @latitude.setter
    def latitude(self, v):
        if v is not None and not isinstance(v, (int, float)):
            raise TypeError("latitude must be float or None")
        self.update_date = datetime.now()
        self.__latitude = None if v is None else float(v)

    @property
    def longitude(self):
        return self.__longitude

    @longitude.setter
    def longitude(self, v):
        if v is not None and not isinstance(v, (int, float)):
            raise TypeError("longitude must be float or None")
        self.update_date = datetime.now()
        self.__longitude = None if v is None else float(v)

    # ---- helpers ----
    def to_dict(self):
        return {
            "id": str(self.id),
            "creation_date": self.creation_date.isoformat(),
            "update_date": self.update_date.isoformat(),
            "name": self.name,
            "city_id": str(self.city_id),
            "user_id": str(self.user_id),
            "description": self.description,
            "number_rooms": self.number_rooms,
            "number_bathrooms": self.number_bathrooms,
            "max_guests": self.max_guests,
            "price_by_night": self.price_by_night,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    def __repr__(self):
        return (
            f"Place(name={self.name!r}, city_id={self.city_id}, "
            f"user_id={self.user_id}, id={self.id})"
        )

    __str__ = __repr__
