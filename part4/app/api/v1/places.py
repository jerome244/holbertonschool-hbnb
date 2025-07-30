from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.facade import facade
from flask import abort, request
from app.models.amenity import Amenity
from app.api.v1.bookings import booking_output

ns = Namespace(
    "places", description="Place listings with amenities", security="BearerAuth"
)

# ----------------------- data models ----------------------- #
place_model = ns.model(
    "Place",
    {
        "id": fields.String(readOnly=True, description="Place UUID"),
        "title": fields.String(required=True, description="Title of the place"),
        "capacity": fields.Integer(
            required=True, description="Maximum number of guests"
        ),
        "price": fields.Float(required=True, description="Price per night"),
        "latitude": fields.Float(description="Latitude of the place"),
        "longitude": fields.Float(description="Longitude of the place"),
        "host_id": fields.String(attribute="host.id", description="Owner's UUID"),
        "description": fields.String(description="Textual description"),
        "amenity_ids": fields.List(fields.String, description="List of amenity UUIDs"),
    },
)

place_create = ns.model(
    "PlaceCreate",
    {
        "title": fields.String(required=True, description="Title of the place"),
        "capacity": fields.Integer(
            required=True, description="Capacity must be greater than 0"
        ),
        "price": fields.Float(
            required=True, description="Price must be greater than 0"
        ),
        "latitude": fields.Float(description="Latitude of the place"),
        "longitude": fields.Float(description="Longitude of the place"),
        "description": fields.String(description="Textual description"),
        "amenity_ids": fields.List(fields.String, description="List of amenity UUIDs"),
    },
)

amenity_model = ns.model(
    "Amenity",
    {
        "id": fields.String(readOnly=True, description="Amenity UUID"),
        "name": fields.String(required=True, description="Amenity name"),
    },
)


@ns.route("/")
class PlaceList(Resource):
    @ns.doc(
        "list_places",
        description="Retrieve all places, or places near lat/lon if provided (Public)",
        security=[],
    )
    @ns.marshal_list_with(place_model)
    def get(self):
        lat = request.args.get("lat", type=float)
        lon = request.args.get("lon", type=float)
        if lat is not None and lon is not None:
            # Replace with a real radius filter if you want, but this works as a demo
            places = [
                p
                for p in facade.place.list()
                if p.latitude is not None
                and p.longitude is not None
                and abs(p.latitude - lat) < 0.05
                and abs(p.longitude - lon) < 0.05
            ]
        else:
            places = facade.place.list()
        return places


@ns.route("/<string:place_id>")
@ns.response(404, "Place not found")
class PlaceDetail(Resource):
    @ns.doc(
        "get_place", description="Fetch a single place by its ID (Public)", security=[]
    )
    @ns.marshal_with(place_model)
    def get(self, place_id):
        """
        Retrieve detailed information for the specified place UUID. Public access.
        """
        place = facade.get_place(place_id)
        if not place:
            ns.abort(404, f"Place {place_id} not found")
        place.amenity_ids = [a.id for a in getattr(place, "amenities", [])]
        return place, 200

    @jwt_required()
    @ns.doc(
        "update_place",
        description="Replace an entire place record (Owner or Admin)",
        security="BearerAuth",
    )
    @ns.expect(place_create, validate=True)
    @ns.response(200, "Place updated successfully", place_model)
    @ns.response(400, "Invalid input or missing fields")
    @ns.response(403, "Unauthorized action")
    def put(self, place_id):
        """
        Overwrite all fields of an existing place. Owners may update their own listings; admins may update any.
        Amenities list is fully replaced; host_id cannot be changed.
        """
        claims = get_jwt()
        caller_id = get_jwt_identity()
        place = facade.get_place(place_id)
        if not place:
            return {"error": f"Place {place_id} not found"}, 404
        if caller_id != place.host.id and not claims.get("is_admin"):
            return {"error": "Unauthorized action"}, 403

        payload = dict(ns.payload)
        amenities = payload.pop("amenity_ids", []) or []

        # Validate required fields
        missing = {"title", "capacity", "price"} - set(payload)
        if missing:
            return {"error": f"Missing fields: {', '.join(sorted(missing))}"}, 400
        if payload["price"] <= 0:
            return {"error": "Price must be greater than 0"}, 400
        if payload["capacity"] <= 0:
            return {"error": "Capacity must be greater than 0"}, 400

        # Replace amenities
        place.amenities.clear()
        for aid in amenities:
            amenity = facade.get_amenity(aid)
            if amenity:
                place.add_amenity(amenity)

        # Prepare update data
        update_data = {}
        for key, value in payload.items():
            if key in ("latitude", "longitude"):
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    return {"error": f"{key.capitalize()} must be a number"}, 400
            update_data[key] = value

        updated = facade.update_place(place_id, update_data)
        updated.amenity_ids = [a.id for a in getattr(updated, "amenities", [])]
        return marshal(updated, place_model), 200

    @jwt_required()
    @ns.doc(
        "delete_place",
        description="Delete a place by its ID (Owner or Admin)",
        security="BearerAuth",
    )
    @ns.response(204, "Place deleted")
    @ns.response(403, "Unauthorized action")
    def delete(self, place_id):
        """
        Remove a place listing. Owners may delete their own listings; admins can delete any.
        """
        claims = get_jwt()
        caller_id = get_jwt_identity()
        place = facade.get_place(place_id)
        if not place:
            return {"error": f"Place {place_id} not found"}, 404
        if caller_id != place.host.id and not claims.get("is_admin"):
            return {"error": "Unauthorized action"}, 403
        facade.delete_place(place_id)
        return "", 204


