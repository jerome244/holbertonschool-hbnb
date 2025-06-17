# app/models/user.py
import re
import uuid
from datetime import datetime

class User:
    EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

    def __init__(self, first_name: str, last_name: str, email: str, is_admin: bool = False):
        # Validation
        if not first_name or len(first_name) > 50:
            raise ValueError("first_name is required (max 50 chars)")
        if not last_name or len(last_name) > 50:
            raise ValueError("last_name is required (max 50 chars)")
        if not email or not User.EMAIL_REGEX.match(email):
            raise ValueError("email is required and must be a valid address")

        # Attributes
        self.id = str(uuid.uuid4())
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin

        # Timestamps
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self):
        self.updated_at = datetime.now()

    def update(self, data: dict):
        for k, v in data.items():
            if hasattr(self, k):
                setattr(self, k, v)
        self.save()

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
