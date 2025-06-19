# places.py

from flask_restx import Namespace, Resource, fields
from app import facade

ns = Namespace('places', description='Place listings with amenities')

place_model = ns.model('Place', {
    'id':          fields.String(readonly=True),
    'title':       fields.String(required=True),
    'capacity':    fields.Integer(required=True),
    'price':       fields.Float(required=True),
    'latitude':    fields.Float(readonly=True),
    'longitude':   fields.Float(readonly=True),
    'host_id':     fields.String(required=True, attribute='host.id'),
    'description': fields.String,
    'amenity_ids': fields.List(fields.String),
})

place_create = ns.model('PlaceCreate', {
    'title':       fields.String(required=True),
    'capacity':    fields.Integer(required=True),
    'price':       fields.Float(required=True),
    'latitude':    fields.Float,
    'longitude':   fields.Float,
    'host_id':     fields.String(required=True),
    'description': fields.String,
    'amenity_ids': fields.List(fields.String),
})

place_patch = ns.model('PlacePatch', {
    'title':       fields.String,
    'capacity':    fields.Integer,
    'price':       fields.Float,
    'description': fields.String,
    'amenity_ids': fields.List(fields.String),
})

@ns.route('/')
class PlaceList(Resource):
    @ns.marshal_list_with(place_model)
    def get(self):
        places = facade.list_places()
        for p in places:
            p.amenity_ids = [a.id for a in getattr(p, 'amenities', [])]
        return places

    @ns.expect(place_create, validate=True)
    @ns.marshal_with(place_model, code=201)
    def post(self):
        payload   = dict(ns.payload)
        amenities = payload.pop('amenity_ids', []) or []

        place = facade.create_place(payload)
        if place is None:
            # either invalid host or duplicate title
            ns.abort(409, f"Cannot create Place: host invalid or title already exists")  

        for aid in amenities:
            am = facade.get_amenity(aid)
            if am:
                place.add_amenity(am)

        place.amenity_ids = [a.id for a in getattr(place, 'amenities', [])]
        return place, 201

@ns.route('/<string:place_id>')
@ns.response(404, 'Place not found')
class PlaceDetail(Resource):
    @ns.marshal_with(place_model)
    def get(self, place_id):
        p = facade.get_place(place_id) or ns.abort(404)
        p.amenity_ids = [a.id for a in getattr(p, 'amenities', [])]
        return p

    @ns.expect(place_patch, validate=True)
    @ns.marshal_with(place_model)
    def patch(self, place_id):
        payload = dict(ns.payload)
        place   = facade.get_place(place_id) or ns.abort(404)

        if 'amenity_ids' in payload:
            ids = payload.pop('amenity_ids') or []
            place.amenities.clear()
            for aid in ids:
                am = facade.get_amenity(aid)
                if am:
                    place.add_amenity(am)

        updated = facade.update_place(place_id, payload)
        updated.amenity_ids = [a.id for a in getattr(updated, 'amenities', [])]
        return updated

    def delete(self, place_id):
        deleted = facade.delete_place(place_id)
        if not deleted:
            ns.abort(404)
        return '', 204

@ns.route('/<string:place_id>/rating')
class PlaceRating(Resource):
    def get(self, place_id):
        p = facade.get_place(place_id) or ns.abort(404)
        return {'average_rating': p.get_average_rating()}
