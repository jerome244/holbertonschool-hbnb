from datetime import datetime
from .user import User


class Host(User):
    """
    Host – a user who can host others, with a rating.

    Args
    ----
    username : str
    email : str
    host_rating : float, default 0.0
    **kwargs : dict
        Optional keys passed to BaseModel (id, creation_date, update_date)
    """

    def __init__(self, username: str, email: str, host_rating: float = 0.0, **kwargs):
        super().__init__(username=username, email=email, **kwargs)
        self.__host_rating = host_rating

    # -------------- host_rating -------------- #
    @property
    def host_rating(self):
        return self.__host_rating

    @host_rating.setter
    def host_rating(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("host_rating must be numeric")
        if not (0.0 <= value <= 5.0):
            raise ValueError("host_rating must be between 0.0 and 5.0")
        self.update_date = datetime.now()
        self.__host_rating = float(value)

    # --------------- helpers ----------------- #
    def to_dict(self):
        data = super().to_dict()
        data["host_rating"] = self.host_rating
        return data

    def __repr__(self):
        return (
            f"Host(username={self.username!r}, email={self.email!r}, "
            f"host_rating={self.host_rating}, id={self.id})"
        )

    __str__ = __repr__
