"""
base.py: Defines the BaseModel with UUID and timestamp management.

This module provides the BaseModel class, which supplies all models with
a unique identifier, creation timestamp, update timestamp, and a dictionary
serialization method.
"""

import uuid
from datetime import datetime
from app.database import db


class BaseModel(db.Model):
    """
    Base class for all models providing ID and timestamp fields.

    Attributes:
        __id (str): Unique identifier for the instance.
        __created_at (datetime): Timestamp when the instance was created.
        __updated_at (datetime): Timestamp when the instance was last updated.
    """

    __abstract__ = True  # Prevent SQLAlchemy from creating a table for BaseModel

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
