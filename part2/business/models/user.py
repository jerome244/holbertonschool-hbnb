from datetime import datetime
from .base import BaseModel


class User(BaseModel):
    """
    User – represents a system user.

    Attributes
    ----------
    username : str
        Unique username.
    email : str
        Email address.
    """

    def __init__(self, username, email,
                 id=None, creation_date=None, update_date=None):
        super().__init__(id=id,
                         creation_date=creation_date,
                         update_date=update_date)
        self.__username = username
        self.__email = email

    # ----------------------- username ----------------------- #
    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, value):
        if not isinstance(value, str):
            raise TypeError("Username must be a string")
        if not (2 <= len(value) <= 32):
            raise ValueError("Username must be between 2 and 32 characters")
        self.update_date = datetime.now()
        self.__username = value

    # ------------------------ email ------------------------- #
    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        if not isinstance(value, str):
            raise TypeError("Email must be a string")
        if "@" not in value or len(value) > 128:
            raise ValueError("Invalid email format or too long")
        self.update_date = datetime.now()
        self.__email = value

    # -------------------- representation -------------------- #
    def __repr__(self):
        return (
            f"User(username={self.username!r}, email={self.email!r}, "
            f"id={self.id})"
        )

    __str__ = __repr__
