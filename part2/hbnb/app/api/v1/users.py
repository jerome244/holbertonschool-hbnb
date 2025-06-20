"""
users.py: Flask-RESTX API endpoints for User resources.

This module defines a namespace and models for users, including:
- Listing users
- Creating users (with optional is_admin flag)
- Retrieving, replacing, and deleting a single user by ID
- Listing a user's bookings and computing average booking ratings

Swagger UI will show parameter descriptions and response models based on these definitions.
"""
from flask_restx import Namespace, Resource, fields
import re
from app import facade
from app.api.v1.bookings import booking_output as booking_model

# ----------------------- namespace ----------------------- #
ns = Namespace(
    "users",
    description="Operations on user accounts"
)

# ----------------------- data models ----------------------- #
# Output model for a User resource
user_model = ns.model(
    "User",
    {
        "id": fields.String(
            readonly=True,
            description="Unique user identifier (UUID)"
        ),
        "first_name": fields.String(
            required=True,
            description="User's first name"
        ),
        "last_name": fields.String(
            required=True,
            description="User's last name"
        ),
        "email": fields.String(
            required=True,
            description="User's email address"
        ),
        "is_admin": fields.Boolean(
            required=True,
            description="Flag indicating if the user has admin privileges"
        ),
    }
)

# Input model for creating a new user (is_admin optional)
user_create = ns.model(
    "UserCreate",
    {
        "first_name": fields.String(
            required=True,
            description="User's first name"
        ),
        "last_name": fields.String(
            required=True,
            description="User's last name"
        ),
        "email": fields.String(
            required=True,
            description="User's email address"
        ),
        "is_admin": fields.Boolean(
            description="Optional admin flag; defaults to False if omitted"
        ),
    }
)

# Input model for full replacement of a user
user_input = ns.model(
    "UserInput",
    {
        "first_name": fields.String(
            required=True,
            description="User's first name"
        ),
        "last_name": fields.String(
            required=True,
            description="User's last name"
        ),
        "email": fields.String(
            required=True,
            description="User's email address"
        ),
        "is_admin": fields.Boolean(
            required=True,
            description="Admin flag; must be provided for full replace"
        ),
    }
)

# Output model for average booking rating per user
avg_rating_output = ns.model(
    "UserBookingAverageRating",
    {
        "user_id": fields.String(
            readonly=True,
            description="UUID of the user"
        ),
        "average_rating": fields.Float(
            readonly=True,
            description="Average rating across all of the user's bookings"
        ),
    }
)

EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

# ----------------------- resources ----------------------- #
@ns.route("/")
class UserList(Resource):
    @ns.doc("list_users")
    @ns.marshal_list_with(user_model)
    def get(self):
        """
        List all users.

        Returns a list of users with basic profile information.
        """
        return facade.list_users()

    @ns.doc("create_user")
    @ns.expect(user_create, validate=True)
    @ns.marshal_with(user_model, code=201)
    def post(self):
        """
        Create a new user.

        Validates email format and uniqueness. If `is_admin` is omitted, defaults to False.
        """
        data = ns.payload or {}
        email = data.get("email", "").strip()
        if not EMAIL_RE.match(email):
            ns.abort(400, "Invalid email address")
        if any(u.email.lower() == email.lower() for u in facade.list_users()):
            ns.abort(400, "Email already in use")
        data["email"] = email
        data.setdefault("is_admin", False)
        return facade.create_user(data), 201

@ns.route("/<string:user_id>")
@ns.response(404, "User not found")
class UserDetail(Resource):
    @ns.doc("get_user")
    @ns.marshal_with(user_model)
    def get(self, user_id):
        """
        Retrieve a user by ID.

        Returns the full user object if found.
        """
        user = facade.get_user(user_id)
        if not user:
            ns.abort(404, f"User {user_id} not found")
        return user

    @ns.doc("replace_user")
    @ns.expect(user_input, validate=True)
    @ns.marshal_with(user_model)
    def put(self, user_id):
        """
        Replace an existing user completely.

        All fields (`first_name`, `last_name`, `email`, `is_admin`) must be provided.
        Validates email format and uniqueness.
        """
        data = ns.payload or {}
        user = facade.get_user(user_id)
        if not user:
            ns.abort(404, f"User {user_id} not found")
        email = data.get("email", "").strip()
        if not EMAIL_RE.match(email):
            ns.abort(400, "Invalid email address")
        if any(u.email.lower() == email.lower() and u.id != user_id for u in facade.list_users()):
            ns.abort(400, "Email already in use")
        data["email"] = email
        required = {"first_name", "last_name", "email", "is_admin"}
        missing = required - set(data.keys())
        if missing:
            ns.abort(400, f"Missing fields for full update: {', '.join(sorted(missing))}")
        return facade.update_user(user_id, data), 200

    @ns.doc("delete_user")
    @ns.response(204, "User deleted")
    def delete(self, user_id):
        """
        Delete a user by ID.

        Returns HTTP 204 on successful deletion.
        """
        if not facade.get_user(user_id):
            ns.abort(404, f"User {user_id} not found")
        facade.delete_user(user_id)
        return "", 204

@ns.route("/<string:user_id>/bookings")
@ns.response(404, "User not found")
class UserBookings(Resource):
    @ns.doc("list_user_bookings")
    @ns.marshal_list_with(booking_model)
    def get(self, user_id):
        """
        List all bookings for a specific user.

        Returns booking summaries including total price and checkout date.
        """
        if not facade.get_user(user_id):
            ns.abort(404, f"User {user_id} not found")
        bookings = facade.get_user_bookings(user_id) or []
        return [
            {
                "id": b.id,
                "user_id": b.user.id,
                "place_id": b.place.id,
                "guest_count": b.guest_count,
                "checkin_date": b.checkin_date.date(),
                "night_count": b.night_count,
                "total_price": b.place.price * b.night_count * b.guest_count,
                "checkout_date": b.checkout_date.date(),
            }
            for b in bookings
        ]

@ns.route("/<string:user_id>/bookings/rating")
@ns.response(404, "User not found or no ratings available")
class UserBookingsAverageRating(Resource):
    @ns.doc("get_user_average_booking_rating")
    @ns.marshal_with(avg_rating_output)
    def get(self, user_id):
        """
        Get the average rating across all bookings of a user.

        Calculates the mean of all existing booking ratings.
        """
        user = facade.get_user(user_id)
        if not user:
            ns.abort(404, f"User {user_id} not found")
        bookings = facade.get_user_bookings(user_id) or []
        ratings = [float(r.review.rating) for r in bookings if getattr(r, "review", None)]
        if not ratings:
            ns.abort(404, f"No ratings found for user {user_id}")
        return {"user_id": user_id, "average_rating": sum(ratings) / len(ratings)}
