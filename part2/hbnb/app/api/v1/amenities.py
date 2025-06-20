"""
amenities.py: Flask-RESTX API endpoints for Amenity resources.

This module defines a namespace and models for amenities, including:
- Listing all amenities and creating a new amenity
- Retrieving and deleting an amenity by ID

Swagger UI will display these descriptions alongside each endpoint.
"""

from flask_restx import Namespace, Resource, fields
from app import facade

# ----------------------- namespace ----------------------- #
ns = Namespace("amenities", description="Amenity management")

# ----------------------- data models ----------------------- #
# Output model (includes id)
amenity_model = ns.model(
    "Amenity",
    {
        "id": fields.String(
            readOnly=True, description="Unique amenity identifier (UUID)"
        ),
        "name": fields.String(required=True, description="Name of the amenity"),
    },
)

# Input model for creation (no id)
amenity_input = ns.model(
    "AmenityInput",
    {
        "name": fields.String(required=True, description="Name of the amenity"),
    },
)


# ----------------------- resources ----------------------- #
@ns.route("/")
class AmenityList(Resource):
    """
    GET  /amenities/  -> List all amenities.
    POST /amenities/  -> Create a new amenity.
                        Payload example:
                        { "name": "WiFi" }
    """

    @ns.doc("list_amenities", description="Retrieve all amenities")
    @ns.marshal_list_with(amenity_model)
    def get(self):
        """List all amenities."""
        return facade.list_amenities()

    @ns.doc(
        "create_amenity",
        description='Create a new amenity; Payload: { "name": "string" }',
    )
    @ns.expect(amenity_input, validate=True)
    @ns.marshal_with(amenity_model, code=201)
    def post(self):
        """Create a new amenity."""
        data = ns.payload or {}
        if not data.get("name") or not data["name"].strip():
            ns.abort(400, "Name cannot be empty")
        return facade.create_amenity(data), 201


@ns.route("/<string:amenity_id>")
@ns.response(404, "Amenity not found")
class AmenityDetail(Resource):
    """
    GET    /amenities/{id}  -> Retrieve an amenity by ID.
    DELETE /amenities/{id}  -> Delete an amenity by ID.
    """

    @ns.doc("get_amenity", description="Retrieve an amenity by its ID")
    @ns.marshal_with(amenity_model)
    def get(self, amenity_id):
        """Fetch an amenity by its ID."""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            ns.abort(404, f"Amenity {amenity_id} not found")
        return amenity

    @ns.doc("delete_amenity", description="Delete an amenity by its ID")
    @ns.response(204, "Amenity deleted")
    def delete(self, amenity_id):
        """Delete an amenity by its ID."""
        if not facade.get_amenity(amenity_id):
            ns.abort(404, f"Amenity {amenity_id} not found")
        facade.delete_amenity(amenity_id)
        return "", 204
