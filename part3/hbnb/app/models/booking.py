from app.models.base import BaseModel
from app.database import db

class Booking(BaseModel):
    __tablename__ = 'bookings'

    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    place_id = db.Column(db.String(36), db.ForeignKey('places.id'), nullable=False)

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    guest_count = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', back_populates='bookings')
    place = db.relationship('Place', back_populates='bookings')
