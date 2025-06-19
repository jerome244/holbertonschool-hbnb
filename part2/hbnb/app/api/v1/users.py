import re
from flask_restx import Namespace, Resource, fields
from app import facade
from app.api.v1.bookings import booking_output as booking_model

ns = Namespace("users", description="Operations on user accounts")

# Full model: used for GET responses and POST/PUT bodies
user_model = ns.model(
    "User",
    {
        "id": fields.String(readonly=True, description="Unique ID"),
        "first_name": fields.String(required=True, description="First name"),
        "last_name": fields.String(required=True, description="Last name"),
        "email": fields.String(required=True, description="Email address"),
        "is_admin": fields.Boolean(description="Admin flag"),
    },
)

# Partial model: used for PATCH bodies (all fields optional)
patch_user_model = ns.model(
    "UserPatch",
    {
        "first_name": fields.String(description="First name"),
        "last_name": fields.String(description="Last name"),
        "email": fields.String(description="Email address"),
        "is_admin": fields.Boolean(description="Admin flag"),
    },
)

# Output model for average booking rating per user
avg_rating_output = ns.model(
    "UserBookingAverageRating",
    {
        "user_id": fields.String(readonly=True, description="User UUID"),
        "average_rating": fields.Float(
            readonly=True, description="Average rating across all bookings"
        ),
    },
)

EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


@ns.route("/")
class UserList(Resource):
    @ns.marshal_list_with(user_model)
    def get(self):
        """List all users"""
        return facade.list_users()

    @ns.expect(user_model, validate=True)
    @ns.marshal_with(user_model, code=201)
    def post(self):
        """Create a new user"""
        payload = ns.payload
        email = payload.get("email", "").strip()

        if not EMAIL_RE.match(email):
            ns.abort(400, "Invalid email address")

        if any(u.email.lower() == email.lower() for u in facade.list_users()):
            ns.abort(400, "Email already in use")

        return facade.create_user(payload), 201


@ns.route("/<string:user_id>")
@ns.response(404, "User not found")
class UserDetail(Resource):
    @ns.marshal_with(user_model)
    def get(self, user_id):
        """Fetch a user by ID"""
        user = facade.get_user(user_id)
        if not user:
            ns.abort(404, f"User {user_id} doesn't exist")
        return user

    @ns.expect(patch_user_model, validate=True)
    @ns.marshal_with(user_model)
    def patch(self, user_id):
        """Partially update an existing user"""
        payload = ns.payload
        user = facade.get_user(user_id)
        if not user:
            ns.abort(404, f"User {user_id} doesn't exist")

        if "email" in payload:
            email = payload["email"].strip()
            if not EMAIL_RE.match(email):
                ns.abort(400, "Invalid email address")
            if any(
                u.email.lower() == email.lower() and u.id != user_id
                for u in facade.list_users()
            ):
                ns.abort(400, "Email already in use")

        return facade.update_user(user_id, payload)

    @ns.response(204, "User deleted")
    def delete(self, user_id):
        """Delete a user"""
        if not facade.get_user(user_id):
            ns.abort(404, f"User {user_id} doesn't exist")
        facade.delete_user(user_id)
        return "", 204


# --- New endpoint: list bookings owned by a user ---
@ns.route("/<string:user_id>/bookings")
@ns.response(404, "User not found")
class UserBookings(Resource):
    @ns.marshal_list_with(booking_model)
    def get(self, user_id):
        """List all bookings for a given user"""
        if not facade.get_user(user_id):
            ns.abort(404, f"User {user_id} doesn't exist")

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


# --- New endpoint: average rating across a user’s bookings ---
@ns.route("/<string:user_id>/bookings/rating")
@ns.response(404, "User not found or no ratings available")
class UserBookingsAverageRating(Resource):
    @ns.marshal_with(avg_rating_output)
    def get(self, user_id):
        """Get the average rating across all bookings for a given user"""
        user = facade.get_user(user_id)
        if not user:
            ns.abort(404, f"User {user_id} not found")

        bookings = facade.get_user_bookings(user_id) or []
        ratings = []
        for b in bookings:
            review = getattr(b, "review", None)
            if review and hasattr(review, "rating"):
                try:
                    ratings.append(float(review.rating))
                except (ValueError, TypeError):
                    continue

        if not ratings:
            ns.abort(404, f"No ratings found for user {user_id}")

        average = sum(ratings) / len(ratings)
        return {"user_id": user_id, "average_rating": average}
