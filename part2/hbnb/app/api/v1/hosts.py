from flask_restx import Namespace, Resource, fields
from app import facade

ns = Namespace("hosts", description="Host management")

# Full Host model returned by GET/POST/PATCH
host_model = ns.model(
    "Host",
    {
        "id": fields.String(readOnly=True, description="Unique host identifier"),
        "first_name": fields.String(required=True, description="Host's first name"),
        "last_name": fields.String(required=True, description="Host's last name"),
        "email": fields.String(required=True, description="Host's email address"),
        "is_admin": fields.Boolean(description="Host admin status"),
    },
)

# Separate model for creating a Host (no client-supplied 'id')
create_host_model = ns.model(
    "HostCreate",
    {
        "first_name": fields.String(required=True, description="Host's first name"),
        "last_name": fields.String(required=True, description="Host's last name"),
        "email": fields.String(required=True, description="Host's email address"),
        "is_admin": fields.Boolean(required=True, description="Host admin status"),
    },
)


@ns.route("")
class HostList(Resource):
    @ns.marshal_list_with(host_model)
    def get(self):
        """List all hosts"""
        return facade.list_hosts()

    @ns.expect(create_host_model, validate=True)
    @ns.marshal_with(host_model, code=201)
    def post(self):
        """Create a new host; server generates the ID"""
        data = ns.payload

        # Normalize & enforce unique email
        email = data["email"].strip().lower()
        if any(h.email.lower() == email for h in facade.list_hosts()):
            ns.abort(400, f"Host with email {email} already exists")

        # Delegate to facade; returned Host will have server-generated ID
        return facade.create_host(data), 201


@ns.route("/<string:host_id>")
class HostDetail(Resource):
    @ns.marshal_with(host_model)
    def get(self, host_id):
        """Fetch a host by ID"""
        host = facade.get_host(host_id)
        if not host:
            ns.abort(404, f"Host {host_id} not found")
        return host

    @ns.expect(host_model, validate=True)
    @ns.marshal_with(host_model)
    def patch(self, host_id):
        """Partially update a host, with email uniqueness enforced"""
        data = ns.payload
        host = facade.get_host(host_id)
        if not host:
            ns.abort(404, f"Host {host_id} not found")

        # If email is changing, check duplicates
        if "email" in data:
            new_email = data["email"].strip().lower()
            if any(
                h.email.lower() == new_email and h.id != host_id
                for h in facade.list_hosts()
            ):
                ns.abort(400, f"Email {new_email} already in use")
            data["email"] = new_email

        updated = facade.update_host(host_id, data)
        return updated or ns.abort(404)

    def delete(self, host_id):
        """Delete a host"""
        if not facade.get_host(host_id):
            ns.abort(404, f"Host {host_id} not found")
        facade.delete_host(host_id)
        return "", 204


@ns.route("/<string:host_id>/rating")
class HostRating(Resource):
    def get(self, host_id):
        """Get a host’s rating"""
        host = facade.get_host(host_id) or ns.abort(404)
        return {"host_rating": host.rating}


# Owned-places endpoint (unchanged)
from app.api.v1.places import place_model


@ns.route("/<string:host_id>/owned_places")
class HostOwnedPlaces(Resource):
    @ns.marshal_list_with(place_model)
    def get(self, host_id):
        places = facade.get_host_owned_places(host_id)
        if places is None:
            ns.abort(404, f"Host {host_id} not found")
        return places
