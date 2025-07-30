from app.database import db
import uuid
from datetime import datetime

class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    place_id = db.Column(db.String(36), db.ForeignKey("places.id"), nullable=False)
    host_id = db.Column(db.String(36), db.ForeignKey("hosts.id"), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    guest_count = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    status = db.Column(db.String(20), nullable=False, default="pending")

    user = db.relationship("User", back_populates="bookings")
    place = db.relationship("Place", back_populates="bookings")
    host = db.relationship("Host", back_populates="bookings", foreign_keys=[host_id])

    def __init__(self, user_id, place_id, host_id, start_date, end_date, total_price, guest_count, status="pending"):
        self.user_id = user_id
        self.place_id = place_id
        self.host_id = host_id
        self.start_date = start_date
        self.end_date = end_date
        self.total_price = total_price
        self.guest_count = guest_count
        self.status = status  # Optional, defaults to "pending"
