from datetime import datetime
from uuid import UUID
from .base import BaseModel


class Review(BaseModel):
    """
    Review – feedback left by a user about a stay (booking).

    Required
    --------
    text : str        (1–1024 characters)
    rating : float    (0.0 – 5.0)

    Optional
    --------
    booking_id : UUID | None   (booking this review relates to)
    **kwargs    -> id, creation_date, update_date (BaseModel)
    """

    def __init__(
        self, text: str, rating: float = 0.0, booking_id: UUID | None = None, **kwargs
    ):
        super().__init__(**kwargs)
        self.__text = text
        self.__rating = rating
        self.__booking_id = booking_id

    # ---------- text ----------
    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, value):
        if not isinstance(value, str):
            raise TypeError("Review text must be a string")
        if not (1 <= len(value) <= 1024):
            raise ValueError("Review text length 1-1024 chars")
        self.update_date = datetime.now()
        self.__text = value

    # --------- rating ---------
    @property
    def rating(self):
        return self.__rating

    @rating.setter
    def rating(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Rating must be numeric")
        if not (0.0 <= value <= 5.0):
            raise ValueError("Rating must be 0.0-5.0")
        self.update_date = datetime.now()
        self.__rating = float(value)

    # ------ booking_id --------
    @property
    def booking_id(self):
        return self.__booking_id

    @booking_id.setter
    def booking_id(self, value):
        if value is not None and not isinstance(value, UUID):
            raise TypeError("booking_id must be UUID or None")
        self.update_date = datetime.now()
        self.__booking_id = value

    # -------- helpers ---------
    def to_dict(self):
        return {
            "id": str(self.id),
            "creation_date": self.creation_date.isoformat(),
            "update_date": self.update_date.isoformat(),
            "text": self.text,
            "rating": self.rating,
            "booking_id": str(self.booking_id) if self.booking_id else None,
        }

    def __repr__(self):
        return (
            f"Review(text={self.text!r}, rating={self.rating}, "
            f"booking_id={self.booking_id}, id={self.id})"
        )

    __str__ = __repr__
