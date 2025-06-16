import uuid
from datetime import datetime, timezone


class BaseModel:
    """
    Base class for all models providing ID and timestamp fields.

    Attributes:
        id (str): Unique identifier.
        created_at (str): Creation timestamp in ISO format.
        updated_at (str): Last update timestamp in ISO format.
    """

    def __init__(self, id=None, creation_date=None, update_date=None):
        """
        Initialize the base model with optional keyword overrides.

        Args:
            kwargs: Dictionary with optional keys
            'id', 'created_at', 'updated_at'.

        Raises:
            Exception: If initialization encounters unexpected errors.
        """

        self.__id = id if id else uuid.uuid4()
        self.__creation_date = creation_date if creation_date else datetime.now()
        self.__update_date = update_date if update_date else datetime.now()

    @property
    def id(self):
        return self.__id

    @property
    def creation_date(self):
        return self.__creation_date

    @property
    def update_date(self):
        return self.__update_date

    @update_date.setter
    def update_date(self, value):
        if not isinstance(value, datetime):
            raise TypeError("update_date must be a datetime object")
        self.__update_date = value

    def to_dict(self):
        return self.__dict__
