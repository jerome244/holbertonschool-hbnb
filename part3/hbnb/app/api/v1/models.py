from flask_restx import fields
import re

# Shared email validation regex
EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

#----------- User models -----------#

def user_model(ns):
    return ns.model(
        "User",
        {
            "id": fields.String(readOnly=True, description="Unique user identifier (UUID)"),
            "first_name": fields.String(description="User's first name"),
            "last_name": fields.String(description="User's last name"),
            "email": fields.String(description="User's email address"),
            "is_admin": fields.Boolean(description="Flag indicating if the user has admin privileges"),
            # "is_host": fields.Boolean(default=False, description="Flag indicating to differentiate hosts and non hosts")
        }
    )

def user_create(ns):
    return ns.model(
        "UserCreate",
        {
            "first_name": fields.String(required=True, description="User's first name"),
            "last_name": fields.String(required=True, description="User's last name"),
            "email": fields.String(required=True, description="User's email address"),
            "password": fields.String(required=True, description="Min 8 characters"),
            "is_admin": fields.Boolean(description="Optional admin flag; honored for the very first signup, otherwise only by existing admins"),
        }
    )

def user_update(ns):
    return ns.model(
        "UserUpdate",
        {
            "first_name": fields.String(description="User's first name (optional)"),
            "last_name": fields.String(description="User's last name (optional)"),
            "is_admin": fields.Boolean(description="Admin flag; only considered if requester is admin"),
        }
    )

#----------- Amenity models -----------#

def amenity_model(ns):
    return ns.model(
        "Amenity",
        {
            "id": fields.String(readOnly=True, description="Unique amenity identifier (UUID)"),
            "name": fields.String(required=True, description="Name of the amenity"),
        },
    )

def amenity_input(ns):
    return ns.model(
        "AmenityInput",
        {
            "name": fields.String(required=True, description="Name of the amenity"),
        },
    )

#----------- Host models -----------#

def host_model(ns):
    return ns.model(
        "Host",
        {
            "id": fields.String(readOnly=True, description="Unique host identifier (UUID)"),
            "first_name": fields.String(required=True, description="Host's first name"),
            "last_name": fields.String(required=True, description="Host's last name"),
            "email": fields.String(required=True, description="Host's email address"),
            "is_admin": fields.Boolean(required=True, description="Flag indicating admin privileges"),
            "created_at": fields.DateTime(description="Timestamp when the host was created"),
            "updated_at": fields.DateTime(description="Timestamp when the host was last updated"),
        }
    )

def host_create(ns):
    return ns.model(
        "HostCreate",
        {
            "first_name": fields.String(required=True, description="Host's first name"),
            "last_name": fields.String(required=True, description="Host's last name"),
            "email": fields.String(required=True, description="Host's email address"),
            "password": fields.String(required=True, description="Min 8 characters"),
            "is_admin": fields.Boolean(description="Optional admin flag; honored for the very first signup, otherwise only by existing admins"),
        }
    )

def host_update(ns):
    return ns.model(
        "HostUpdate",
        {
            "first_name": fields.String(description="Host's first name (optional)"),
            "last_name": fields.String(description="Host's last name (optional)"),
            "is_admin": fields.Boolean(description="Admin flag; only considered if requester is admin"),
        }
    )
