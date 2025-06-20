"""
amenities.py: API endpoints for Amenity resources.

This module defines the Flask-RESTX namespace, data model, and resource classes
for listing, creating, retrieving, and deleting amenities.
"""

from flask_restx import Namespace, Resource, fields
from app import facade

# ----------------------- namespace ----------------------- #
ns = Namespace("amenities", description="Amenity management")

# ----------------------- data model ----------------------- #
amenity_model = ns.model(
    "Amenity",
    {
        "id": fields.String(
            readonly=True, description="Unique identifier of the amenity"
        ),
        "name": fields.String(required=True, description="Name of the amenity"),
    },
)


# ----------------------- resources ----------------------- #
@ns.route("/")
class AmenityList(Resource):
    """
    Resource for listing and creating amenities.
    """

    @ns.marshal_list_with(amenity_model)
    def get(self):
        """
        List all amenities.

        Returns:
            list: A list of all Amenity objects.
        """
        return facade.get_all_amenities()

    @ns.expect(amenity_model, validate=True)
    @ns.marshal_with(amenity_model, code=201)
    def post(self):
        """
        Create a new amenity.

        Validates payload and checks for duplicates before creation.

        Returns:
            Amenity: The newly created Amenity object.
        """
        return facade.create_amenity(ns.payload), 201


@ns.route("/<string:amenity_id>")
@ns.response(404, "Amenity not found")
class AmenityDetail(Resource):
    """
    Resource for retrieving and deleting a single amenity by ID.
    """

    @ns.marshal_with(amenity_model)
    def get(self, amenity_id):
        """
        Fetch an amenity by its ID.

        Args:
            amenity_id (str): Unique identifier of the amenity.

        Returns:
            Amenity: The requested Amenity object.
        """
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            ns.abort(404, f"Amenity {amenity_id} doesn't exist")
        return amenity

    @ns.response(204, "Amenity deleted")
    def delete(self, amenity_id):
        """
        Delete an amenity by its ID.

        Args:
            amenity_id (str): Unique identifier of the amenity.

        Returns:
            tuple: Empty response and HTTP 204 status.
        """
        if not facade.get_amenity(amenity_id):
            ns.abort(404, f"Amenity {amenity_id} doesn't exist")
        facade.delete_amenity(amenity_id)
        return "", 204
