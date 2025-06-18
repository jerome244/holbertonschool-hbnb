# app/api/v1/bookings.py

from flask import request
from flask_restx import Namespace, Resource, fields
from app import facade

ns = Namespace('bookings', description='Booking management')

# 1) Input model (no `id`, no `checkout_date`)
booking_input = ns.model('BookingInput', {
    'user_id':      fields.String(required=True, description='UUID of the user'),
    'place_id':     fields.String(required=True, description='UUID of the place'),
    'guest_count':  fields.Integer(required=True, description='Number of guests'),
    'checkin_date': fields.DateTime(required=True, description='ISO-8601 date'),
    'night_count':  fields.Integer(required=True, description='Number of nights'),
})

# 2) Output model (inherits input and adds read-only fields)
booking_output = ns.inherit('Booking', booking_input, {
    'id':            fields.String(readOnly=True, description='Booking UUID'),
    'checkout_date': fields.DateTime(readOnly=True, description='Computed check-out date'),
})

@ns.route('/')
class BookingList(Resource):
    @ns.marshal_list_with(booking_output)
    def get(self):
        """List all bookings"""
        return facade.list_bookings()

    @ns.expect(booking_input, validate=True)      # only input model here
    @ns.marshal_with(booking_output, code=201)    # output model for response
    def post(self):
        """Create a new booking"""
        data = request.json
        booking = facade.create_booking(data)
        return {
            'id':            booking.id,
            'user_id':       booking.user.id,
            'place_id':      booking.place.id,
            'guest_count':   booking.guest_count,
            'checkin_date':  booking.checkin_date,
            'night_count':   booking.night_count,
            'checkout_date': booking.checkout_date,
        }, 201

@ns.route('/<string:booking_id>')
class BookingDetail(Resource):
    @ns.marshal_with(booking_output)
    def get(self, booking_id):
        """Fetch a booking by its ID"""
        booking = facade.get_booking(booking_id)
        ns.abort(404, f"Booking {booking_id} not found") if not booking else None
        return {
            'id':            booking.id,
            'user_id':       booking.user.id,
            'place_id':      booking.place.id,
            'guest_count':   booking.guest_count,
            'checkin_date':  booking.checkin_date,
            'night_count':   booking.night_count,
            'checkout_date': booking.checkout_date,
        }

    @ns.expect(booking_input, validate=True)
    @ns.marshal_with(booking_output)
    def patch(self, booking_id):
        """Update an existing booking"""
        booking = facade.update_booking(booking_id, request.json)
        ns.abort(404, f"Booking {booking_id} not found") if not booking else None
        return {
            'id':            booking.id,
            'user_id':       booking.user.id,
            'place_id':      booking.place.id,
            'guest_count':   booking.guest_count,
            'checkin_date':  booking.checkin_date,
            'night_count':   booking.night_count,
            'checkout_date': booking.checkout_date,
        }

    def delete(self, booking_id):
        """Delete a booking"""
        facade.delete_booking(booking_id)
        return '', 204
