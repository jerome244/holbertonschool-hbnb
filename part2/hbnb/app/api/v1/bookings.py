# app/api/v1/bookings.py

from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.facade import facade

booking_ns = Namespace('bookings', description='Booking operations')
booking_model = booking_ns.model('Booking', {
    'id': fields.String(readonly=True),
    'place_id': fields.String(required=True),
    'guest_count': fields.Integer(required=True),
    'checkin_date': fields.String(required=True),
    'night_count': fields.Integer(required=True),
    'total_price': fields.Float(readonly=True)
})

@booking_ns.route('/')
class BookingList(Resource):
    @booking_ns.marshal_list_with(booking_model)
    def get(self):
        return facade.get_all_bookings()

    @booking_ns.expect(booking_model, validate=True)
    @booking_ns.marshal_with(booking_model, code=201)
    def post(self):
        try:
            return facade.create_booking(request.get_json()), 201
        except KeyError as e:
            booking_ns.abort(404, str(e))
        except (TypeError, ValueError) as e:
            booking_ns.abort(400, str(e))

@booking_ns.route('/<string:id>')
@booking_ns.response(404, 'Booking not found')
class BookingResource(Resource):
    @booking_ns.marshal_with(booking_model)
    def get(self, id):
        try:
            return facade.get_booking(id)
        except KeyError as e:
            booking_ns.abort(404, str(e))

    @booking_ns.response(204, 'Booking deleted')
    def delete(self, id):
        try:
            facade.delete_booking(id)
            return '', 204
        except KeyError as e:
            booking_ns.abort(404, str(e))

    @booking_ns.expect(booking_model, validate=True)
    @booking_ns.marshal_with(booking_model)
    def put(self, id):
        try:
            return facade.update_booking(id, request.get_json())
        except KeyError as e:
            booking_ns.abort(404, str(e))
        except (TypeError, ValueError) as e:
            booking_ns.abort(400, str(e))
