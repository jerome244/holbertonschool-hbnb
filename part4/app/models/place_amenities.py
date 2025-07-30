from app.database import db

place_amenities = db.Table(
    "place_amenities",
    db.Column("place_id", db.Integer, db.ForeignKey("places.id"), primary_key=True),
    db.Column(
        "amenity_id", db.Integer, db.ForeignKey("amenities.id"), primary_key=True
    ),
)
