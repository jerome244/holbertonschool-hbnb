from flask_restx import Namespace, Resource, fields
from app import facade

ns = Namespace('hosts', description='Host management')

# Define core Host fields
host_model = ns.model('Host', {
    'id':         fields.String(readonly=True),
    'first_name': fields.String(required=True),
    'last_name':  fields.String(required=True),
    'email':      fields.String(required=True),
    'is_admin':   fields.Boolean,
})

host_create = ns.clone('HostCreate', host_model, {})
host_patch  = ns.clone('HostPatch', host_model, {
    'first_name': fields.String,
    'last_name':  fields.String,
    'email':      fields.String,
    'is_admin':   fields.Boolean,
})

@ns.route('/')
class HostList(Resource):
    @ns.marshal_list_with(host_model)
    def get(self):
        return facade.list_hosts()

    @ns.expect(host_create, validate=True)
    @ns.marshal_with(host_model, code=201)
    def post(self):
        return facade.create_host(ns.payload), 201

@ns.route('/<string:host_id>')
class HostDetail(Resource):
    @ns.marshal_with(host_model)
    def get(self, host_id):
        host = facade.get_host(host_id) or ns.abort(404)
        return host

    @ns.expect(host_patch, validate=True)
    @ns.marshal_with(host_model)
    def patch(self, host_id):
        host = facade.update_host(host_id, ns.payload) or ns.abort(404)
        return host

    def delete(self, host_id):
        if not facade.get_host(host_id):
            ns.abort(404)
        facade.delete_host(host_id)
        return '', 204

# —— Expose aggregated host.rating ——

@ns.route('/<string:host_id>/rating')
class HostRating(Resource):
    def get(self, host_id):
        host = facade.get_host(host_id) or ns.abort(404, 'Host not found')
        return {'host_rating': host.rating}
