"""
auth.py: Authentication endpoints for logging in users or hosts.
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, create_refresh_token
from app.services import facade

# Namespace for authentication
ns = Namespace("auth", description="Authentication operations")

# Model for login input
login_model = ns.model(
    "Login",
    {
        "email": fields.String(required=True, description="User or Host email"),
        "password": fields.String(required=True, description="Account password"),
    },
)

# Model for token output
token_model = ns.model(
    "Tokens",
    {
        "access_token": fields.String(description="JWT access token"),
        "refresh_token": fields.String(description="JWT refresh token"),
    },
)


@ns.route("/login")
class Login(Resource):
    @ns.doc("login_user_or_host")
    @ns.expect(login_model, validate=True)
    @ns.marshal_with(token_model)
    def post(self):
        """Authenticate user or host and return JWT tokens"""
        data = request.json
        email = data["email"].strip().lower()
        password = data["password"]

        # Try User first
        user = facade.get_user_by_email(email)
        if user and user.check_password(password):
            identity = str(user.id)  # ✅ cast to string
            claims = {"is_admin": user.is_admin}
            access_token = create_access_token(
                identity=identity, additional_claims=claims
            )
            refresh_token = create_refresh_token(
                identity=identity, additional_claims=claims
            )
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        # Try Host
        try:
            host = facade.get_host_by_email(email)
        except AttributeError:
            host = None

        if host and host.check_password(password):
            identity = str(host.id)  # ✅ cast to string
            claims = {"is_admin": host.is_admin}
            access_token = create_access_token(
                identity=identity, additional_claims=claims
            )
            refresh_token = create_refresh_token(
                identity=identity, additional_claims=claims
            )
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        # If neither matched
        ns.abort(401, "Invalid credentials")
