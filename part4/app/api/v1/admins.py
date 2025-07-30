from flask_restx import Namespace, Resource, marshal
from flask_jwt_extended import jwt_required, get_jwt
from flask import request
from app.services import facade
from .models import user_model, user_create, user_update, amenity_input, amenity_model
import re

ns = Namespace("admin", description="Admin operations")

# Email validation regex
EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

# -------- Entites Models -------- #

user_model = user_model(ns)
user_create = user_create(ns)
user_update = user_update(ns)

amenity_model = amenity_model(ns)
amenity_input = amenity_input(ns)

# -------- Resources -------- #


@ns.route("/users/")
class AdminUserCreate(Resource):
    @ns.expect(user_create, validate=True)
    @jwt_required()
    @ns.response(201, "User created successfully", user_model)
    def post(self):
        claims = get_jwt()
        if not claims.get("is_admin"):
            ns.abort(403, "Admin provileges required")

        data = request.json

        first = data.get("first_name", "").strip()
        last = data.get("last_name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        is_admin = data.get("is_admin", False)

        # ------------ Data validation ------------#

        if not first or not last:
            ns.abort(400, "First and last name are required")
        if not EMAIL_RE.match(email):
            ns.abort(400, "Invalid email address")
        if facade.get_user_by_email(email):
            ns.abort(400, "Email is already in use")
        if len(password) < 8:
            ns.abort(400, "Password must be at least 8 characters")

        # Not setting password here to pass it through class validation
        user = facade.create_user(
            {
                "first_name": first,
                "last_name": last,
                "email": email,
                "password": password,
                "is_admin": is_admin,
            }
        )

        return marshal(user, user_model), 201


@ns.route("/users/<user_id>")
class AdminUserResource(Resource):
    @ns.expect(user_create, validate=True)
    @jwt_required()
    def put(self, user_id):
        current_user = get_jwt()
        if not current_user.get("is_admin"):
            return {"error": "Admin privileges required"}, 403

        user = facade.get_user(user_id)
        if not user:
            ns.abort(404, "User not found")

        data = request.json

        first = data.get("first_name")
        last = data.get("last_name")
        email = data.get("email")
        password = data.get("password")
        is_admin = data.get("is_admin")

        # ------------ Data validation ------------#

        if email:
            existing_user = facade.get_user_by_email(email)
            if existing_user and existing_user.id != user_id:
                return {"error": "Email is already in use"}, 400
            if not EMAIL_RE.match(email):
                ns.abort(400, "Invalid email address")
            email = email.strip().lower()

        if password:
            if len(password) < 8:
                ns.abort(400, "Password must be at least 8 characters")

        user_data = {}
        if first:
            user_data["first_name"] = first.strip()
        if last:
            user_data["last_name"] = last.strip()
        if email:
            user_data["email"] = email
        if is_admin is not None:
            user_data["is_admin"] = is_admin

        if password:
            user.password = password

        updated_user = facade.update_user(user_id, user_data)

        return marshal(updated_user, user_model)


@ns.route("/amenities/")
class AdminAmenityCreate(Resource):
    @ns.expect(amenity_input, validate=True)
    @jwt_required()
    @ns.marshal_with(amenity_model, code=201)
    def post(self):
        current_user = get_jwt()
        if not current_user.get("is_admin"):
            return {"error": "Admin privileges required"}, 403

        data = request.json
        name = data.get("name", "").strip()

        # Remake checks at API level to avoid
        # disgusting error 500 to be prompted to user
        if not name:
            ns.abort(400, "Amenity name is required")
        if len(name) < 1 or len(name) > 32:
            ns.abort(400, "Amenity name must be between 1 and 32 characters")

        amenity = facade.create_amenity({"name": name})

        return marshal(amenity, amenity_model), 201


@ns.route("/amenities/<amenity_id>")
class AdminAmenityModify(Resource):
    @ns.expect(user_update, validate=True)
    @jwt_required()
    @ns.marshal_with(user_model, code=200)
    def put(self, amenity_id):
        current_user = get_jwt()
        if not current_user.get("is_admin"):
            return {"error": "Admin privileges required"}, 403

        data = request.json
        new_name = data.get("name", "").strip()

        # ------------ Data validation ------------#

        if not new_name:
            ns.abort(400, "Amenity name is required")
        if len(new_name) < 1 or len(new_name) > 32:
            ns.abort(400, "Amenity name must be between 1 and 32 characters")

        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            ns.abort(404, "Amenity not found")

        # Checks is amenity already bears a similar name ar new_name
        amenities = facade.list_amenities()
        for amenity in amenities:
            if (
                amenity.name.strip().lower() == new_name.strip().lower()
                and amenity.id != amenity_id
            ):
                ns.abort(400, "Amenity name already exists")
                break

        amenity.name = new_name

        return amenity
