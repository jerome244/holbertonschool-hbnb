from app.models.user import User
from app.database import db
from werkzeug.security import generate_password_hash, check_password_hash


class Host(User):
    __tablename__ = "hosts"

    # ForeignKey linking Host to User
    id = db.Column(db.String(36), db.ForeignKey("users.id"), primary_key=True)

    # Polymorphic identity to distinguish this model from others (e.g., User vs Host)
    __mapper_args__ = {
        "polymorphic_identity": "host",  # Identity that Flask-SQLAlchemy uses to differentiate between 'user' and 'host'
    }

    # Relationships
    places = db.relationship(
        "Place",
        back_populates="host",  # Assuming "Place" model has a relationship defined with the Host model
        lazy=True,  # Load the related places lazily (load them only when requested)
        cascade="all, delete-orphan",  # Automatically delete orphaned places
        foreign_keys="Place.host_id",  # Ensure that the foreign key to the host is used
    )

    # Password utilities
    def set_password(self, password):
        """Set password for the host."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the given password matches the stored hashed password."""
        return check_password_hash(self.password, password)

    # Serialization method to convert object into a dictionary for easy use in APIs or responses
    def to_dict(self):
        """Convert the Host object into a dictionary."""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
