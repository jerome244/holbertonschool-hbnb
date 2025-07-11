from app.models.base import BaseModel
from app.database import db

from .amenity import place_amenities

class Place(BaseModel):
    __tablename__ = 'places'

    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    # Foreign keys
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    host_id = db.Column(db.String(36), db.ForeignKey('hosts.id'), nullable=True)

    # Relationships
    host = db.relationship('Host', back_populates='places', foreign_keys=[host_id])
    bookings = db.relationship(
        'Booking',
        back_populates='place',
        cascade='all, delete-orphan',
        lazy=True
    )
    reviews = db.relationship(
        'Review',
        back_populates='place',
        cascade='all, delete-orphan'
    )

    amenities = db.relationship(
        'Amenity',
        secondary=place_amenities,
        lazy='subquery',
        back_populates='places'
    )

    def add_amenity(self, amenity):
        self.amenities.append(amenity)
