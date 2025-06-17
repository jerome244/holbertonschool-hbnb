# app/api/v1/users.py
from flask_restx import Namespace, Resource, fields, abort
from flask import current_app
from http import HTTPStatus

ns = Namespace('users', description='Operations on users')

# Input/output model for Swagger & automatic validation
user_model = ns.model('User', {
    'id':         fields.String(readOnly=True, description='UUID'),
    'first_name': fields.String(required=True, max_length=50),
    'last_name':  fields.String(required=True, max_length=50),
    'email':      fields.String(required=True, pattern='[^@]+@[^@]+\\.[^@]+'),
    'is_admin':   fields.Boolean(default=False),
    'created_at': fields.DateTime(readOnly=True),
    'updated_at': fields.DateTime(readOnly=True),
})

create_user_model = ns.model('NewUser', {
    'first_name': fields.String(required=True, max_length=50),
    'last_name':  fields.String(required=True, max_length=50),
    'email':      fields.String(required=True, pattern='[^@]+@[^@]+\\.[^@]+'),
    'is_admin':   fields.Boolean(default=False),
})

@ns.route('/')
class UserList(Resource):
    @ns.marshal_list_with(user_model)
    def get(self):
        """List all users"""
        return current_app.config['FACADE'].list_users()

    @ns.expect(create_user_model, validate=True)
    @ns.marshal_with(user_model, code=HTTPStatus.CREATED)
    def post(self):
        """Create a new user"""
        data = ns.payload
        try:
            user = current_app.config['FACADE'].create_user(data)
        except ValueError as e:
            ns.abort(HTTPStatus.BAD_REQUEST, str(e))
        return user, HTTPStatus.CREATED

@ns.route('/<string:user_id>')
@ns.response(HTTPStatus.NOT_FOUND, 'User not found')
class User(Resource):
    @ns.marshal_with(user_model)
    def get(self, user_id):
        """Fetch a user given its identifier"""
        user = current_app.config['FACADE'].get_user(user_id)
        if not user:
            abort(HTTPStatus.NOT_FOUND)
        return user

    @ns.expect(user_model, validate=True)
    @ns.marshal_with(user_model)
    def patch(self, user_id):
        """Update an existing user"""
        try:
            user = current_app.config['FACADE'].update_user(user_id, ns.payload)
        except ValueError as e:
            ns.abort(HTTPStatus.BAD_REQUEST, str(e))
        if not user:
            abort(HTTPStatus.NOT_FOUND)
        return user

    @ns.response(HTTPStatus.NO_CONTENT, 'User deleted')
    def delete(self, user_id):
        """Delete a user"""
        success = current_app.config['FACADE'].delete_user(user_id)
        if not success:
            abort(HTTPStatus.NOT_FOUND)
        return '', HTTPStatus.NO_CONTENT
