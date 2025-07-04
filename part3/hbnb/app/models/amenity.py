"""
amenity.py: Defines the Amenity model with name validation and update timestamp.

This module provides the Amenity class inheriting from BaseModel,
enforcing name type and length constraints.
"""

from .base import BaseModel
from datetime import datetime


class Amenity(BaseModel):
    """
    Model representing an Amenity.

    Attributes:
        __name (str): Private name of the amenity.
        update_date (datetime): Timestamp of the last update.
    """

    def __init__(self, name, **kwargs):
        """
        Initialize a new Amenity instance.

        Validates name type and length, and delegates BaseModel initialization.

        Args:
            name (str): Name of the amenity.
            **kwargs: Additional keyword args passed to BaseModel.
        """
        super().__init__(**kwargs)

        # ---------- Init amenity ----------#
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if len(name) < 1 or len(name) > 32:
            raise ValueError("Name length must be between 1 and 32 characters")
        else:
            self.__name = name

    # ----------------------- name ----------------------- #
    @property
    def name(self):
        """
        Get the amenity's name.

        Returns:
            str: The name of the amenity.
        """
        return self.__name

    @name.setter
    def name(self, name):
        """
        Set or update the amenity's name with validation.

        Validates that the provided name is a non-empty string of length 1–32,
        and updates the update_date timestamp.

        Args:
            name (str): New name for the amenity.

        Raises:
            TypeError: If name is not a string.
            ValueError: If name length is outside 1–32 characters.
        """
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if len(name) < 1 or len(name) > 32:
            raise ValueError("Name length must be between 1 and 32 characters")
        self.__name = name
        self.update_date = datetime.now()
