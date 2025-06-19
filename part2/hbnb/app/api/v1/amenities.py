from flask_restx import Namespace, Resource, fields
from app import facade

ns = Namespace("amenities", description="Amenity management")

amenity_model = ns.model(
    "Amenity",
    {
        "id": fields.String(readonly=True),
        "name": fields.String(required=True, description="Name of the amenity"),
    },
)


@ns.route("/")
class AmenityList(Resource):
    @ns.marshal_list_with(amenity_model)
    def get(self):
        """List all amenities"""
        return facade.list_amenities()

    @ns.expect(amenity_model, validate=True)
    @ns.marshal_with(amenity_model, code=201)
    def post(self):
        """Create a new amenity"""
        name = ns.payload.get("name", "").strip()
        if not name:
            ns.abort(400, "Amenity name cannot be empty")
        if any(a.name.lower() == name.lower() for a in facade.list_amenities()):
            ns.abort(400, "Amenity already exists")
        amenity = facade.create_amenity({"name": name})
        return amenity, 201


@ns.route("/<string:amenity_id>")
@ns.response(404, "Amenity not found")
class AmenityDetail(Resource):
    @ns.marshal_with(amenity_model)
    def get(self, amenity_id):
        """Fetch an amenity by ID"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            ns.abort(404, f"Amenity {amenity_id} doesn't exist")
        return amenity

    @ns.response(204, "Amenity deleted")
    def delete(self, amenity_id):
        """Delete an amenity"""
        if not facade.get_amenity(amenity_id):
            ns.abort(404, f"Amenity {amenity_id} doesn't exist")
        facade.delete_amenity(amenity_id)
        return "", 204
