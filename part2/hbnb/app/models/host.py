"""
host.py: Defines the Host model extending User with owned places and ratings.

This module provides the Host class, inheriting from User, adding attributes
for owned places and dynamic rating computation.
"""

from .user import User
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .place import Place


class Host(User):
    """
    Model representing a Host with owned places and computed ratings.

    Attributes:
        __rating (float or None): Cached average rating.
        __owned_places (list): List of Place instances owned by this host.
    """

    def __init__(self, first_name, last_name, email, owned_places=None, **kwargs):
        """
        Initialize a new Host instance.

        Args:
            first_name (str): Host's first name.
            last_name (str): Host's last name.
            email (str): Host's email address.
            owned_places (list, optional): Initial list of Place instances.
            **kwargs: Additional keyword args passed to User.
        """
        super().__init__(first_name, last_name, email, **kwargs)
        self.__rating = None
        self.__owned_places = owned_places if owned_places is not None else []

    @property
    def owned_places(self):
        """
        Get the list of places owned by the host.

        Returns:
            list: List of Place instances.
        """
        return self.__owned_places

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

    def add_place(self, place):
        """
        Add a Place to the host's owned places list.

        Args:
            place (Place): Place instance to add.

        Raises:
            TypeError: If the provided object is not a Place.
        """
        from .place import Place

        if not isinstance(place, Place):
            raise TypeError("Must add a Place instance")
        # Check if added place already exists by ID
        if not any(
            existing_place.id == place.id for existing_place in self.owned_places
        ):
            self.__owned_places.append(place)
            self.update_date = datetime.now()
