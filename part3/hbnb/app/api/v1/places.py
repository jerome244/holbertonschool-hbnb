from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

ns = Namespace(
    "places",
    description="Place listings with amenities",
    security='BearerAuth'
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
        "host_id": fields.String(attribute="host.id", description="Owner's UUID"),
        "description": fields.String(description="Textual description"),
        "amenity_ids": fields.List(fields.String, description="List of amenity UUIDs"),
    }
)

place_create = ns.model(
    "PlaceCreate",
    {
        "title": fields.String(required=True, description="Title of the place"),
        "capacity": fields.Integer(required=True, description="Capacity must be greater than 0"),
        "price": fields.Float(required=True, description="Price must be greater than 0"),
        "latitude": fields.Float(description="Latitude of the place"),
        "longitude": fields.Float(description="Longitude of the place"),
        "description": fields.String(description="Textual description"),
        "amenity_ids": fields.List(fields.String, description="List of amenity UUIDs"),
    }
)

@ns.route("/")
class PlaceList(Resource):
    @ns.doc(
        "list_places",
        description="Retrieve all places (Public)",
        security=[]
    )
    @ns.marshal_list_with(place_model)
    def get(self):
        """
        Retrieve a list of all place listings. Public access.
        """
        places = facade.list_places()
        for p in places:
            p.amenity_ids = [a.id for a in getattr(p, "amenities", [])]
        return places, 200

    @jwt_required()
    @ns.doc(
        "create_place",
        description="Create a new place (Authenticated hosts)",
        security='BearerAuth'
    )
    @ns.expect(place_create, validate=True)
    @ns.response(201, "Place created successfully", place_model)
    @ns.response(400, "Invalid input or missing fields")
    @ns.response(409, "Place creation conflict")
    def post(self):
        """
        Register a new place under the authenticated host account.
        Host identity is inferred from the JWT; client-supplied host_id is ignored.
        """
        payload = dict(ns.payload)
        amenities = payload.pop("amenity_ids", []) or []
        payload["host_id"] = get_jwt_identity()

        # Validate required fields
        missing = {"title", "capacity", "price"} - set(payload)
        if missing:
            return {"error": f"Missing fields: {', '.join(sorted(missing))}"}, 400
        if payload["price"] <= 0:
            return {"error": "Price must be greater than 0"}, 400
        if payload["capacity"] <= 0:
            return {"error": "Capacity must be greater than 0"}, 400

        place = facade.create_place(payload)
        if not place:
            return {"error": "Cannot create place: invalid host or title conflict"}, 409

        for aid in amenities:
            amenity = facade.get_amenity(aid)
            if amenity:
                place.add_amenity(amenity)

        place.amenity_ids = [a.id for a in getattr(place, "amenities", [])]
        return marshal(place, place_model), 201

@ns.route("/<string:place_id>")
@ns.response(404, "Place not found")
class PlaceDetail(Resource):
    @ns.doc(
        "get_place",
        description="Fetch a single place by its ID (Public)",
        security=[]
    )
    @ns.marshal_with(place_model)
    def get(self, place_id):
        """
        Retrieve detailed information for the specified place UUID. Public access.
        """
        place = facade.get_place(place_id)
        if not place:
            return {"error": f"Place {place_id} not found"}, 404
        place.amenity_ids = [a.id for a in getattr(place, "amenities", [])]
        return place, 200

    @jwt_required()
    @ns.doc(
        "update_place",
        description="Replace an entire place record (Owner or Admin)",
        security='BearerAuth'
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
        security='BearerAuth'
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
        security=[]
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
            float(r.rating) for r in reviews
            if getattr(r, "booking", None)
            and r.booking.place.id == place_id
            and isinstance(r.rating, (int, float, str))
        ]
        if not ratings:
            return {"error": f"No ratings found for place {place_id}"}, 404
        return {"place_id": place_id, "average_rating": sum(ratings) / len(ratings)}, 200
