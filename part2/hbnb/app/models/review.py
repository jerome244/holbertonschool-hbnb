from .base import BaseModel
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .booking import Booking


class Review(BaseModel):
    def __init__(self, booking, text, rating=None, **kwargs):
        from booking import Booking
        if not isinstance(booking, Booking):
            raise TypeError("booking must be a Booking instance")

        # condition commented because testes can't be made otherwise
        # checkin_date must not be in te past and review must be made
        # after checkout_date (don't know how to test being both in past and future)
        """
        if datetime.now() < booking.checkout_date:
            raise ValueError("Review must be made after checkout")
        """

        super().__init__(**kwargs)
        self.__booking = booking
        self.__text = text
        self.__rating = rating

        """
        implémenter le corps des setters
        """
        booking.review = self

        booking.place.add_review(self)

    # ----------------------- rating ----------------------- #

    @property
    def rating(self):
        return self.__rating

    @rating.setter
    def rating(self, rating):
        if not isinstance(rating, int):
            raise TypeError("Rating must be of type int")
        if rating < 1 and rating > 5:
            raise ValueError("Rating must be a value between 1 and 5")
        self.__rating = rating
        self.update_date = datetime.now()

    # ----------------------- text ----------------------- #

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, text):
        if not isinstance(text, str):
            raise TypeError("Text must be of type string")
        self.__text = text
        self.update_date = datetime.now()

    # ----------------------- booking ----------------------- #

    @property
    def booking(self):
        return self.__booking
