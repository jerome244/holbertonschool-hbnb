# app/api/v1/bookings.py

from flask import request
from flask_restx import Namespace, Resource, fields
from datetime import datetime, timedelta, date
from app import facade

ns = Namespace('bookings', description='Booking management')

# 1) Input model for POST (all fields required)
booking_input = ns.model('BookingInput', {
    'user_id':      fields.String(required=True, description='UUID of the user'),
    'place_id':     fields.String(required=True, description='UUID of the place'),
    'guest_count':  fields.Integer(required=True, description='Number of guests'),
    'checkin_date': fields.Date(required=True, description='Date in YYYY-MM-DD format'),
    'night_count':  fields.Integer(required=True, description='Number of nights'),
})

# 1b) Patch model (all fields optional)
booking_patch = ns.model('BookingPatch', {
    'user_id':      fields.String(description='UUID of the user'),
    'place_id':     fields.String(description='UUID of the place'),
    'guest_count':  fields.Integer(description='Number of guests'),
    'checkin_date': fields.Date(description='Date in YYYY-MM-DD format'),
    'night_count':  fields.Integer(description='Number of nights'),
})

# 2) Output model with ordered fields
booking_output = ns.inherit('Booking', booking_input, {
    'id':            fields.String(readOnly=True, description='Booking UUID'),
    'total_price':   fields.Float(readOnly=True, description='Computed total price'),
    'checkout_date': fields.Date(readOnly=True, description='Computed check-out date'),
})

# 3) Output model for booking rating
rating_output = ns.model('BookingRating', {
    'booking_id': fields.String(readOnly=True, description='Booking UUID'),
    'rating':     fields.Float(readOnly=True, description='Rating for this booking'),
})

@ns.route('/')
class BookingList(Resource):
    @ns.marshal_list_with(booking_output)
    def get(self):
        """List all bookings"""
        bookings = facade.list_bookings()
        return [
            {
                'id':            b.id,
                'user_id':       b.user.id,
                'place_id':      b.place.id,
                'guest_count':   b.guest_count,
                'checkin_date':  b.checkin_date.date(),
                'night_count':   b.night_count,
                'total_price':   b.place.price * b.night_count * b.guest_count,
                'checkout_date': b.checkout_date.date(),
            }
            for b in bookings
        ]

    @ns.expect(booking_input, validate=True)
    @ns.marshal_with(booking_output, code=201)
    def post(self):
        """Create a new booking"""
        data = request.json

        # Validate user
        user = facade.get_user(data.get('user_id'))
        if not user:
            ns.abort(400, "User not found")

        # Validate numeric bounds
        if data.get('guest_count', 0) <= 0:
            ns.abort(400, "Guest count must be greater than 0")
        if data.get('night_count', 0) <= 0:
            ns.abort(400, "Night count must be greater than 0")

        # Parse check-in date
        try:
            checkin_str = data.get('checkin_date')
            checkin_date = date.fromisoformat(checkin_str)
        except ValueError:
            ns.abort(400, 'Invalid checkin_date, must be YYYY-MM-DD')
        except Exception:
            ns.abort(400, 'Invalid checkin_date format, expected YYYY-MM-DD')

        # Reject if check-in is today or past
        if checkin_date <= date.today():
            ns.abort(400, "Checkin_date must be later than today")

        # Validate place and capacity
        place = facade.get_place(data.get('place_id'))
        if not place:
            ns.abort(400, "Place not found")
        if data['guest_count'] > place.capacity:
            ns.abort(400, f"Guest count exceeds place capacity ({place.capacity})")

        # Check for overlap
        start_dt = datetime.combine(checkin_date, datetime.min.time())
        requested_checkout = start_dt + timedelta(days=data['night_count'])
        for existing in facade.list_bookings():
            if existing.place.id != place.id:
                continue
            if (start_dt < existing.checkout_date and
                existing.checkin_date < requested_checkout):
                ns.abort(400, 'Place already booked for these dates')

        # Create booking
        data['checkin_date'] = checkin_date.isoformat()
        booking = facade.create_booking(data)

        return {
            'id':            booking.id,
            'user_id':       booking.user.id,
            'place_id':      booking.place.id,
            'guest_count':   booking.guest_count,
            'checkin_date':  booking.checkin_date.date(),
            'night_count':   booking.night_count,
            'total_price':   booking.place.price * booking.night_count * booking.guest_count,
            'checkout_date': booking.checkout_date.date(),
        }, 201

