# app/api/v1/hosts.py

from flask_restx import Namespace, Resource, fields
from app import facade

ns = Namespace('hosts', description='Host management')

host_model = ns.model('Host', {
    'id':         fields.String(readOnly=True),
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
        """List all hosts"""
        return facade.list_hosts()

    @ns.expect(host_model, validate=True)
    @ns.marshal_with(host_model, code=201)
    def post(self):
        """Create a new host, error if email already in use"""
        data = ns.payload

        # Validate email uniqueness
        email = data.get('email', '').strip().lower()
        if any(h.email.lower() == email for h in facade.list_hosts()):
            ns.abort(400, f"Host with email {email} already exists")

        # Delegate creation
        return facade.create_host(data), 201

@ns.route('/<string:host_id>')
class HostDetail(Resource):
    @ns.marshal_with(host_model)
    def get(self, host_id):
        """Fetch a host by ID"""
        host = facade.get_host(host_id)
        if not host:
            ns.abort(404, f"Host {host_id} not found")
        return host

    @ns.expect(patch_model, validate=True)
    @ns.marshal_with(host_model)
    def patch(self, host_id):
        """Partially update a host, with email uniqueness enforced"""
        data = ns.payload
        host = facade.get_host(host_id)
        if not host:
            ns.abort(404, f"Host {host_id} not found")

        if 'email' in data:
            new_email = data['email'].strip().lower()
            # check other hosts for duplicate
            if any(h.email.lower() == new_email and h.id != host_id for h in facade.list_hosts()):
                ns.abort(400, f"Email {new_email} already in use")
            data['email'] = new_email

        updated = facade.update_host(host_id, data)
        return updated or ns.abort(404)

    def delete(self, host_id):
        """Delete a host"""
        if not facade.get_host(host_id):
            ns.abort(404, f"Host {host_id} not found")
        facade.delete_host(host_id)
        return '', 204

@ns.route('/<string:host_id>/rating')
class HostRating(Resource):
    def get(self, host_id):
        host = facade.get_host(host_id) or ns.abort(404)
        return {'host_rating': host.rating}

# Owned-places endpoint unchanged
from app.api.v1.places import place_model
@ns.route('/<string:host_id>/owned_places')
class HostOwnedPlaces(Resource):
    @ns.marshal_list_with(place_model)
    def get(self, host_id):
        places = facade.get_host_owned_places(host_id)
        if places is None:
            ns.abort(404, f"Host {host_id} not found")
        return places
