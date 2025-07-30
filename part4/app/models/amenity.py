from app.models.base import BaseModel
from app.database import db
from app.models.place_amenities import place_amenities


class Amenity(BaseModel):
    __tablename__ = "amenities"

    # --- Columns ---
    name = db.Column(db.String(128), nullable=False)

    # --- Many-to-Many with Place ---
    places = db.relationship(
        "Place", secondary=place_amenities, lazy="subquery", back_populates="amenities"
    )