@ns.route('/<string:booking_id>')
class BookingDetail(Resource):
    @ns.marshal_with(booking_output)
    def get(self, booking_id):
        """Fetch a booking by its ID"""
        booking = facade.get_booking(booking_id) or ns.abort(404, f"Booking {booking_id} not found")
        return {
            'id':            booking.id,
            'user_id':       booking.user.id,
            'place_id':      booking.place.id,
            'guest_count':   booking.guest_count,
            'checkin_date':  booking.checkin_date.date(),
            'night_count':   booking.night_count,
            'total_price':   booking.place.price * booking.night_count * booking.guest_count,
            'checkout_date': booking.checkout_date.date(),
        }

    @ns.expect(booking_patch, validate=True)
    @ns.marshal_with(booking_output)
    def patch(self, booking_id):
        """Partially update a booking"""
        data = request.json
        booking = facade.get_booking(booking_id)
        if not booking:
            ns.abort(404, f"Booking {booking_id} not found")

        # guest_count
        if 'guest_count' in data:
            if data['guest_count'] <= 0:
                ns.abort(400, "Guest count must be greater than 0")
            if data['guest_count'] > booking.place.capacity:
                ns.abort(400, f"Guest count exceeds place capacity ({booking.place.capacity})")
            booking.guest_count = data['guest_count']

        # night_count
        if 'night_count' in data:
            if data['night_count'] <= 0:
                ns.abort(400, "Night count must be greater than 0")
            booking.night_count = data['night_count']

        # checkin_date
        if 'checkin_date' in data:
            try:
                checkin_date = date.fromisoformat(data['checkin_date'])
            except ValueError:
                ns.abort(400, 'Invalid checkin_date, must be YYYY-MM-DD')
            if checkin_date <= date.today():
                ns.abort(400, "Checkin_date must be later than today")
            booking.checkin_date = datetime.combine(checkin_date, datetime.min.time())

        # place_id
        if 'place_id' in data:
            new_place = facade.get_place(data['place_id'])
            if not new_place:
                ns.abort(400, "Place not found")
            booking.place = new_place

        # user_id
        if 'user_id' in data:
            new_user = facade.get_user(data['user_id'])
            if not new_user:
                ns.abort(400, "User not found")
            booking.user = new_user

        return {
            'id':            booking.id,
            'user_id':       booking.user.id,
            'place_id':      booking.place.id,
            'guest_count':   booking.guest_count,
            'checkin_date':  booking.checkin_date.date(),
            'night_count':   booking.night_count,
            'total_price':   booking.place.price * booking.night_count * booking.guest_count,
            'checkout_date': booking.checkout_date.date(),
        }

    def delete(self, booking_id):
        """Delete a booking"""
        if not facade.get_booking(booking_id):
            ns.abort(404, f"Booking {booking_id} not found")
        facade.delete_booking(booking_id)
        return '', 204

# --- New endpoint: get rating for a booking ---
@ns.route('/<string:booking_id>/rating')
@ns.response(404, 'Booking or rating not found')
class BookingRating(Resource):
    @ns.marshal_with(rating_output)
    def get(self, booking_id):
        """Get the rating for a specific booking"""
        booking = facade.get_booking(booking_id)
        if not booking:
            ns.abort(404, f"Booking {booking_id} not found")

        # Pull and coerce rating
        review = getattr(booking, 'review', None)
        if not review or not hasattr(review, 'rating'):
            ns.abort(404, f"No rating found for booking {booking_id}")

        try:
            rating_value = float(review.rating)
        except (ValueError, TypeError):
            ns.abort(500, 'Stored rating is invalid')

        return {
            'booking_id': booking_id,
            'rating':     rating_value
        }
