from flask import request
from flask_restx import Namespace, Resource, fields, marshal
from datetime import datetime, timedelta, date
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

ns = Namespace(
    "bookings",
    description="Booking management",
    security='BearerAuth'
)

# ----------------------- data models ----------------------- #
booking_input = ns.model(
    "BookingInput",
    {
        "place_id": fields.String(required=True, description="ID of the place to book"),
        "check_in": fields.String(required=True, description="Check-in date (YYYY-MM-DD)", example="2025-07-01"),
        "nights": fields.Integer(required=True, description="Number of nights to stay", example=3),
        "guest_count": fields.Integer(description="Number of guests", default=1, example=2),
    }
)

booking_output = ns.model(
    "Booking",
    {
        "id": fields.String(description="Booking unique identifier (UUID)"),
        "user_id": fields.String(description="UUID of the user who made the booking"),
        "place_id": fields.String(description="ID of the booked place"),
        "check_in": fields.Date(description="Check-in date"),
        "nights": fields.Integer(description="Number of nights"),
        "guest_count": fields.Integer(description="Number of guests"),
        "check_out": fields.Date(description="Calculated check-out date"),
        "total_price": fields.Float(description="Total price for the stay"),
    }
)

rating_output = ns.model(
    "BookingRating",
    {
        "booking_id": fields.String(description="Booking ID for which rating applies"),
        "rating": fields.Float(description="User-provided rating for the booking"),
    }
)

@ns.route("")
class Bookings(Resource):
    @jwt_required()
    @ns.doc(
        "list_bookings",
        description="List all bookings (Admin only)",
        security='BearerAuth'
    )
    @ns.marshal_list_with(booking_output)
    @ns.response(403, "Unauthorized action")
    def get(self):
        """
        Retrieve a list of all bookings. Only accessible by administrators.
        """
        claims = get_jwt()
        if not claims.get("is_admin"):
            ns.abort(403, "Unauthorized action")

        bookings = facade.get_all_bookings()
        result = []
        for b in bookings:
            check_out = b.checkin_date + timedelta(days=b.night_count)
            total = b.place.price * b.night_count
            result.append({
                "id": b.id,
                "user_id": b.user.id,
                "place_id": b.place.id,
                "check_in": b.checkin_date,
                "nights": b.night_count,
                "guest_count": b.guest_count,
                "check_out": check_out,
                "total_price": total,
            })
        return result, 200

    @jwt_required()
    @ns.doc(
        "create_booking",
        description="Create a new booking (Authenticated users)",
        security='BearerAuth'
    )
    @ns.expect(booking_input, validate=True)
    @ns.marshal_with(booking_output, code=201)
    @ns.response(400, "Invalid input or booking conflict")
    def post(self):
        """
        Create a new booking for the authenticated user. Validates dates and place availability.
        """
        payload = request.json or {}
        user_id = get_jwt_identity()

        # Required fields
        for field in ("place_id", "check_in", "nights"):
            if field not in payload:
                ns.abort(400, f"Missing required field: {field}")

        # Parse and validate check_in date
        try:
            checkin_date = datetime.strptime(payload.get("check_in"), "%Y-%m-%d")
        except Exception:
            ns.abort(400, "Invalid or missing 'check_in'. Format must be YYYY-MM-DD.")
        if checkin_date.date() < date.today():
            ns.abort(400, "Check-in date cannot be in the past.")

        # Validate nights
        try:
            nights = int(payload.get("nights"))
        except Exception:
            ns.abort(400, "'nights' must be an integer.")
        if nights <= 0:
            ns.abort(400, "Number of nights must be at least 1.")

        # Guest count
        guest_count = payload.get("guest_count", 1)
        try:
            guest_count = int(guest_count)
        except Exception:
            ns.abort(400, "'guest_count' must be an integer.")
        if guest_count <= 0:
            ns.abort(400, "Guest count must be at least 1.")

        # Validate place
        place = facade.get_place(payload.get("place_id"))
        if not place:
            ns.abort(400, "Place not found.")

        # Build data for facade
        data = {
            "user_id": user_id,
            "place_id": payload.get("place_id"),
            "place": place,
            "checkin_date": checkin_date,
            "night_count": nights,
            "guest_count": guest_count,
        }

        # Create booking
        booking = facade.create_booking(data)
        if not booking:
            ns.abort(400, "Cannot create booking: conflict or invalid data.")

        check_out = booking.checkin_date + timedelta(days=booking.night_count)
        total = booking.place.price * booking.night_count
        return {
            "id": booking.id,
            "user_id": booking.user.id,
            "place_id": booking.place.id,
            "check_in": booking.checkin_date,
            "nights": booking.night_count,
            "guest_count": booking.guest_count,
            "check_out": check_out,
            "total_price": total,
        }, 201

