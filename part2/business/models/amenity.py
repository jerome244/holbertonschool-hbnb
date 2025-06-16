from .base import BaseModel
from datetime import datetime, timezone

"""
Amenity - A class describing an amenity
"""


class Amenity(BaseModel):
    def __init__(self, name, description, **kwargs):
        super().__init__(**kwargs)
        self.__name = name
        self.__description = description

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        """
        name setter - Enforces type being string and
        length between 1 and 1024 characters
        """
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if len(name) <= 1 or len(name) >= 32:
            raise ValueError("Name length must be between 1 and" " 32 characters")
        self.update_date = datetime.now()
        self.__name = name

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, desc):
        """
        description setter - Enforces type string and
        length between 1 and 1024 characters
        """
        if not isinstance(desc, str):
            raise TypeError("Description must be a string")
        if len(desc) <= 1 or len(desc) >= 1024:
            raise ValueError("Name length must be between 1 and " "1024 characters")
        self.update_date = datetime.now()
        self.__description = desc
