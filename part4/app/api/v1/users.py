from flask_restx import Resource, marshal
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.services.facade import facade
from .models import EMAIL_RE, user_model, user_create, user_update
from flask import request
from .ns import ns
from app.api.v1.bookings import booking_output

# ----------------------- data models ----------------------- #

user_model = user_model(ns)
user_create = user_create(ns)
user_update = user_update(ns)

# ----------------------- resources ----------------------- #


@ns.route("/users")
@ns.doc(tags=["Users"])
class UserList(Resource):
    @jwt_required()
    @ns.doc(
        "list_users",
        description="List all user accounts (Admin only)",
        security="BearerAuth",
    )
    @ns.response(403, "Unauthorized action")
    @ns.marshal_list_with(user_model)
    def get(self):
        claims = get_jwt()
        if not claims.get("is_admin"):
            ns.abort(403, "Unauthorized action")
        user_list = facade.list_users()
        host_ids = {host.id for host in facade.list_hosts()}  # Precompute host IDs

        # Inject is_host flag into each user
        enriched_users = []
        for user in user_list:
            user_dict = marshal(user, user_model)
            user_dict["is_host"] = user.id in host_ids
            enriched_users.append(user_dict)

        return enriched_users, 200

    @jwt_required(optional=True)
    @ns.doc(
        "create_user",
        description="Create a new user account (first is admin, then admin-only)",
        security=[],
    )
    @ns.expect(user_create, validate=True)
    @ns.response(201, "User created successfully", user_model)
    def post(self):
        data = request.json
        first = data.get("first_name", "").strip()
        last = data.get("last_name", "").strip()
        email = data.get("email", "").strip().lower()
        pwd = data.get("password", "")

        claims = get_jwt()
        caller_is_admin = claims.get("is_admin", False)

        is_admin = bool(data.get("is_admin", False)) if caller_is_admin else False

        if not first or not last:
            ns.abort(400, "First and last name required")
        if not EMAIL_RE.match(email):
            ns.abort(400, "Invalid email address")
        if any(u.email.lower() == email for u in facade.list_users()):
            ns.abort(400, "Email already in use")
        if len(pwd) < 8:
            ns.abort(400, "Password must be at least 8 characters")

        user = facade.create_user(
            {
                "first_name": first,
                "last_name": last,
                "email": email,
                "password": pwd,
                "is_admin": is_admin,
            }
        )
        return marshal(user, user_model), 201


@ns.route("/users/<string:user_id>")
@ns.response(404, "User not found")
@ns.doc(tags=["Users"])
class UserResource(Resource):
    @jwt_required()
    @ns.doc(
        "get_user",
        description="Retrieve user details (Self or Admin)",
        security="BearerAuth",
    )
    @ns.marshal_with(user_model)
    def get(self, user_id):
        user = facade.get_user(user_id)
        if not user:
            ns.abort(404, f"User {user_id} not found")
        claims = get_jwt()
        caller = get_jwt_identity()
        if caller != user_id and not claims.get("is_admin"):
            ns.abort(403, "Unauthorized action")
        return user, 200

    @jwt_required()
    @ns.doc(
        "update_user",
        description="Update user profile (Self or Admin)",
        security="BearerAuth",
    )
    @ns.expect(user_update, validate=True)
    def put(self, user_id):
        user = facade.get_user(user_id)
        if not user:
            ns.abort(404, f"User {user_id} not found")
        claims = get_jwt()
        caller = get_jwt_identity()
        if caller != user_id and not claims.get("is_admin"):
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

        updated = facade.update_user(user_id, updates)
        return marshal(updated, user_model), 200

    @jwt_required()
    @ns.doc(
        "delete_user",
        description="Delete a user (Self or Admin)",
        security="BearerAuth",
    )
    @ns.response(204, "User deleted")
    def delete(self, user_id):
        user = facade.get_user(user_id)
        if not user:
            ns.abort(404, f"User {user_id} not found")
        claims = get_jwt()
        caller = get_jwt_identity()
        if caller != user_id and not claims.get("is_admin"):
            ns.abort(403, "Unauthorized action")
        facade.delete_user(user_id)
        return "", 204


@ns.route("/<string:user_id>/bookings")
@ns.response(404, "User not found")
class UserBookings(Resource):
    @jwt_required()
    @ns.doc(
        "list_user_bookings",
        description="List all bookings made by a user (Self or Admin)",
        security="BearerAuth",
    )
    @ns.marshal_list_with(booking_output)  # import booking_output from bookings.py
    @ns.response(403, "Unauthorized action")
    def get(self, user_id):
        """
        Retrieve all bookings for the given user.
        """
        # 1) fetch user, abort if missing
        user = facade.get_user(user_id)
        if not user:
            ns.abort(404, f"User {user_id} not found")

        # 2) enforce self-or-admin
        caller = get_jwt_identity()
        claims = get_jwt()
        if caller != user_id and not claims.get("is_admin"):
            ns.abort(403, "Unauthorized action")

        # 3) list bookings via facade
        bookings = facade.list_bookings_for_user(user_id)
        # 4) return marshaled
        return bookings, 200
