from base import BaseModel
from datetime import datetime


class Amenity(BaseModel):
    def __init__(self, name, description, **kwargs):
        super().__init__(**kwargs)
        self.__name = name
        self.__description = description

    # ----------------------- name ----------------------- #
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if not (1 <= len(name) <= 32):
            raise ValueError("Name length must be between 1 and 32 characters")
        self.__name = name
        self.update_date = datetime.now()

    # ----------------------- description ----------------------- #
    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, desc):
        if not isinstance(desc, str):
            raise TypeError("Description must be a string")
        if not (1 <= len(desc) <= 1024):
            raise ValueError("Description length must be between 1 and 1024 characters")
        self.__description = desc
        self.update_date = datetime.now()
