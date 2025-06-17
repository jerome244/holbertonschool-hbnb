# app/api/v1/places.py

from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.facade import facade

place_ns = Namespace('places', description='Place operations')
place_model = place_ns.model('Place', {
    'id': fields.String(readonly=True),
    'title': fields.String(required=True),
    'capacity': fields.Integer(required=True),
    'price': fields.Float(required=True),
    'latitude': fields.Float(required=True),
    'longitude': fields.Float(required=True),
    'description': fields.String(),
    'host_id': fields.String(required=True)
})

@place_ns.route('/')
class PlaceList(Resource):
    @place_ns.marshal_list_with(place_model)
    def get(self):
        return facade.get_all_places()

    @place_ns.expect(place_model, validate=True)
    @place_ns.marshal_with(place_model, code=201)
    def post(self):
        try:
            return facade.create_place(request.get_json()), 201
        except KeyError as e:
            place_ns.abort(404, str(e))
        except (TypeError, ValueError) as e:
            place_ns.abort(400, str(e))

@place_ns.route('/<string:id>')
@place_ns.response(404, 'Place not found')
class PlaceResource(Resource):
    @place_ns.marshal_with(place_model)
    def get(self, id):
        try:
            return facade.get_place(id)
        except KeyError as e:
            place_ns.abort(404, str(e))

    @place_ns.expect(place_model, validate=True)
    @place_ns.marshal_with(place_model)
    def put(self, id):
        try:
            return facade.update_place(id, request.get_json())
        except KeyError as e:
            place_ns.abort(404, str(e))
        except (TypeError, ValueError) as e:
            place_ns.abort(400, str(e))

    @place_ns.response(204, 'Place deleted')
    def delete(self, id):
        try:
            facade.delete_place(id)
            return '', 204
        except KeyError as e:
            place_ns.abort(404, str(e))
