from base import BaseModel
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from place import Place


class Booking(BaseModel):
    def __init__(self, guest_count, checkin_date, night_count, place, **kwargs):
        super().__init__(**kwargs)
        self.__place = place
        self.guest_count = guest_count
        self.__checkin_date = checkin_date
        self.__night_count = night_count
        self.__total_price = self.night_count * self.__place.price
        self.__checkout_date = self.checkin_date + timedelta(days=self.night_count)
        self.__rating = None
        self.__review = None

    # ----------------------- guest count ----------------------- #
    @property
    def guest_count(self):
        return self.__guest_count

    @guest_count.setter
    def guest_count(self, guest_count):
        if guest_count > self.__place.capacity:
            raise ValueError(f"Number of guests exceeds {self.__place.name}'s capacity")
        self.__guest_count = guest_count
        self.update_date = datetime.now()

    # ----------------------- checkin ----------------------- #
    @property
    def checkin_date(self):
        return self.__checkin_date

    @checkin_date.setter
    def checkin_date(self, checkin_date):
        if not isinstance(checkin_date, datetime):
            raise TypeError("Checkin_date must be datetime format")
        if checkin_date.date() < datetime.today().date():
            raise ValueError("Checkin_date must be later than today")
        self.__checkin_date = checkin_date
        self.update_date = datetime.now()

    # ----------------------- night count ----------------------- #
    @property
    def night_count(self):
        return self.__night_count

    @night_count.setter
    def night_count(self, night_count):
        if not isinstance(night_count, int):
            raise TypeError("Number of nights stayed must be integer")
        if night_count <= 0:
            raise ValueError("Number of nights stayed must be greater than 0")
        self.__night_count = night_count
        self.update_date = datetime.now()

    # ----------------------- checkout ----------------------- #
    @property
    def checkout_date(self):
        return self.__checkout_date

    # ----------------------- total price ----------------------- #
    @property
    def total_price(self):
        return self.__total_price

    # ----------------------- rating ----------------------- #
    @property
    def rating(self):
        return self.__rating

    # ----------------------- review ----------------------- #
    @property
    def review(self):
        return self.__review
