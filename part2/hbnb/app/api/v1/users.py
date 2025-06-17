from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.facade import facade

user_ns = Namespace('users', description='User operations')
user_model = user_ns.model('User', {
    'id': fields.String(readonly=True),
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True),
    'is_admin': fields.Boolean()
})

@user_ns.route('/')
class UserList(Resource):
    @user_ns.marshal_list_with(user_model)
    def get(self):
        return facade.get_all_users()

    @user_ns.expect(user_model, validate=True)
    @user_ns.marshal_with(user_model, code=201)
    def post(self):
        try:
            return facade.create_user(request.get_json()), 201
        except ValueError as e:
            user_ns.abort(400, str(e))

@user_ns.route('/<string:id>')
@user_ns.response(404, 'User not found')
class UserResource(Resource):
    @user_ns.marshal_with(user_model)
    def get(self, id):
        try:
            return facade.get_user(id)
        except KeyError as e:
            user_ns.abort(404, str(e))

    @user_ns.expect(user_model, validate=True)
    @user_ns.marshal_with(user_model)
    def put(self, id):
        try:
            return facade.update_user(id, request.get_json())
        except KeyError as e:
            user_ns.abort(404, str(e))
        except ValueError as e:
            user_ns.abort(400, str(e))

    @user_ns.response(204, 'User deleted')
    def delete(self, id):
        try:
            facade.delete_user(id)
            return '', 204
        except KeyError as e:
            user_ns.abort(404, str(e))
