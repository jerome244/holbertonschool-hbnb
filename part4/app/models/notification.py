from app.database import db
from datetime import datetime


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(
        db.String(36), nullable=False
    )  # Generic user ID (host or guest)
    recipient_type = db.Column(db.String(20), nullable=False)  # 'host' or 'guest'
    message = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50), default="unread")  # 'unread' or 'read'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(
        self, recipient_id, recipient_type, message, status="unread", timestamp=None
    ):
        self.recipient_id = recipient_id
        self.recipient_type = recipient_type
        self.message = message
        self.status = status
        self.timestamp = timestamp or datetime.utcnow()
