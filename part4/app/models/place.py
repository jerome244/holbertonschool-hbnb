from app.models.base import BaseModel
from app.database import db
from .amenity import place_amenities
import uuid

class Place(BaseModel):
    __tablename__ = "places"

    # Place fields
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(128), nullable=True)
    city = db.Column(db.String(64), nullable=True)

    # Foreign keys
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    host_id = db.Column(db.String(36), db.ForeignKey("hosts.id"), nullable=True)

    # Relationships
    user = db.relationship("User", backref="owned_places", foreign_keys=[user_id])
    host = db.relationship("Host", back_populates="places", foreign_keys=[host_id])
    bookings = db.relationship(
        "Booking", back_populates="place", cascade="all, delete-orphan", lazy=True
    )
    reviews = db.relationship(
        "Review", back_populates="place", cascade="all, delete-orphan"
    )

    amenities = db.relationship(
        "Amenity", secondary=place_amenities, lazy="subquery", back_populates="places"
    )

    photos = db.relationship(
        "PlacePhoto", back_populates="place", cascade="all, delete-orphan", lazy=True
    )

    # New field for counting views
    views = db.Column(db.Integer, default=0, nullable=False)

    # Method to add a photo to this place
    def add_photo(self, url):
        new_photo = PlacePhoto(url=url, place_id=self.id)
        db.session.add(new_photo)
        db.session.commit()
        return new_photo

    # Method to remove a photo from this place
    def remove_photo(self, photo_id):
        photo_to_remove = PlacePhoto.query.get(photo_id)
        if photo_to_remove:
            db.session.delete(photo_to_remove)
            db.session.commit()

    # Method to increment view count for the place
    def increment_views(self, user=None):
        # Only increment views if the user is not the owner
        if user and user.id != self.host_id:
            self.views += 1
            db.session.commit()

    # Serialize the Place object, including photos
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "price": self.price,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "photos": [photo.url for photo in self.photos],  # List of photo URLs
            "address": self.address,
            "city": self.city,
            "views": self.views  # Include views in the serialized data
        }