@ns.route("/<string:place_id>/rating")
@ns.response(404, "Place not found or no ratings available")
class PlaceRating(Resource):
    @ns.doc(
        "get_place_rating",
        description="Return the average review rating for a place (Public)",
        security=[],
    )
    def get(self, place_id):
        """
        Calculate and return the average rating score for the specified place UUID.
        """
        place = facade.get_place(place_id)
        if not place:
            return {"error": f"Place {place_id} not found"}, 404
        reviews = facade.list_reviews()
        ratings = [
            float(r.rating)
            for r in reviews
            if getattr(r, "booking", None)
            and r.booking.place.id == place_id
            and isinstance(r.rating, (int, float, str))
        ]
        if not ratings:
            return {"error": f"No ratings found for place {place_id}"}, 404
        return {
            "place_id": place_id,
            "average_rating": sum(ratings) / len(ratings),
        }, 200


@ns.route("/<string:place_id>/bookings")
@ns.response(404, "Place not found")
class PlaceBookings(Resource):
    @jwt_required(optional=True)
    @ns.doc(
        "list_place_bookings",
        description="List all bookings for a place (Owners, Admins or Public?)",
        security="BearerAuth",
    )
    @ns.marshal_list_with(booking_output)
    def get(self, place_id):
        """
        Retrieve all bookings for the given place.
        """
        place = facade.get_place(place_id)
        if not place:
            ns.abort(404, f"Place {place_id} not found")

        # Optional: enforce owner/admin if you don’t want these public
        caller = get_jwt_identity()
        claims = get_jwt()
        if place.host.id != caller and not claims.get("is_admin"):
            ns.abort(403, "Unauthorized action")

        bookings = facade.list_bookings_for_place(place_id)
        return bookings, 200


@ns.route("/<string:place_id>/amenities")
@ns.response(404, "Place not found")
class PlaceAmenitiesList(Resource):
    @ns.doc("list_place_amenities")
    @ns.marshal_list_with(amenity_model)
    def get(self, place_id):
        place = facade.get_place(place_id)
        if not place:
            abort(404)
        if hasattr(place, "amenities"):
            items = place.amenities
        else:
            items = [facade.get_amenity(aid) for aid in place.amenity_ids]
        return items, 200


@ns.route("/<string:place_id>/amenities/<string:amenity_id>")
@ns.response(404, "Place or Amenity not found")
class PlaceAmenityLink(Resource):
    @ns.doc("link_place_amenity")
    @ns.marshal_with(amenity_model, code=201)
    def post(self, place_id, amenity_id):
        place = facade.get_place(place_id)
        amenity = facade.get_amenity(amenity_id)
        if not place or not amenity:
            abort(404)
        if amenity in getattr(place, "amenities", []):
            return amenity, 200
        place.add_amenity(amenity)
        return amenity, 201

    @ns.doc("unlink_place_amenity")
    def delete(self, place_id, amenity_id):
        place = facade.get_place(place_id)
        amenity = facade.get_amenity(amenity_id)
        if not place or not amenity or amenity not in getattr(place, "amenities", []):
            abort(404)
        place.remove_amenity(amenity)
        return {}, 200
