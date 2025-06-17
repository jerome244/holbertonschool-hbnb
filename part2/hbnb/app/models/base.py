import uuid
from datetime import datetime


class BaseModel:
    """
    Base class for all models providing ID and timestamp fields.
    """

    def __init__(self, id=None, created_at=None, updated_at=None):
        self.__id = id or str(uuid.uuid4())
        self.__created_at = created_at or datetime.now()
        self.__updated_at = updated_at or datetime.now()

    @property
    def id(self):
        return self.__id

    @property
    def created_at(self):
        return self.__created_at

    @property
    def updated_at(self):
        return self.__updated_at

    @updated_at.setter
    def updated_at(self, value):
        if not isinstance(value, datetime):
            raise TypeError("updated_at must be a datetime object")
        self.__updated_at = value

    def to_dict(self):
        return self.__dict__
