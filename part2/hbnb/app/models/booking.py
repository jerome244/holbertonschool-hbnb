from base import BaseModel
from datetime import datetime, timedelta
from user import User
# Check place for circular import
from place import Place
from typing import TYPE_CHECKING




class Booking(BaseModel):
    def __init__(self, guest_count, checkin_date, night_count, place, user, **kwargs):
        super().__init__(**kwargs)

        # ---------- Init place ---------- #
        if not isinstance(place, Place):
            TypeError("Place must be of type Place")
        else:
            self.__place = place

        # ---------- Init capacity ---------- #
        if guest_count > self.__place.capacity:
            raise ValueError(f"Number of guests exceeds {self.__place.title}'s capacity")
        else:
            self.__guest_count = guest_count

        # ---------- Init checkin_date ---------- #
        if not isinstance(checkin_date, datetime):
            raise TypeError("Checkin_date must be datetime format")
        elif checkin_date.date() < datetime.today().date():
            raise ValueError("Checkin_date must be later than today")
        else:
            self.checkin_date = checkin_date

        # ---------- Init night_count ---------- #
        if not isinstance(night_count, int):
            raise TypeError("Number of nights stayed must be integer")
        if night_count <= 0:
            raise ValueError("Number of nights stayed must be greater than 0")
        else:
            self.__night_count = night_count

        # ---------- Init user ---------- #
        if not isinstance(user, User):
            TypeError("user lust be of type User")
        else:
            self.__user = user


        self.__total_price = self.night_count * self.__place.price
        self.__checkout_date = self.checkin_date + timedelta(days=self.night_count)
        self.__rating = None
        self.__review = None

        user.add_booking(self)

    #----------------------- Place -----------------------#

    @property
    def place(self):
        return self.__place

    @place.setter
    def place(self, place):
        if not isinstance(place, Place):
            TypeError("Place must be of type Place")
        self.__place = place
        self.update_date = datetime.now()

    # ----------------------- guest count ----------------------- #

    @property
    def guest_count(self):
        return self.__guest_count

    @guest_count.setter
    def guest_count(self, guest_count):
        if guest_count > self.__place.capacity:
            raise ValueError(f"Number of guests exceeds {self.__place.title}'s capacity")
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
        elif checkin_date.date() < datetime.today().date():
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

    # ------------------------- user ------------------------- #

    @property
    def user(self):
         return self.__user

    @user.setter
    def user(self, user):
        if not isinstance(user, User):
            TypeError("user lust be of type User")
        self.__user = user

    # ----------------------- total price ----------------------- #

    @property
    def total_price(self):
        return self.__total_price

    # ----------------------- checkout ----------------------- #

    @property
    def checkout_date(self):
        return self.__checkout_date

    # ----------------------- rating ----------------------- #
    @property
    def rating(self):
        return self.__rating

    # ----------------------- review ----------------------- #

    @property
    def review(self):
        return self.__review

    @review.setter
    def review(self, review):
        if self.review:
            raise ValueError("This Booking already has a review")
        self.__review = review
        self.update_date = datetime.now()
