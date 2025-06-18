from flask_restx import Namespace, Resource, fields
from app import facade

ns = Namespace('places', description='Place listings with amenities')

# Response model includes amenity_ids
place_model = ns.model('Place', {
    'id':          fields.String(readonly=True),
    'title':       fields.String(required=True),
    'capacity':    fields.Integer(required=True, description='Number of guests'),
    'price':       fields.Float(required=True, description='Price per night'),
    'latitude':    fields.Float(required=True),
    'longitude':   fields.Float(required=True),
    'host_id':     fields.String(required=True, attribute='host.id', description='UUID of the host'),
    'description': fields.String,
    'amenity_ids': fields.List(fields.String, description='List of amenity IDs'),
})

# Creation model allows optional amenity_ids
place_create_model = ns.model('PlaceCreate', {
    'title':        fields.String(required=True),
    'capacity':     fields.Integer(required=True, description='Number of guests'),
    'price':        fields.Float(required=True, description='Price per night'),
    'latitude':     fields.Float(required=True),
    'longitude':    fields.Float(required=True),
    'host_id':      fields.String(required=True, description='UUID of the host'),
    'description':  fields.String,
    'amenity_ids':  fields.List(fields.String, description='Optional list of amenity IDs'),
})

# Partial update for PATCH, now including amenity_ids
place_patch_model = ns.model('PlacePatch', {
    'title':       fields.String,
    'capacity':    fields.Integer(description='Number of guests'),
    'price':       fields.Float(description='Price per night'),
    'latitude':    fields.Float,
    'longitude':   fields.Float,
    'host_id':     fields.String(description='UUID of the host'),
    'description': fields.String,
    'amenity_ids': fields.List(fields.String, description='Optional list of amenity IDs'),
})

@ns.route('/')
class PlaceList(Resource):
    @ns.marshal_list_with(place_model)
    def get(self):
        """List all places"""
        places = facade.list_places()
        for p in places:
            p.amenity_ids = [a.id for a in getattr(p, 'amenities', [])]
        return places

    @ns.expect(place_create_model, validate=True)
    @ns.marshal_with(place_model, code=201)
    def post(self):
        """Create a new place, optionally with amenities"""
        payload = dict(ns.payload)

        # Validate capacity and price
        if payload.get('capacity', 0) <= 0:
            ns.abort(400, "Capacity must be greater than 0")
        if payload.get('price', 0.0) <= 0:
            ns.abort(400, "Price must be greater than 0")

        # Remove amenity_ids to avoid constructor errors
        amenity_ids = payload.pop('amenity_ids', []) or []

        # Validate host
        host_id = payload['host_id']
        if not facade.get_host(host_id):
            ns.abort(400, "Host not found")

        # Create the place without amenities
        place = facade.create_place(payload)

        # Attach each amenity, ignoring invalid IDs
        for aid in amenity_ids:
            amenity = facade.get_amenity(aid)
            if amenity:
                place.add_amenity(amenity)

        # Expose amenity_ids in response
        place.amenity_ids = [a.id for a in getattr(place, 'amenities', [])]
        return place, 201

@ns.route('/<string:place_id>')
@ns.response(404, 'Place not found')
class PlaceDetail(Resource):
    @ns.marshal_with(place_model)
    def get(self, place_id):
        """Fetch a place by ID"""
        place = facade.get_place(place_id) or ns.abort(404)
        place.amenity_ids = [a.id for a in getattr(place, 'amenities', [])]
        return place

    @ns.expect(place_patch_model, validate=True)
    @ns.marshal_with(place_model)
    def patch(self, place_id):
        """Partially update a place, including amenities if provided"""
        payload = dict(ns.payload)
        place = facade.get_place(place_id) or ns.abort(404)

        # Validate capacity and price if present
        if 'capacity' in payload and payload['capacity'] <= 0:
            ns.abort(400, "Capacity must be greater than 0")
        if 'price' in payload and payload['price'] <= 0:
            ns.abort(400, "Price must be greater than 0")

        # Handle amenities if included in patch (ignore invalid IDs)
        if 'amenity_ids' in payload:
            ids = payload.pop('amenity_ids') or []
            place.amenities.clear()
            for aid in ids:
                amenity = facade.get_amenity(aid)
                if amenity:
                    place.add_amenity(amenity)

        # Validate host if updating
        if 'host_id' in payload and not facade.get_host(payload['host_id']):
            ns.abort(400, "Host not found")

        # Update other fields
        updated = facade.update_place(place_id, payload)
        updated.amenity_ids = [a.id for a in getattr(updated, 'amenities', [])]
        return updated

    @ns.response(204, 'Place deleted')
    def delete(self, place_id):
        """Delete a place"""
        if not facade.get_place(place_id):
            ns.abort(404)
        facade.delete_place(place_id)
        return '', 204

# ——— Expose model’s get_average_rating() ———

@ns.route('/<string:place_id>/rating')
class PlaceRating(Resource):
    def get(self, place_id):
        place = facade.get_place(place_id) or ns.abort(404, 'Place not found')
        return {'average_rating': place.get_average_rating()}

# ——— Raw dict via BaseModel.to_dict() ———

@ns.route('/<string:place_id>/raw')
class PlaceRaw(Resource):
    def get(self, place_id):
        place = facade.get_place(place_id) or ns.abort(404, 'Place not found')
        return place.to_dict()
