from flask import request
from flask_restx import Namespace, Resource, fields
from datetime import datetime, timedelta, date
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

ns = Namespace("bookings", description="Booking management", security="BearerAuth")

booking_input = ns.model(
    "BookingInput",
    {
        "place_id": fields.String(required=True, description="ID of the place to book"),
        "check_in": fields.String(
            required=True,
            description="Check-in date (YYYY-MM-DD)",
            example="2025-07-01",
        ),
        "nights": fields.Integer(
            required=True, description="Number of nights to stay", example=3
        ),
        "guest_count": fields.Integer(
            description="Number of guests", default=1, example=2
        ),
    },
)

booking_output = ns.model(
    "Booking",
    {
        "id": fields.String(description="Booking unique identifier (UUID)"),
        "user_id": fields.String(description="UUID of the user who made the booking"),
        "place_id": fields.String(description="ID of the booked place"),
        "start_date": fields.Date(description="Check-in date"),
        "end_date": fields.Date(description="Check-out date"),
        "guest_count": fields.Integer(description="Number of guests"),
        "total_price": fields.Float(description="Total price for the stay"),
    },
)


rating_output = ns.model(
    "BookingRating",
    {
        "booking_id": fields.String(description="Booking ID for which rating applies"),
        "rating": fields.Float(description="User-provided rating for the booking"),
    },
)


@ns.route("")
class Bookings(Resource):
    @jwt_required()
    @ns.marshal_list_with(booking_output)
    def get(self):
        current_user = get_jwt_identity()
        claims = get_jwt()

        if claims.get("is_admin"):
            bookings = facade.list_bookings()
        else:
            bookings = facade.get_user_bookings(current_user)

        result = []
        for booking in bookings:
            result.append(
                {
                    "id": booking.id,
                    "user_id": booking.user.id,
                    "place_id": booking.place.id,
                    "start_date": booking.start_date,
                    "end_date": booking.end_date,
                    "guest_count": booking.guest_count,
                    "total_price": booking.total_price,
                }
            )
        return result, 200

    @jwt_required()
    @ns.expect(booking_input, validate=True)
    @ns.marshal_with(booking_output, code=201)
    def post(self):
        payload = request.json or {}
        user_id = get_jwt_identity()

        try:
            start_date = datetime.strptime(payload["check_in"], "%Y-%m-%d").date()
        except Exception:
            ns.abort(400, "Invalid or missing 'check_in'. Format must be YYYY-MM-DD.")

        nights = int(payload.get("nights", 1))
        if nights <= 0:
            ns.abort(400, "'nights' must be a positive integer")

        end_date = start_date + timedelta(days=nights)

        guest_count = int(payload.get("guest_count", 1))
        if guest_count <= 0:
            ns.abort(400, "'guest_count' must be at least 1")

        data = {
            "user_id": user_id,
            "place_id": payload["place_id"],
            "start_date": start_date,
            "end_date": end_date,
            "guest_count": guest_count,
        }

        booking = facade.create_booking(data)
        if not booking:
            ns.abort(400, "Cannot create booking: conflict or invalid data.")

        return {
            "id": booking.id,
            "user_id": booking.user.id,
            "place_id": booking.place.id,
            "start_date": booking.start_date,
            "end_date": booking.end_date,
            "guest_count": booking.guest_count,
            "total_price": booking.total_price,
        }, 201


@ns.route("/<string:booking_id>")
@ns.response(404, "Booking not found")
class BookingResource(Resource):
    @jwt_required()
    @ns.doc(
        "get_booking", description="Retrieve a specific booking", security="BearerAuth"
    )
    @ns.marshal_with(booking_output)
    @ns.response(403, "Unauthorized action")
    def get(self, booking_id):
        booking = facade.get_booking(booking_id)
        if not booking:
            ns.abort(404, f"Booking {booking_id} not found")
        user_id = get_jwt_identity()
        claims = get_jwt()
        if str(booking.user.id) != str(user_id) and not claims.get("is_admin", False):
            ns.abort(403, "Unauthorized action")

        return {
            "id": booking.id,
            "user_id": booking.user.id,
            "place_id": booking.place.id,
            "start_date": booking.start_date,
            "end_date": booking.end_date,
            "guest_count": booking.guest_count,
            "total_price": booking.total_price,
        }, 200

    @jwt_required()
    @ns.doc(
        "replace_booking",
        description="Replace an existing booking (Owner or Admin only)",
        security="BearerAuth",
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
        security="BearerAuth",
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
        security="BearerAuth",
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
