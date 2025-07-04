# app/models/host.py

from datetime import datetime
from typing import TYPE_CHECKING
from .user import User

if TYPE_CHECKING:
    from .place import Place

class Host(User):
    """
    Host model, subclass of User, with owned places and average rating.
    Inherits password hashing and verification from User.
    """
    def __init__(self, first_name: str, last_name: str, email: str,
                 password: str, is_admin: bool = False, **kwargs):
        """
        Initialize a new Host instance.

        Args:
            first_name (str): Host's first name
            last_name (str): Host's last name
            email (str): Host's email address
            password (str): Plaintext password, min length 8
            is_admin (bool): Admin flag (optional; defaults to False)
            **kwargs: Additional BaseModel kwargs
        """
        # Pass password (and is_admin) through to User so it gets hashed
        super().__init__(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            is_admin=is_admin,
            **kwargs
        )
        self.__owned_places = []

    @property
    def owned_places(self):
        """Return the list of places owned by this host."""
        return self.__owned_places

    def add_place(self, place):
        """Associate a Place with this Host."""
        from .place import Place
        if not isinstance(place, Place):
            raise TypeError("place must be a Place instance")
        self.__owned_places.append(place)
        self.updated_at = datetime.now()

    @property
    def rating(self):
        """
        Compute and return the host's average rating across owned places.

        Returns:
            float: Average rating of all owned places.

        Raises:
            AttributeError: If the host owns no places.
        """
        if not self.__owned_places:
            raise AttributeError("Must own at least one place")
        total = 0
        for place in self.__owned_places:
            total += place.get_average_rating()
        self.__rating = total / len(self.__owned_places)
        return self.__rating
