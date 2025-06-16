from datetime import datetime
from .base import BaseModel


class User(BaseModel):
    """
    User – represents a system user.

    Args
    ----
    username : str
    email : str
    **kwargs : dict
        Optional keys: id, creation_date, update_date
    """

    def __init__(self, username: str, email: str, **kwargs):
        super().__init__(**kwargs)          # handles id / timestamps
        self.__username = username
        self.__email = email

    # ---------------- username ---------------- #
    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, value):
        if not isinstance(value, str):
            raise TypeError("Username must be a string")
        if not (2 <= len(value) <= 32):
            raise ValueError("Username length 2-32 chars")
        self.update_date = datetime.now()
        self.__username = value

    # ----------------- email ------------------ #
    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        if not isinstance(value, str):
            raise TypeError("Email must be a string")
        if "@" not in value or len(value) > 128:
            raise ValueError("Invalid email format / too long")
        self.update_date = datetime.now()
        self.__email = value

    # --------------- helpers ------------------ #
    def to_dict(self):
        return {
            "id": str(self.id),
            "creation_date": self.creation_date.isoformat(),
            "update_date": self.update_date.isoformat(),
            "username": self.username,
            "email": self.email,
        }

    def __repr__(self):
        return (
            f"User(username={self.username!r}, email={self.email!r}, id={self.id})"
        )

    __str__ = __repr__
