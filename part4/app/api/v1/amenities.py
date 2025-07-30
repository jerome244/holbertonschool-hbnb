# ---------- amenities.py ----------
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt
from app.services import facade
from .models import amenity_model, amenity_input

ns = Namespace("amenities", description="Amenity management")

# ----------------------- data models ----------------------- #

amenity_model = amenity_model(ns)

amenity_input = amenity_input(ns)

# ----------------------- Resources ----------------------- #


@ns.route("/")
class AmenityList(Resource):
    @ns.doc("list_amenities", description="Retrieve all amenities (Public)")
    @ns.marshal_list_with(amenity_model)
    def get(self):
        """List all amenities."""
        return facade.list_amenities()

    @ns.doc(
        "create_amenity",
        description="Create a new amenity (Admin only); Payload: { 'name': 'string' }",
    )
    @ns.expect(amenity_input, validate=True)
    @jwt_required()
    @ns.marshal_with(amenity_model, code=201)
    def post(self):
        """Create a new amenity."""
        claims = get_jwt()
        if not claims.get("is_admin"):
            return {"error": "Unauthorized action"}, 403
        data = ns.payload or {}
        name = data.get("name", "").strip()
        if not name:
            return {"error": "Name cannot be empty"}, 400
        data["name"] = name
        amenity = facade.create_amenity(data)
        return amenity, 201


@ns.route("/<string:amenity_id>")
@ns.response(404, "Amenity not found")
class AmenityDetail(Resource):
    @ns.doc("get_amenity", description="Retrieve an amenity by its ID (Public)")
    @ns.marshal_with(amenity_model)
    def get(self, amenity_id):
        """Fetch an amenity by its ID."""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            ns.abort(404, f"Amenity {amenity_id} not found")
        return amenity, 200

    @ns.doc("delete_amenity", description="Delete an amenity by its ID (Admin only)")
    @jwt_required()
    @ns.response(204, "Amenity deleted")
    def delete(self, amenity_id):
        """Delete an amenity by its ID."""
        claims = get_jwt()
        if not claims.get("is_admin"):
            return {"error": "Unauthorized action"}, 403

        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            ns.abort(404, f"Amenity {amenity_id} not found")
        facade.delete_amenity(amenity_id)
        return "", 204
