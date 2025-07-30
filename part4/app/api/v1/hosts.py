from flask_restx import Resource, marshal
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.services import facade
from app.api.v1.places import place_model
from .models import EMAIL_RE, host_create, host_model, host_update
from .ns import ns
from ...models.host import Host

# ----------------------- data models ----------------------- #

host_create = host_create(ns)
host_model = host_model(ns)
host_update = host_update(ns)

# ----------------------- resources ----------------------- #


@ns.route("/hosts")
@ns.doc(tags=["Hosts"])
class HostList(Resource):
    @jwt_required()
    @ns.doc(
        "list_hosts",
        description="List all host accounts (Admin only)",
        security="BearerAuth",
    )
    @ns.response(403, "Unauthorized action")
    @ns.marshal_list_with(host_model)
    def get(self):
        claims = get_jwt()
        if not claims.get("is_admin"):
            ns.abort(403, "Unauthorized action")
        return facade.list_hosts(), 200

    @jwt_required(optional=True)
    @ns.doc(
        "create_host",
        description="Create a new host (if first user created is admin, then admin-only)",
    )
    @ns.expect(host_create, validate=True)
    @ns.response(400, "Invalid input")
    @ns.response(201, "Host created successfully", host_model)
    def post(self):
        data = ns.payload or {}
        first = data.get("first_name", "").strip()
        last = data.get("last_name", "").strip()
        email = data.get("email", "").strip().lower()
        pwd = data.get("password", "")

        claims = get_jwt()
        caller_is_admin = claims.get("is_admin", False)

        requested_admin = bool(data.get("is_admin", False))
        is_admin = requested_admin if caller_is_admin else False

        print("Is first user:", facade.is_first_user())
        print("Caller is admin:", caller_is_admin)
        print("Requested admin:", data.get("is_admin"))
        print("Final is_admin assigned:", is_admin)

        if not first or not last:
            ns.abort(400, "First and last name required")
        if not EMAIL_RE.match(email):
            ns.abort(400, "Invalid email address")
        if any(h.email.lower() == email for h in facade.list_hosts()):
            ns.abort(400, f"Host with email {email} already exists")
        if len(pwd) < 8:
            ns.abort(400, "Password must be at least 8 characters")

        host = facade.create_host(
            {
                "first_name": first,
                "last_name": last,
                "email": email,
                "password": pwd,
                "is_admin": is_admin,
            }
        )
        return marshal(host, host_model), 201


@ns.route("/hosts/<string:host_id>")
@ns.response(404, "Host not found")
@ns.doc(tags=["Hosts"])
class HostDetail(Resource):
    @jwt_required()
    @ns.doc(
        "get_host",
        description="Retrieve host details (Self or Admin)",
        security="BearerAuth",
    )
    @ns.marshal_with(host_model)
    def get(self, host_id):
        host = facade.get_host(host_id)
        if not host:
            ns.abort(404, f"Host {host_id} not found")
        claims = get_jwt()
        caller = get_jwt_identity()
        if not claims.get("is_admin"):
            if caller != host_id or not isinstance(host, Host):
                ns.abort(403, "Unauthorized action")
        return host, 200

    @jwt_required()
    @ns.doc(
        "update_host",
        description="Update host profile (Self or Admin)",
        security="BearerAuth",
    )
    @ns.expect(host_update, validate=True)
    def put(self, host_id):
        host = facade.get_host(host_id)
        if not host:
            ns.abort(404, f"Host {host_id} not found")
        claims = get_jwt()
        caller = get_jwt_identity()
        if not claims.get("is_admin"):
            if caller != host_id or not isinstance(host, Host):
                ns.abort(403, "Unauthorized action")

        data = ns.payload or {}
        if "email" in data or "password" in data:
            ns.abort(400, "You cannot modify email or password here")

        updates = {}
        if "first_name" in data:
            updates["first_name"] = data["first_name"].strip()
        if "last_name" in data:
            updates["last_name"] = data["last_name"].strip()
        if claims.get("is_admin") and "is_admin" in data:
            updates["is_admin"] = bool(data["is_admin"])
        if not updates:
            ns.abort(400, "No valid fields provided for update")

        updated = facade.update_host(host_id, updates)
        return marshal(updated, host_model), 200

    @jwt_required()
    @ns.doc(
        "delete_host",
        description="Delete a host (Self or Admin)",
        security="BearerAuth",
    )
    @ns.response(204, "Host deleted")
    def delete(self, host_id):
        host = facade.get_host(host_id)
        if not host:
            ns.abort(404, f"Host {host_id} not found")
        claims = get_jwt()
        caller = get_jwt_identity()
        if not claims.get("is_admin"):
            if caller != host_id or not isinstance(host, Host):
                ns.abort(403, "Unauthorized action")
        facade.delete_host(host_id)
        return "", 204


@ns.route("/hosts/<string:host_id>/rating")
@ns.response(404, "Host not found or rating unavailable")
@ns.doc(tags=["Hosts"])
class HostRating(Resource):
    @ns.doc("get_host_rating", description="Get host rating (Public)", security=[])
    def get(self, host_id):
        host = facade.get_host(host_id)
        if not host:
            ns.abort(404, f"Host {host_id} not found")
        return {"host_rating": float(getattr(host, "rating", 0.0) or 0.0)}, 200


@ns.route("/hosts/<string:host_id>/owned_places")
@ns.response(404, "Host not found")
@ns.doc(tags=["Hosts"])
class HostOwnedPlaces(Resource):
    @ns.doc(
        "get_host_owned_places",
        description="List places owned by host (Public)",
        security=[],
    )
    @ns.marshal_list_with(place_model)
    def get(self, host_id):
        places = facade.get_host_owned_places(host_id)
        if places is None:
            ns.abort(404, f"Host {host_id} not found")
        return places, 200
