from flask import Flask
from flask_restx import Api, Namespace, Resource, fields
from app.services.facade import HBnBFacade

# Initialize application and facade
app = Flask(__name__)
api = Api(
    app,
    version='1.0',
    title='HBnB API',
    description='HBnB Application API',
    doc='/api/v1/'
)
facade = HBnBFacade()

# Define the User namespace and models
user_ns = Namespace('users', description='User operations')
user_model = user_ns.model('User', {
    'id': fields.String(readonly=True, description='Unique identifier'),
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'email': fields.String(required=True, description='Email address'),
    'is_admin': fields.Boolean(description='Admin flag')
})

# Resource for list and creation
@user_ns.route('/')
class UserList(Resource):
    @user_ns.doc('list_users')
    @user_ns.marshal_list_with(user_model)
    def get(self):
        """List all users"""
        return facade.get_all_users()

    @user_ns.doc('create_user')
    @user_ns.expect(user_model, validate=True)
    @user_ns.marshal_with(user_model, code=201)
    def post(self):
        """Create a new user"""
        data = api.payload
        try:
            user = facade.create_user(data)
            return user, 201
        except ValueError as e:
            api.abort(400, str(e))

# Resource for single user operations
@user_ns.route('/<string:id>')
@user_ns.response(404, 'User not found')
@user_ns.param('id', 'The user identifier')
class UserResource(Resource):
    @user_ns.doc('get_user')
    @user_ns.marshal_with(user_model)
    def get(self, id):
        """Fetch a user given its identifier"""
        try:
            return facade.get_user(id)
        except KeyError as e:
            api.abort(404, str(e))

    @user_ns.doc('delete_user')
    @user_ns.response(204, 'User deleted')
    def delete(self, id):
        """Delete a user given its identifier"""
        try:
            facade.delete_user(id)
            return '', 204
        except KeyError as e:
            api.abort(404, str(e))

    @user_ns.doc('update_user')
    @user_ns.expect(user_model, validate=True)
    @user_ns.marshal_with(user_model)
    def put(self, id):
        """Update a user given its identifier"""
        data = api.payload
        try:
            user = facade.update_user(id, data)
            return user
        except KeyError as e:
            api.abort(404, str(e))
        except ValueError as e:
            api.abort(400, str(e))

# Register namespace
api.add_namespace(user_ns, path='/api/v1/users')

if __name__ == '__main__':
    app.run(debug=True)