@ns.route("/<string:booking_id>")
@ns.response(404, "Booking not found")
class BookingResource(Resource):
    @jwt_required()
    @ns.doc(
        "get_booking",
        description="Get booking details (Owner or Admin only)",
        security='BearerAuth'
    )
    @ns.marshal_with(booking_output)
    @ns.response(403, "Unauthorized action")
    def get(self, booking_id):
        """
        Retrieve details for a specific booking. Users may fetch their own bookings; admins may fetch any.
        """
        booking = facade.get_booking(booking_id)
        if not booking:
            ns.abort(404, f"Booking {booking_id} not found")
        user_id = get_jwt_identity()
        claims = get_jwt()
        if booking.user.id != user_id and not claims.get("is_admin"):
            ns.abort(403, "Unauthorized action")

        check_out = booking.checkin_date + timedelta(days=booking.night_count)
        total = booking.place.price * booking.night_count
        return {
            "id": booking.id,
            "user_id": booking.user.id,
            "place_id": booking.place.id,
            "check_in": booking.checkin_date,
            "nights": booking.night_count,
            "guest_count": booking.guest_count,
            "check_out": check_out,
            "total_price": total,
        }, 200

    @jwt_required()
    @ns.doc(
        "replace_booking",
        description="Replace an existing booking (Owner or Admin only)",
        security='BearerAuth'
    )
    @ns.expect(booking_input, validate=True)
    @ns.marshal_with(booking_output)
    @ns.response(403, "Unauthorized action")
    def put(self, booking_id):
        """
        Overwrite an existing booking. Owners may update their own bookings; admins may update any.
        Validates input and business rules.
        """
        booking = facade.get_booking(booking_id)
        if not booking:
            ns.abort(404, f"Booking {booking_id} not found")
        user_id = get_jwt_identity()
        claims = get_jwt()
        if booking.user.id != user_id and not claims.get("is_admin"):
            ns.abort(403, "Unauthorized action")

        payload = request.json or {}
        for field in ("place_id", "check_in", "nights"):
            if field not in payload:
                ns.abort(400, f"Missing required field: {field}")
        try:
            checkin_date = datetime.strptime(payload.get("check_in"), "%Y-%m-%d")
        except Exception:
            ns.abort(400, "Invalid or missing 'check_in'. Format must be YYYY-MM-DD.")
        if checkin_date.date() < date.today():
            ns.abort(400, "Check-in date cannot be in the past.")
        try:
            nights = int(payload.get("nights"))
        except Exception:
            ns.abort(400, "'nights' must be an integer.")
        if nights <= 0:
            ns.abort(400, "Number of nights must be at least 1.")
        try:
            guest_count = int(payload.get("guest_count", booking.guest_count))
        except Exception:
            ns.abort(400, "'guest_count' must be an integer.")
        if guest_count <= 0:
            ns.abort(400, "Guest count must be at least 1.")
        place = facade.get_place(payload.get("place_id"))
        if not place:
            ns.abort(400, "Place not found.")

        data = {
            "place": place,
            "checkin_date": checkin_date,
            "night_count": nights,
            "guest_count": guest_count,
        }

        updated = facade.update_booking(booking_id, data)
        if not updated:
            ns.abort(400, "Cannot update booking: conflict or invalid data.")

        check_out = updated.checkin_date + timedelta(days=updated.night_count)
        total = updated.place.price * updated.night_count
        return {
            "id": updated.id,
            "user_id": updated.user.id,
            "place_id": updated.place.id,
            "check_in": updated.checkin_date,
            "nights": updated.night_count,
            "guest_count": updated.guest_count,
            "check_out": check_out,
            "total_price": total,
        }, 200

    @jwt_required()
    @ns.doc(
        "delete_booking",
        description="Delete a booking by its ID (Owner or Admin only)",
        security='BearerAuth'
    )
    @ns.response(204, "Booking deleted")
    @ns.response(403, "Unauthorized action")
    def delete(self, booking_id):
        """
        Remove a booking. Users may delete their own bookings; admins may delete any.
        """
        booking = facade.get_booking(booking_id)
        if not booking:
            ns.abort(404, f"Booking {booking_id} not found")
        user_id = get_jwt_identity()
        claims = get_jwt()
        if booking.user.id != user_id and not claims.get("is_admin"):
            ns.abort(403, "Unauthorized action")
        facade.delete_booking(booking_id)
        return "", 204

@ns.route("/<string:booking_id>/rating")
class BookingRating(Resource):
    @jwt_required()
    @ns.doc(
        "get_booking_rating",
        description="Fetch the user's rating for a booking (Owner only)",
        security='BearerAuth'
    )
    @ns.response(404, "Booking or rating not found")
    @ns.response(403, "Unauthorized action")
    @ns.marshal_with(rating_output)
    def get(self, booking_id):
        """
        Retrieve the review rating for a given booking. Only the booking owner can access.
        """
        booking = facade.get_booking(booking_id)
        if not booking:
            ns.abort(404, f"Booking {booking_id} not found")
        user_id = get_jwt_identity()
        if booking.user.id != user_id:
            ns.abort(403, "Unauthorized action")
        if not getattr(booking, "review", None) or booking.review.rating is None:
            ns.abort(404, f"No rating found for booking {booking_id}")
        return {"booking_id": booking_id, "rating": float(booking.review.rating)}
