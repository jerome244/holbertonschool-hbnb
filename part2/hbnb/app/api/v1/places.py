"""
places.py: Flask-RESTX API endpoints for Place resources.

This module defines a namespace and models for places, including:
- Listing all places and creating a new place
- Retrieving, replacing, and deleting a place by ID
- Fetching a place’s average rating

Swagger UI will display these descriptions alongside each endpoint.
"""
from flask_restx import Namespace, Resource, fields
from app import facade

# ----------------------- namespace ----------------------- #
ns = Namespace(
    "places",
    description="Place listings with amenities"
)

# ----------------------- data models ----------------------- #
place_model = ns.model(
    "Place",
    {
        "id": fields.String(readOnly=True, description="Place UUID"),
        "title": fields.String(required=True, description="Title of the place"),
        "capacity": fields.Integer(required=True, description="Maximum number of guests"),
        "price": fields.Float(required=True, description="Price per night"),
        "latitude": fields.Float(description="Latitude of the place"),
        "longitude": fields.Float(description="Longitude of the place"),
        "host_id": fields.String(attribute="host.id", description="Owner’s UUID"),
        "description": fields.String(description="Textual description"),
        "amenity_ids": fields.List(fields.String, description="List of amenity UUIDs"),
    }
)

place_create = ns.model(
    "PlaceCreate",
    {
        "title": fields.String(required=True, description="Title of the place"),
        "capacity": fields.Integer(required=True, description="> 0"),
        "price": fields.Float(required=True, description="> 0"),
        "latitude": fields.Float(description="Latitude of the place"),
        "longitude": fields.Float(description="Longitude of the place"),
        "host_id": fields.String(required=True, description="UUID of the owner"),
        "description": fields.String(description="Textual description"),
        "amenity_ids": fields.List(fields.String, description="List of amenity UUIDs"),
    }
)

@ns.route("/")
class PlaceList(Resource):
    """
    GET  /places/  -> List all places.
    POST /places/  -> Create a new place.
                      Payload example:
                      {
                        "title": "Cozy Cottage",
                        "capacity": 4,
                        "price": 150.0,
                        "host_id": "<UUID>",
                        "description": "A nice place",
                        "amenity_ids": ["<amenity_uuid>"]
                      }
    """
    @ns.doc('list_places', description='Retrieve all places with amenity IDs')
    @ns.marshal_list_with(place_model)
    def get(self):
        places = facade.list_places()
        for p in places:
            p.amenity_ids = [a.id for a in getattr(p, "amenities", [])]
        return places

    @ns.doc('create_place', description='Create a new place with validation and amenities')
    @ns.expect(place_create, validate=True)
    @ns.marshal_with(place_model, code=201)
    def post(self):
        """
        Create a new place.

        Validates required fields, numeric bounds, and attaches amenities.
        """
        payload = dict(ns.payload)
        amenities = payload.pop("amenity_ids", []) or []

        required = {"title", "capacity", "price", "host_id"}
        missing = required - set(payload.keys())
        if missing:
            ns.abort(400, f"Missing fields for creation: {', '.join(sorted(missing))}")
        if payload["price"] <= 0:
            ns.abort(400, "Price must be greater than 0")
        if payload["capacity"] <= 0:
            ns.abort(400, "Capacity must be greater than 0")

        place = facade.create_place(payload)
        if place is None:
            ns.abort(409, "Cannot create Place: invalid host or title exists")

        for aid in amenities:
            am = facade.get_amenity(aid)
            if am:
                place.add_amenity(am)

        place.amenity_ids = [a.id for a in getattr(place, "amenities", [])]
        return place, 201

@ns.route("/<string:place_id>")
@ns.response(404, "Place not found")
class PlaceDetail(Resource):
    """
    GET    /places/{id}  -> Fetch a place by ID with amenity IDs.
    PUT    /places/{id}  -> Replace an existing place.
                          Payload example:
                          {
                            "title": "Lake House",
                            "capacity": 6,
                            "price": 200.0,
                            "latitude": 0.0,
                            "longitude": 0.0,
                            "host_id": "<UUID>",
                            "description": "Beautiful view",
                            "amenity_ids": ["<amenity_uuid>"]
                          }
    DELETE /places/{id}  -> Delete a place by ID.
    """
    @ns.doc('get_place', description='Fetch a place by its ID')
    @ns.marshal_with(place_model)
    def get(self, place_id):
        p = facade.get_place(place_id) or ns.abort(404, f"Place {place_id} not found")
        p.amenity_ids = [a.id for a in getattr(p, "amenities", [])]
        return p

    @ns.doc('replace_place', description='Replace an existing place completely')
    @ns.expect(place_create, validate=True)
    @ns.marshal_with(place_model)
    def put(self, place_id):
        """
        Replace an existing place.

        Validates required fields and numeric bounds, resets amenities, and casts numeric fields.
        """
        payload = dict(ns.payload)
        amenities = payload.pop("amenity_ids", []) or []

        required = {"title", "capacity", "price", "host_id"}
        missing = required - set(payload.keys())
        if missing:
            ns.abort(400, f"Missing fields for full update: {', '.join(sorted(missing))}")
        if payload["price"] <= 0:
            ns.abort(400, "Price must be greater than 0")
        if payload["capacity"] <= 0:
            ns.abort(400, "Capacity must be greater than 0")

        place = facade.get_place(place_id)
        if not place:
            ns.abort(404, f"Place {place_id} doesn't exist")

        # Reset amenities
        place.amenities.clear()
        for aid in amenities:
            am = facade.get_amenity(aid)
            if am:
                place.add_amenity(am)

        # Filter out None and cast ints to floats for numeric fields
        update_data = {}
        for k, v in payload.items():
            if v is None:
                continue
            if k in ("latitude", "longitude"):
                try:
                    v = float(v)
                except (TypeError, ValueError):
                    ns.abort(400, f"{k.capitalize()} must be a float")
            update_data[k] = v

        updated = facade.update_place(place_id, update_data)
        if not updated:
            ns.abort(404, f"Place {place_id} not found or not updated")

        updated.amenity_ids = [a.id for a in getattr(updated, "amenities", [])]
        return updated, 200

    @ns.doc('delete_place', description='Delete a place by ID')
    @ns.response(204, "Place deleted")
    def delete(self, place_id):
        deleted = facade.delete_place(place_id)
        if not deleted:
            ns.abort(404, f"Place {place_id} not found")
        return "", 204

@ns.route("/<string:place_id>/rating")
@ns.response(404, "Place not found or no ratings available")
class PlaceRating(Resource):
    """
    GET /places/{id}/rating  -> Calculate and return the average review rating for this place.
    """
    @ns.doc('get_place_rating', description='Calculate and return the average review rating for this place')
    @ns.marshal_with(
        ns.model(
            "PlaceRating",
            {
                "place_id": fields.String(readOnly=True, description="Place UUID"),
                "average_rating": fields.Float(readOnly=True, description="Average across reviews"),
            }
        )
    )
    def get(self, place_id):
        place = facade.get_place(place_id)
        if not place:
            ns.abort(404, f"Place {place_id} not found")

        reviews = facade.list_reviews()
        ratings = []
        for r in reviews:
            bk = getattr(r, "booking", None)
            if bk and bk.place and bk.place.id == place_id:
                try:
                    ratings.append(float(r.rating))
                except (ValueError, TypeError):
                    continue

        if not ratings:
            ns.abort(404, f"No ratings found for place {place_id}")

        average = sum(ratings) / len(ratings)
        return {"place_id": place_id, "average_rating": average}
