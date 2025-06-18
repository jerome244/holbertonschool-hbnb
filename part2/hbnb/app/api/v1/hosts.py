import re
from flask_restx import Namespace, Resource, fields
from app import facade

ns = Namespace('hosts', description='Host operations')

EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

host_model = ns.model('Host', {
    'id':         fields.String(readonly=True),
    'first_name': fields.String(required=True),
    'last_name':  fields.String(required=True),
    'email':      fields.String(required=True),
})

@ns.route('/')
class HostList(Resource):
    @ns.marshal_list_with(host_model)
    def get(self):
        """List all hosts"""
        return facade.list_hosts()

    @ns.expect(host_model, validate=True)
    @ns.marshal_with(host_model, code=201)
    def post(self):
        """Create a new host"""
        payload = ns.payload
        email = payload.get('email', '').strip()
        if not EMAIL_RE.match(email):
            ns.abort(400, "Invalid email address")
        if any(h.email.lower() == email.lower() for h in facade.list_hosts()):
            ns.abort(400, "Email already in use")
        host = facade.create_host(payload)
        return host, 201

@ns.route('/<string:host_id>')
@ns.response(404, 'Host not found')
class HostDetail(Resource):
    @ns.marshal_with(host_model)
    def get(self, host_id):
        """Fetch a host by ID"""
        host = facade.get_host(host_id)
        if not host:
            ns.abort(404, f"Host {host_id} doesn't exist")
        return host

    @ns.expect(host_model, validate=True)
    @ns.marshal_with(host_model)
    def patch(self, host_id):
        """Partially update a host"""
        payload = ns.payload
        host = facade.get_host(host_id)
        if not host:
            ns.abort(404, f"Host {host_id} doesn't exist")
        if 'email' in payload:
            email = payload['email'].strip()
            if not EMAIL_RE.match(email):
                ns.abort(400, "Invalid email address")
            if any(h.email.lower()==email.lower() and h.id!=host_id for h in facade.list_hosts()):
                ns.abort(400, "Email already in use")
        updated = facade.update_host(host_id, payload)
        return updated

    @ns.response(204, 'Host deleted')
    def delete(self, host_id):
        """Delete a host"""
        if not facade.get_host(host_id):
            ns.abort(404, f"Host {host_id} doesn't exist")
        facade.delete_host(host_id)
        return '', 204
