from datetime import datetime
from .base import BaseModel


class User(BaseModel):
    """
    User – represents a system user.

    Args
    ----
    username : str
    email : str
    first_name : str, optional
    last_name : str, optional
    phone_number : str, optional
    **kwargs : dict
        Optional keys passed to BaseModel (id, creation_date, update_date)
    """

    # -------------------- constructor -------------------- #
    def __init__(
        self,
        username: str,
        email: str,
        first_name: str | None = None,
        last_name: str | None = None,
        phone_number: str | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)          # id / timestamps
        self.__username = username
        self.__email = email
        self.__first_name = first_name
        self.__last_name = last_name
        self.__phone_number = phone_number

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

    # -------------- first_name ---------------- #
    @property
    def first_name(self):
        return self.__first_name

    @first_name.setter
    def first_name(self, value):
        if value is not None and not isinstance(value, str):
            raise TypeError("first_name must be a string or None")
        self.update_date = datetime.now()
        self.__first_name = value

    # -------------- last_name ----------------- #
    @property
    def last_name(self):
        return self.__last_name

    @last_name.setter
    def last_name(self, value):
        if value is not None and not isinstance(value, str):
            raise TypeError("last_name must be a string or None")
        self.update_date = datetime.now()
        self.__last_name = value

    # ------------ phone_number ---------------- #
    @property
    def phone_number(self):
        return self.__phone_number

    @phone_number.setter
    def phone_number(self, value):
        if value is not None and not isinstance(value, str):
            raise TypeError("phone_number must be a string or None")
        if value and len(value) > 32:
            raise ValueError("phone_number must be ≤ 32 characters")
        self.update_date = datetime.now()
        self.__phone_number = value

    # --------------- helpers ------------------ #
    def to_dict(self):
        return {
            "id": str(self.id),
            "creation_date": self.creation_date.isoformat(),
            "update_date": self.update_date.isoformat(),
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
        }

    def __repr__(self):
        return (
            f"User(username={self.username!r}, email={self.email!r}, "
            f"first_name={self.first_name!r}, last_name={self.last_name!r}, "
            f"phone_number={self.phone_number!r}, id={self.id})"
        )

    __str__ = __repr__
