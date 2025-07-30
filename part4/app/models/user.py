from flask_login import UserMixin
from app.models.base import BaseModel
from app.database import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid  # Import UUID module

class User(UserMixin, BaseModel):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # Store UUID as string
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    pseudo = db.Column(db.String(128), unique=True, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    bio = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(256), nullable=True)

    type = db.Column(db.String(50))  # 'user' or 'host'
    __mapper_args__ = {"polymorphic_identity": "user", "polymorphic_on": type}

    bookings = db.relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    reviews = db.relationship("Review", back_populates="user", cascade="all, delete-orphan")
    
    # Add the places relationship
    places = db.relationship("Place", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def verify_password(self, password):
        return self.check_password(password)

    def leave_review(self, booking, text, rating):
        """
        Create a review for a booking made by the user.
        """
        from app.models.review import Review

        review = Review(
            user=self, 
            place=booking.place, 
            booking=booking, 
            text=text, 
            rating=rating
        )

        db.session.add(review)
        self.reviews.append(review)  # Associate the review with the user
        db.session.commit()

        return review  # Return the created review object

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
