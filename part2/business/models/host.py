from datetime import datetime
from .user import User


class Host(User):
    """
    Host – a User who can host others and has a rating.

    Attributes
    ----------
    host_rating : float
        Rating between 0.0 and 5.0.
    """

    def __init__(self, username, email, host_rating=0.0,
                 id=None, creation_date=None, update_date=None):
        super().__init__(username=username,
                         email=email,
                         id=id,
                         creation_date=creation_date,
                         update_date=update_date)
        self.__host_rating = host_rating

    # -------------------- host_rating ----------------------- #
    @property
    def host_rating(self):
        return self.__host_rating

    @host_rating.setter
    def host_rating(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("host_rating must be a number")
        if not (0.0 <= value <= 5.0):
            raise ValueError("host_rating must be between 0.0 and 5.0")
        self.update_date = datetime.now()
        self.__host_rating = float(value)

    # -------------------- representation -------------------- #
    def __repr__(self):
        return (
            f"Host(username={self.username!r}, email={self.email!r}, "
            f"host_rating={self.host_rating}, id={self.id})"
        )

    __str__ = __repr__
