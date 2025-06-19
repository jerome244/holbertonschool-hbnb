from base import BaseModel
from datetime import datetime


class Amenity(BaseModel):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)

        #---------- Init amenity ----------#
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if len(name) < 1 or len(name) > 32:
            raise ValueError("Name length must be between 1 and 32 characters")
        else:
            self.__name = name

    # ----------------------- name ----------------------- #
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if len(name) < 1 or len(name) > 32:
            raise ValueError("Name length must be between 1 and 32 characters")
        self.__name = name
        self.update_date = datetime.now()
