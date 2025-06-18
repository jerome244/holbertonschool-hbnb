# app/api/users.py
import re
from flask_restx import Namespace, Resource, fields
from app import facade

ns = Namespace('users', description='Operations on user accounts')

# Full model: used for GET responses and POST/PUT bodies
user_model = ns.model('User', {
    'id':         fields.String(readonly=True, description='Unique ID'),
    'first_name': fields.String(required=True, description='First name'),
    'last_name':  fields.String(required=True, description='Last name'),
    'email':      fields.String(required=True, description='Email address'),
    'is_admin':   fields.Boolean(description='Admin flag'),
})

# Partial model: used for PATCH bodies (all fields optional)
patch_user_model = ns.model('UserPatch', {
    'first_name': fields.String(description='First name'),
    'last_name':  fields.String(description='Last name'),
    'email':      fields.String(description='Email address'),
    'is_admin':   fields.Boolean(description='Admin flag'),
})

EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

@ns.route('/')
class UserList(Resource):
    @ns.marshal_list_with(user_model)
    def get(self):
        """List all users"""
        return facade.list_users()

    @ns.expect(user_model, validate=True)
    @ns.marshal_with(user_model, code=201)
    def post(self):
        """Create a new user"""
        payload = ns.payload
        email = payload.get('email', '').strip()

        # Validate email format
        if not EMAIL_RE.match(email):
            ns.abort(400, "Invalid email address")

        # Enforce uniqueness
        if any(u.email.lower() == email.lower() for u in facade.list_users()):
            ns.abort(400, "Email already in use")

        new_user = facade.create_user(payload)
        return new_user, 201

@ns.route('/<string:user_id>')
@ns.response(404, 'User not found')
class UserDetail(Resource):
    @ns.marshal_with(user_model)
    def get(self, user_id):
        """Fetch a user by ID"""
        user = facade.get_user(user_id)
        if not user:
            ns.abort(404, f"User {user_id} doesn't exist")
        return user

    @ns.expect(patch_user_model, validate=True)
    @ns.marshal_with(user_model)
    def patch(self, user_id):
        """Partially update an existing user"""
        payload = ns.payload
        user = facade.get_user(user_id)
        if not user:
            ns.abort(404, f"User {user_id} doesn't exist")

        # If updating email, validate format & uniqueness
        if 'email' in payload:
            email = payload['email'].strip()
            if not EMAIL_RE.match(email):
                ns.abort(400, "Invalid email address")
            if any(u.email.lower() == email.lower() and u.id != user_id
                   for u in facade.list_users()):
                ns.abort(400, "Email already in use")

        updated = facade.update_user(user_id, payload)
        return updated

    @ns.response(204, 'User deleted')
    def delete(self, user_id):
        """Delete a user"""
        if not facade.get_user(user_id):
            ns.abort(404, f"User {user_id} doesn't exist")
        facade.delete_user(user_id)
        return '', 204
