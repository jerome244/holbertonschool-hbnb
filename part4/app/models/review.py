import uuid
from app.database import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    text = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    place_id = db.Column(db.String(36), db.ForeignKey("places.id"), nullable=False)
    booking_id = db.Column(db.String(36), db.ForeignKey("bookings.id"), nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    reported = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Ensure created_at is set properly

    user = db.relationship("User", back_populates="reviews")
    place = db.relationship("Place", back_populates="reviews")
    booking = db.relationship("Booking", backref="review")

    def __repr__(self):
        return f'<Review {self.text}>'
