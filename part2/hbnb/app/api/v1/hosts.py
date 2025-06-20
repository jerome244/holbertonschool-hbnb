"""
hosts.py: Flask-RESTX API endpoints for Host resources.

Defines a namespace and models for hosts, including:
- Listing hosts
- Creating hosts (with optional is_admin)
- Retrieving, replacing, and deleting a host by ID
- Fetching a host’s rating
- Listing places owned by a host

Swagger UI will use these models and docstrings for endpoint documentation.
"""

from flask_restx import Namespace, Resource, fields
import re
from app import facade
from app.api.v1.places import place_model

# ----------------------- namespace ----------------------- #
ns = Namespace("hosts", description="Host management")

# ----------------------- data models ----------------------- #
host_model = ns.model(
    "Host",
    {
        "id": fields.String(readonly=True, description="Unique host identifier (UUID)"),
        "first_name": fields.String(required=True, description="Host's first name"),
        "last_name": fields.String(required=True, description="Host's last name"),
        "email": fields.String(required=True, description="Host's email address"),
        "is_admin": fields.Boolean(
            required=True, description="Flag indicating if host has admin privileges"
        ),
    },
)

# Input model for creating a new host (is_admin optional)
host_create = ns.model(
    "HostCreate",
    {
        "first_name": fields.String(required=True, description="Host's first name"),
        "last_name": fields.String(required=True, description="Host's last name"),
        "email": fields.String(required=True, description="Host's email address"),
        "is_admin": fields.Boolean(
            description="Optional admin flag; defaults to False if omitted"
        ),
    },
)

# Input model for full replace
host_input = ns.model(
    "HostInput",
    {
        "first_name": fields.String(required=True, description="Host's first name"),
        "last_name": fields.String(required=True, description="Host's last name"),
        "email": fields.String(required=True, description="Host's email address"),
        "is_admin": fields.Boolean(
            required=True, description="Admin flag; must be provided for full replace"
        ),
    },
)

EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


# ----------------------- resources ----------------------- #
@ns.route("")
class HostList(Resource):
    """
    GET  /hosts/  -> List all hosts.
    POST /hosts/  -> Create a new host.
                     Payload example:
                     {
                       "first_name": "Alice",
                       "last_name": "Smith",
                       "email": "alice@example.com",
                       "is_admin": true  # optional
                     }
    """

    @ns.doc("list_hosts", description="List all hosts with basic information")
    @ns.marshal_list_with(host_model)
    def get(self):
        return facade.list_hosts()

    @ns.doc(
        "create_host",
        description="Create a new host. Payload: first_name, last_name, email, optional is_admin",
    )
    @ns.expect(host_create, validate=True)
    @ns.marshal_with(host_model, code=201)
    def post(self):
        data = ns.payload or {}
        email = data.get("email", "").strip().lower()
        if not EMAIL_RE.match(email):
            ns.abort(400, "Invalid email address")
        if any(h.email.lower() == email for h in facade.list_hosts()):
            ns.abort(400, f"Host with email {email} already exists")
        data["email"] = email
        data.setdefault("is_admin", False)
        return facade.create_host(data), 201


@ns.route("/<string:host_id>")
@ns.response(404, "Host not found")
class HostDetail(Resource):
    """
    GET    /hosts/{id}  -> Retrieve a host by ID.
    PUT    /hosts/{id}  -> Replace a host completely.
                          Payload example:
                          {
                            "first_name": "Bob",
                            "last_name": "Jones",
                            "email": "bob@example.com",
                            "is_admin": false
                          }
    DELETE /hosts/{id}  -> Delete a host by ID.
    """

    @ns.doc("get_host", description="Retrieve a host by ID")
    @ns.marshal_with(host_model)
    def get(self, host_id):
        host = facade.get_host(host_id)
        if not host:
            ns.abort(404, f"Host {host_id} not found")
        return host

    @ns.doc(
        "replace_host",
        description="Replace an existing host completely. Payload: first_name, last_name, email, is_admin",
    )
    @ns.expect(host_input, validate=True)
    @ns.marshal_with(host_model)
    def put(self, host_id):
        data = ns.payload or {}
        host = facade.get_host(host_id)
        if not host:
            ns.abort(404, f"Host {host_id} not found")
        email = data.get("email", "").strip().lower()
        if not EMAIL_RE.match(email):
            ns.abort(400, "Invalid email address")
        if any(
            h.email.lower() == email and h.id != host_id for h in facade.list_hosts()
        ):
            ns.abort(400, f"Email {email} already in use")
        data["email"] = email
        required = {"first_name", "last_name", "email", "is_admin"}
        missing = required - set(data.keys())
        if missing:
            ns.abort(
                400, f"Missing fields for full update: {', '.join(sorted(missing))}"
            )
        return facade.update_host(host_id, data), 200

    @ns.doc("delete_host", description="Delete a host by ID")
    @ns.response(204, "Host deleted")
    def delete(self, host_id):
        if not facade.get_host(host_id):
            ns.abort(404, f"Host {host_id} not found")
        facade.delete_host(host_id)
        return "", 204


@ns.route("/<string:host_id>/rating")
@ns.response(404, "Host not found")
class HostRating(Resource):
    """
    GET /hosts/{id}/rating  -> Fetch the numeric rating for a host.
    """

    @ns.doc("get_host_rating", description="Fetch the numeric rating for a host")
    def get(self, host_id):
        host = facade.get_host(host_id)
        if not host:
            ns.abort(404, f"Host {host_id} not found")
        return {"host_rating": host.rating}


@ns.route("/<string:host_id>/owned_places")
@ns.response(404, "Host not found")
class HostOwnedPlaces(Resource):
    """
    GET /hosts/{id}/owned_places  -> List places owned by the host.
    """

    @ns.doc(
        "list_host_owned_places", description="List all places owned by the given host"
    )
    @ns.marshal_list_with(place_model)
    def get(self, host_id):
        places = facade.get_host_owned_places(host_id)
        if places is None:
            ns.abort(404, f"Host {host_id} not found")
        return places
