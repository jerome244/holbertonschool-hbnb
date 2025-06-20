"""
places.py: API endpoints for Place resources.

This module defines the Flask-RESTX namespace, data models, and resources
for listing, creating, retrieving, updating, deleting places, and fetching average ratings.
"""

from flask_restx import Namespace, Resource, fields
from app import facade

ns = Namespace("places", description="Place listings with amenities")

place_model = ns.model(
    "Place",
    {
        "id": fields.String(readOnly=True, description="Place UUID"),
        "title": fields.String(required=True, description="Title of the place"),
        "capacity": fields.Integer(required=True, description="Max guests"),
        "price": fields.Float(required=True, description="Price per night"),
        "latitude": fields.Float(description="Latitude of the place"),
        "longitude": fields.Float(description="Longitude of the place"),
        "host_id": fields.String(attribute="host.id", description="Owner’s UUID"),
        "description": fields.String(description="Textual description"),
        "amenity_ids": fields.List(fields.String, description="List of amenity UUIDs"),
    },
)

place_create = ns.model(
    "PlaceCreate",
    {
        "title": fields.String(required=True),
        "capacity": fields.Integer(required=True, description="> 0"),
        "price": fields.Float(required=True, description="> 0"),
        "latitude": fields.Float,
        "longitude": fields.Float,
        "host_id": fields.String(required=True),
        "description": fields.String,
        "amenity_ids": fields.List(fields.String),
    },
)

place_patch = ns.model(
    "PlacePatch",
    {
        "title": fields.String,
        "capacity": fields.Integer(description="> 0"),
        "price": fields.Float(description="> 0"),
        "description": fields.String,
        "amenity_ids": fields.List(fields.String),
    },
)


@ns.route("/")
class PlaceList(Resource):
    """
    List all places or create a new place.
    """

    @ns.marshal_list_with(place_model)
    def get(self):
        """
        Retrieve all places, appending amenity IDs.
        """
        places = facade.list_places()
        for p in places:
            p.amenity_ids = [a.id for a in getattr(p, "amenities", [])]
        return places

    @ns.expect(place_create, validate=True)
    @ns.marshal_with(place_model, code=201)
    def post(self):
        """
        Create a new place.

        Validates price and capacity, then links amenities if provided.

        Returns:
            tuple: (Place, HTTP 201)
        """
        payload = dict(ns.payload)
        amenities = payload.pop("amenity_ids", []) or []

        if payload["price"] <= 0:
            ns.abort(400, "Price must be greater than 0")
        if payload["capacity"] <= 0:
            ns.abort(400, "Capacity must be greater than 0")

        place = facade.create_place(payload)
        if place is None:
            ns.abort(409, "Cannot create Place: host invalid or title exists")

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
    Retrieve, update, or delete a specific place.
    """

    @ns.marshal_with(place_model)
    def get(self, place_id):
        """
        Fetch a place by ID, including its amenity IDs.

        Args:
            place_id (str): Place UUID.
        """
        p = facade.get_place(place_id) or ns.abort(404)
        p.amenity_ids = [a.id for a in getattr(p, "amenities", [])]
        return p

    @ns.expect(place_patch, validate=True)
    @ns.marshal_with(place_model)
    def patch(self, place_id):
        """
        Partially update place attributes.

        Args:
            place_id (str): Place UUID.

        Returns:
            Place
        """
        payload = dict(ns.payload)
        place = facade.get_place(place_id) or ns.abort(404)

        if "price" in payload and payload["price"] <= 0:
            ns.abort(400, "Price must be greater than 0")
        if "capacity" in payload and payload["capacity"] <= 0:
            ns.abort(400, "Capacity must be greater than 0")

        if "amenity_ids" in payload:
            ids = payload.pop("amenity_ids") or []
            place.amenities.clear()
            for aid in ids:
                am = facade.get_amenity(aid)
                if am:
                    place.add_amenity(am)

        updated = facade.update_place(place_id, payload)
        updated.amenity_ids = [a.id for a in getattr(updated, "amenities", [])]
        return updated

    def delete(self, place_id):
        """
        Delete a place by ID.

        Args:
            place_id (str): Place UUID.

        Returns:
            tuple: Empty response and HTTP 204 status.
        """
        deleted = facade.delete_place(place_id)
        if not deleted:
            ns.abort(404)
        return "", 204


place_rating_output = ns.model(
    "PlaceRating",
    {
        "place_id": fields.String(readOnly=True, description="Place UUID"),
        "average_rating": fields.Float(
            readOnly=True, description="Average across reviews"
        ),
    },
)


@ns.route("/<string:place_id>/rating")
@ns.response(404, "Place not found or no ratings available")
class PlaceRating(Resource):
    """
    Fetch the average rating for a place.
    """

    @ns.marshal_with(place_rating_output)
    def get(self, place_id):
        """
        Calculate and return the average review rating for this place.

        Args:
            place_id (str): Place UUID.

        Returns:
            dict: { 'place_id': str, 'average_rating': float }
        """
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
