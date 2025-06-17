from base import BaseModel
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from booking import Booking


class Review(BaseModel):
    def __init__(self, booking, comment=None, rating=None, **kwargs):
        from booking import Booking
        if not isinstance(booking, Booking):
            raise TypeError("booking must be a Booking instance")

        if datetime.now() < booking.checkout_date:
            raise ValueError("Review must be made after checkout")
        super().__init__(**kwargs)
        self.__booking = booking
        self.__comment = None
        self.__rating = None

    # ----------------------- rating ----------------------- #
    @property
    def rating(self):
        return self.__rating

    @rating.setter
    def rating(self, rating):
        if not isinstance(rating, (int, float)):
            raise TypeError("Rating must be of type int")
        if not (0 <= rating <= 5):
            raise ValueError("Rating must be a value between 0 and 5")
        self.__rating = rating
        self.update_date = datetime.now()

    # ----------------------- comment ----------------------- #
    @property
    def comment(self):
        return self.__comment

    @comment.setter
    def comment(self, comment):
        if not isinstance(comment, str):
            raise TypeError("Comment must be of type string")
        if not (0 < len(comment) <= 1024):
            raise ValueError("Comment length must be between 1 and 1024")
        self.__comment = comment
        self.update_date = datetime.now()

    # ----------------------- booking ----------------------- #
    @property
    def booking(self):
        return self.__booking
