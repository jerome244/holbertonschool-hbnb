# app/api/v1/amenities.py

from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.facade import facade

amenity_ns = Namespace('amenities', description='Amenity operations')
amenity_model = amenity_ns.model('Amenity', {
    'id': fields.String(readonly=True),
    'name': fields.String(required=True)
})
link_model = amenity_ns.model('AmenityLink', {
    'place_id': fields.String(required=True),
    'amenity_id': fields.String(required=True)
})

@amenity_ns.route('/')
class AmenityList(Resource):
    @amenity_ns.marshal_list_with(amenity_model)
    def get(self):
        return facade.get_all_amenities()

    @amenity_ns.expect(amenity_model, validate=True)
    @amenity_ns.marshal_with(amenity_model, code=201)
    def post(self):
        try:
            return facade.create_amenity(request.get_json()), 201
        except (TypeError, ValueError) as e:
            amenity_ns.abort(400, str(e))

@amenity_ns.route('/link')
class AmenityLink(Resource):
    @amenity_ns.expect(link_model, validate=True)
    @amenity_ns.marshal_with(link_model, code=201)
    def post(self):
        data = request.get_json()
        try:
            return facade.add_amenity(data['place_id'], data['amenity_id']), 201
        except KeyError as e:
            amenity_ns.abort(404, str(e))

@amenity_ns.route('/<string:id>')
@amenity_ns.response(404, 'Amenity not found')
class AmenityResource(Resource):
    @amenity_ns.response(204, 'Amenity deleted')
    def delete(self, id):
        try:
            facade.delete_amenity(id)
            return '', 204
        except KeyError as e:
            amenity_ns.abort(404, str(e))
