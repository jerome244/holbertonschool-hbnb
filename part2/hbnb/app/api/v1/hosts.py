# hosts.py

from flask_restx import Namespace, Resource, fields
from app import facade
# new import for Place serialization model
from app.api.v1.places import place_model

ns = Namespace('hosts', description='Host management')

host_model = ns.model('Host', {
    'id':         fields.String(readonly=True),
    'first_name': fields.String(required=True),
    'last_name':  fields.String(required=True),
    'email':      fields.String(required=True),
    'is_admin':   fields.Boolean,
})

patch_model = ns.model('HostPatch', {
    'first_name': fields.String,
    'last_name':  fields.String,
    'email':      fields.String,
    'is_admin':   fields.Boolean,
})

@ns.route('')
class HostList(Resource):
    @ns.marshal_list_with(host_model)
    def get(self):
        return facade.list_hosts()

    @ns.expect(host_model, validate=True)
    @ns.marshal_with(host_model, code=201)
    def post(self):
        return facade.create_host(ns.payload), 201

@ns.route('/<string:host_id>')
class HostDetail(Resource):
    @ns.marshal_with(host_model)
    def get(self, host_id):
        return facade.get_host(host_id) or ns.abort(404)

    @ns.expect(patch_model, validate=True)
    @ns.marshal_with(host_model)
    def patch(self, host_id):
        return facade.update_host(host_id, ns.payload) or ns.abort(404)

    def delete(self, host_id):
        if not facade.get_host(host_id):
            ns.abort(404)
        facade.delete_host(host_id)
        return '', 204

@ns.route('/<string:host_id>/rating')
class HostRating(Resource):
    def get(self, host_id):
        host = facade.get_host(host_id) or ns.abort(404)
        return {'host_rating': host.rating}

# ---- NEW: Owned Places ----
@ns.route('/<string:host_id>/owned_places')
class HostOwnedPlaces(Resource):
    @ns.marshal_list_with(place_model)
    def get(self, host_id):
        """
        Return all Place objects owned by this host.
        """
        places = facade.get_host_owned_places(host_id)
        if places is None:
            ns.abort(404, f"Host {host_id} not found")
        return places
