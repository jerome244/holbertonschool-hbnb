from app.models.base import BaseModel
from app.database import db

class PlacePhoto(BaseModel):
    __tablename__ = "place_photos"

    # Column to store the URL of the photo (e.g., file path or URL)
    url = db.Column(db.String(256), nullable=False)

    # Foreign key linking this photo to a specific place
    place_id = db.Column(db.String(36), db.ForeignKey("places.id"), nullable=False)

    # Establish a relationship to the 'Place' model
    place = db.relationship("Place", back_populates="photos")
