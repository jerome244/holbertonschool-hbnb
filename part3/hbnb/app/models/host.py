from app.models.user import User
from app.database import db
from werkzeug.security import generate_password_hash, check_password_hash

class Host(User):
    __tablename__ = 'hosts'

    id = db.Column(db.String(36), db.ForeignKey('users.id'), primary_key=True)

    # --- Relationships ---
    places = db.relationship(
        "Place",
        back_populates="host",
        lazy=True,
        cascade="all, delete-orphan",
        foreign_keys='Place.host_id'
    )

    # --- Password utils ---
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # --- Serialization ---
    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
