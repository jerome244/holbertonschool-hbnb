from datetime import datetime
from uuid import UUID
from .base import BaseModel


class Booking(BaseModel):
    """
    Booking – reservation of a Place by a User.

    Required
    --------
    user_id    : UUID
    place_id   : UUID
    start_date : datetime
    end_date   : datetime

    **kwargs : id, creation_date, update_date
    """

    def __init__(
        self,
        user_id: UUID,
        place_id: UUID,
        start_date: datetime,
        end_date: datetime,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.place_id = place_id
        self.start_date = start_date
        self.end_date = end_date

    # ------ user_id ------
    @property
    def user_id(self):
        return self.__user_id

    @user_id.setter
    def user_id(self, v):
        if not isinstance(v, UUID):
            raise TypeError("user_id must be UUID")
        self.update_date = datetime.now()
        self.__user_id = v

    # ------ place_id -----
    @property
    def place_id(self):
        return self.__place_id

    @place_id.setter
    def place_id(self, v):
        if not isinstance(v, UUID):
            raise TypeError("place_id must be UUID")
        self.update_date = datetime.now()
        self.__place_id = v

    # ---- start_date -----
    @property
    def start_date(self):
        return self.__start_date

    @start_date.setter
    def start_date(self, v):
        if not isinstance(v, datetime):
            raise TypeError("start_date must be datetime")
        self.update_date = datetime.now()
        self.__start_date = v

    # ----- end_date ------
    @property
    def end_date(self):
        return self.__end_date

    @end_date.setter
    def end_date(self, v):
        if not isinstance(v, datetime):
            raise TypeError("end_date must be datetime")
        if v <= self.start_date:
            raise ValueError("end_date must be after start_date")
        self.update_date = datetime.now()
        self.__end_date = v

    # ---- helpers --------
    def to_dict(self):
        return {
            "id": str(self.id),
            "creation_date": self.creation_date.isoformat(),
            "update_date": self.update_date.isoformat(),
            "user_id": str(self.user_id),
            "place_id": str(self.place_id),
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
        }

    def __repr__(self):
        return (
            f"Booking(user_id={self.user_id}, place_id={self.place_id}, "
            f"start={self.start_date.date()}, end={self.end_date.date()}, "
            f"id={self.id})"
        )

    __str__ = __repr__
