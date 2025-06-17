from user import User
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from place import Place


class Host(User):
    def __init__(self, first_name, last_name, email, owned_places=None, **kwargs):
        super().__init__(first_name, last_name, email, **kwargs)
        self.__rating = None
        self.__owned_places = owned_places if owned_places is not None else []

    @property
    def owned_places(self):
        return self.__owned_places

    @property
    def rating(self):
        if not self.__owned_places:
            raise AttributeError("Must own at least one place")
        total = 0
        for place in self.__owned_places:
            total += place.get_average_rating()
        self.__rating = total / len(self.__owned_places)
        return self.__rating


    def add_place(self, place):
        from place import Place
        if not isinstance(place, Place):
            raise TypeError("Must add a Place instance")
        if not any(existing_place.id == place.id for existing_place in self.owned_places):
            self.__owned_places.append(place)
            self.update_date = datetime.now()
