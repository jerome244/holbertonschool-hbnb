from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.facade import facade

host_ns = Namespace('hosts', description='Host operations')
host_model = host_ns.model('Host', {
    'id': fields.String(readonly=True),
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True)
})

@host_ns.route('/')
class HostList(Resource):
    @host_ns.marshal_list_with(host_model)
    def get(self):
        return facade.get_all_hosts()

    @host_ns.expect(host_model, validate=True)
    @host_ns.marshal_with(host_model, code=201)
    def post(self):
        try:
            return facade.create_host(request.get_json()), 201
        except ValueError as e:
            host_ns.abort(400, str(e))

@host_ns.route('/<string:id>')
@host_ns.response(404, 'Host not found')
class HostResource(Resource):
    @host_ns.marshal_with(host_model)
    def get(self, id):
        try:
            return facade.get_host(id)
        except KeyError as e:
            host_ns.abort(404, str(e))

    @host_ns.expect(host_model, validate=True)
    @host_ns.marshal_with(host_model)
    def put(self, id):
        try:
            return facade.update_host(id, request.get_json())
        except KeyError as e:
            host_ns.abort(404, str(e))
        except ValueError as e:
            host_ns.abort(400, str(e))

    @host_ns.response(204, 'Host deleted')
    def delete(self, id):
        try:
            facade.delete_host(id)
            return '', 204
        except KeyError as e:
            host_ns.abort(404, str(e))
