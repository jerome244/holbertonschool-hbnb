from app.models.base import BaseModel
from app.database import db

class Review(BaseModel):
    __tablename__ = 'reviews'

    text = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=True)
    rating = db.Column(db.Integer, nullable=True)

    user = db.relationship("User", back_populates="reviews")
    place = db.relationship("Place", back_populates="reviews")
    booking = db.relationship("Booking", backref="review")
