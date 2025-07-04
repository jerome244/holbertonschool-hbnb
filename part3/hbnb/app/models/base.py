"""
base.py: Defines the BaseModel with UUID and timestamp management.

This module provides the BaseModel class, which supplies all models with
a unique identifier, creation timestamp, update timestamp, and a dictionary
serialization method.
"""

import uuid
from datetime import datetime


class BaseModel:
    """
    Base class for all models providing ID and timestamp fields.

    Attributes:
        __id (str): Unique identifier for the instance.
        __created_at (datetime): Timestamp when the instance was created.
        __updated_at (datetime): Timestamp when the instance was last updated.
    """

    def __init__(self, id=None, created_at=None, updated_at=None):
        """
        Initialize a new BaseModel instance.

        Args:
            id (str, optional): Predefined unique identifier. If None, a new UUID4 is generated.
            created_at (datetime, optional): Predefined creation timestamp. Defaults to now.
            updated_at (datetime, optional): Predefined update timestamp. Defaults to now.
        """
        self.__id = id or str(uuid.uuid4())
        self.__created_at = created_at or datetime.now()
        self.__updated_at = updated_at or datetime.now()

    @property
    def id(self):
        """
        Get the unique identifier of the instance.

        Returns:
            str: The UUID string of the instance.
        """
        return self.__id

    @property
    def created_at(self):
        """
        Get the creation timestamp of the instance.

        Returns:
            datetime: When the instance was created.
        """
        return self.__created_at

    @property
    def updated_at(self):
        """
        Get the last update timestamp of the instance.

        Returns:
            datetime: When the instance was last updated.
        """
        return self.__updated_at

    @updated_at.setter
    def updated_at(self, value):
        """
        Set the last update timestamp of the instance.

        Args:
            value (datetime): New update timestamp.

        Raises:
            TypeError: If the provided value is not a datetime object.
        """
        if not isinstance(value, datetime):
            raise TypeError("updated_at must be a datetime object")
        self.__updated_at = value

    def to_dict(self):
        """
        Convert this model instance to a dictionary.

        Returns:
            dict: A dict containing all private attributes of the instance.
        """
        return self.__dict__
