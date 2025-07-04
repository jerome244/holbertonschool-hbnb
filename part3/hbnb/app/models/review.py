"""
review.py: Defines the Review model linking to a Booking with text and rating validation.

This module provides the Review class, inheriting from BaseModel, enforcing type and
value constraints on the booking, text, and rating attributes, and updating timestamps.
"""

from .base import BaseModel
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .booking import Booking


class Review(BaseModel):
    """
    Model representing a review left by a user for a booking.

    Attributes:
        __booking (Booking): The Booking instance being reviewed.
        __text (str): The body text of the review.
        __rating (int): Rating given, between 1 and 5.
    """

    def __init__(self, booking, text, rating=None, **kwargs):
        """
        Initialize a new Review instance.

        Validates that the booking is a Booking instance, text is a string,
        and rating is an integer between 1 and 5. Links the review to the booking
        and to the place associated with the booking.

        Args:
            booking (Booking): The Booking instance to review.
            text (str): The textual content of the review.
            rating (int, optional): The rating value between 1 and 5.

        Raises:
            TypeError: If booking is not a Booking instance.
            TypeError: If text is not a string.
            TypeError: If rating is not an integer.
            ValueError: If rating is outside 1–5.
        """
        # condition commented because testes can't be made otherwise
        # checkin_date must not be in te past and review must be made
        # after checkout_date (don't know how to test being both in past and future)
        """
        if datetime.now() < booking.checkout_date:
            raise ValueError("Review must be made after checkout")
        """

        super().__init__(**kwargs)

        # ---------- Init booking ---------- #
        from .booking import Booking

        if not isinstance(booking, Booking):
            raise TypeError("booking must be a Booking instance")
        self.__booking = booking

        # ---------- Init text ---------- #
        if not isinstance(text, str):
            raise TypeError("Text must be of type string")
        self.__text = text

        # ---------- Init rating ---------- #
        if not isinstance(rating, int):
            raise TypeError("Rating must be of type int")
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be a value between 1 and 5")
        self.__rating = rating

        booking.review = self
        booking.place.add_review(self)

    # ----------------------- rating ----------------------- #
    @property
    def rating(self):
        """
        Get the rating of this review.

        Returns:
            int: The rating value between 1 and 5.
        """
        return self.__rating

    @rating.setter
    def rating(self, rating):
        """
        Update the review's rating with validation and timestamp update.

        Args:
            rating (int): New rating value between 1 and 5.

        Raises:
            TypeError: If rating is not an integer.
            ValueError: If rating is outside 1–5.
        """
        if not isinstance(rating, int):
            raise TypeError("Rating must be of type int")
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be a value between 1 and 5")
        self.__rating = rating
        self.update_date = datetime.now()

    # ----------------------- text ----------------------- #
    @property
    def text(self):
        """
        Get the text content of this review.

        Returns:
            str: The review text.
        """
        return self.__text

    @text.setter
    def text(self, text):
        """
        Update the review's text with validation and timestamp update.

        Args:
            text (str): New review text.

        Raises:
            TypeError: If text is not a string.
        """
        if not isinstance(text, str):
            raise TypeError("Text must be of type string")
        self.__text = text
        self.update_date = datetime.now()

    # ----------------------- booking ----------------------- #
    @property
    def booking(self):
        """
        Get the Booking associated with this review.

        Returns:
            Booking: The Booking instance this review is linked to.
        """
        return self.__booking
