"""
hosts.py: API endpoints for Host resources.

This module defines the Flask-RESTX namespace, data models, and resource classes
for listing, creating, retrieving, updating, deleting hosts, fetching ratings,
and listing owned places.
"""

from flask_restx import Namespace, Resource, fields
from app import facade

# ----------------------- namespace ----------------------- #
ns = Namespace("hosts", description="Host management")

# ----------------------- data models ----------------------- #
host_model = ns.model(
    "Host",
    {
        "id": fields.String(readOnly=True, description="Unique host identifier"),
        "first_name": fields.String(required=True, description="Host's first name"),
        "last_name": fields.String(required=True, description="Host's last name"),
        "email": fields.String(required=True, description="Host's email address"),
        "is_admin": fields.Boolean(description="Host admin status"),
    },
)

create_host_model = ns.model(
    "HostCreate",
    {
        "first_name": fields.String(required=True, description="Host's first name"),
        "last_name": fields.String(required=True, description="Host's last name"),
        "email": fields.String(required=True, description="Host's email address"),
        "is_admin": fields.Boolean(required=True, description="Host admin status"),
    },
)


# ----------------------- resource classes ----------------------- #
@ns.route("")
class HostList(Resource):
    """
    Resource for listing all hosts and creating new hosts.
    """

    @ns.marshal_list_with(host_model)
    def get(self):
        """
        List all hosts.

        Returns:
            list: A list of all Host objects.
        """
        return facade.list_hosts()

    @ns.expect(create_host_model, validate=True)
    @ns.marshal_with(host_model, code=201)
    def post(self):
        """
        Create a new host.

        Validates payload, enforces unique email, and returns the created Host.

        Returns:
            tuple: Created Host object and HTTP 201 status.
        """
        data = ns.payload

        # Normalize & enforce unique email
        email = data["email"].strip().lower()
        if any(h.email.lower() == email for h in facade.list_hosts()):
            ns.abort(400, f"Host with email {email} already exists")

        # Delegate to facade; returned Host will have server-generated ID
        return facade.create_host(data), 201


@ns.route("/<string:host_id>")
class HostDetail(Resource):
    """
    Resource for retrieving, updating, and deleting a specific host.
    """

    @ns.marshal_with(host_model)
    def get(self, host_id):
        """
        Fetch a host by ID.

        Args:
            host_id (str): Unique identifier of the host.

        Returns:
            Host: The requested Host object.
        """
        host = facade.get_host(host_id)
        if not host:
            ns.abort(404, f"Host {host_id} not found")
        return host

    @ns.expect(host_model, validate=True)
    @ns.marshal_with(host_model)
    def patch(self, host_id):
        """
        Partially update a host.

        Args:
            host_id (str): Unique identifier of the host.

        Enforces unique email if changed and returns the updated Host.
        """
        data = ns.payload
        host = facade.get_host(host_id)
        if not host:
            ns.abort(404, f"Host {host_id} not found")

        # If email is changing, check duplicates
        if "email" in data:
            new_email = data["email"].strip().lower()
            if any(
                h.email.lower() == new_email and h.id != host_id
                for h in facade.list_hosts()
            ):
                ns.abort(400, f"Email {new_email} already in use")
            data["email"] = new_email

        updated = facade.update_host(host_id, data)
        return updated or ns.abort(404)

    def delete(self, host_id):
        """
        Delete a host.

        Args:
            host_id (str): Unique identifier of the host.

        Returns:
            tuple: Empty response and HTTP 204 status.
        """
        if not facade.get_host(host_id):
            ns.abort(404, f"Host {host_id} not found")
        facade.delete_host(host_id)
        return "", 204


@ns.route("/<string:host_id>/rating")
class HostRating(Resource):
    """
    Resource for fetching a host’s rating.
    """

    def get(self, host_id):
        """
        Get the rating for a specific host.

        Args:
            host_id (str): Unique identifier of the host.

        Returns:
            dict: Mapping with 'host_rating' as key and rating value.
        """
        host = facade.get_host(host_id) or ns.abort(404, f"Host {host_id} not found")
        return {"host_rating": host.rating}


# ----------------------- owned places endpoint ----------------------- #
from app.api.v1.places import place_model


@ns.route("/<string:host_id>/owned_places")
class HostOwnedPlaces(Resource):
    """
    Resource for listing all places owned by a specific host.
    """

    @ns.marshal_list_with(place_model)
    def get(self, host_id):
        """
        List all places owned by the host.

        Args:
            host_id (str): Unique identifier of the host.

        Returns:
            list: A list of Place objects owned by the host.
        """
        places = facade.get_host_owned_places(host_id)
        if places is None:
            ns.abort(404, f"Host {host_id} not found")
        return places
