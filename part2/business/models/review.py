from datetime import datetime
from .base import BaseModel


class Review(BaseModel):
    """
    Review – feedback left by a user or guest.

    Args
    ----
    text : str
        The review comment (1–1024 characters).
    rating : float
        Score between 0.0 and 5.0 (default 0.0).
    **kwargs : dict
        Optional keys forwarded to BaseModel:
        id, creation_date, update_date
    """

    # -------------------- constructor -------------------- #
    def __init__(self, text: str, rating: float = 0.0, **kwargs):
        super().__init__(**kwargs)          # handles id / timestamps
        self.__text = text
        self.__rating = rating

    # ----------------------- text ------------------------ #
    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, value):
        if not isinstance(value, str):
            raise TypeError("Review text must be a string")
        if not (1 <= len(value) <= 1024):
            raise ValueError("Review text must be 1-1024 characters")
        self.update_date = datetime.now()
        self.__text = value

    # ---------------------- rating ----------------------- #
    @property
    def rating(self):
        return self.__rating

    @rating.setter
    def rating(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Rating must be numeric")
        if not (0.0 <= value <= 5.0):
            raise ValueError("Rating must be between 0.0 and 5.0")
        self.update_date = datetime.now()
        self.__rating = float(value)

    # --------------------- helpers ----------------------- #
    def to_dict(self):
        return {
            "id": str(self.id),
            "creation_date": self.creation_date.isoformat(),
            "update_date": self.update_date.isoformat(),
            "text": self.text,
            "rating": self.rating,
        }

    def __repr__(self):
        return (
            f"Review(text={self.text!r}, rating={self.rating}, id={self.id})"
        )

    __str__ = __repr__
