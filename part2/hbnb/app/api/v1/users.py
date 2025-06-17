# app/api/v1/users.py
from flask import Blueprint, current_app, request, jsonify, abort
from http import HTTPStatus

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['POST'])
def create_user():
    payload = request.get_json() or {}
    required = {'first_name', 'last_name', 'email'}
    if not required.issubset(payload):
        missing = required - payload.keys()
        abort(HTTPStatus.BAD_REQUEST,
              description=f"Missing fields: {', '.join(missing)}")

    try:
        user = current_app.config['FACADE'].create_user(payload)
    except ValueError as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))

    return jsonify(user.to_dict()), HTTPStatus.CREATED

@users_bp.route('/', methods=['GET'])
def list_users():
    users = current_app.config['FACADE'].list_users()
    return jsonify([u.to_dict() for u in users]), HTTPStatus.OK

@users_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    user = current_app.config['FACADE'].get_user(user_id)
    if not user:
        abort(HTTPStatus.NOT_FOUND)
    return jsonify(user.to_dict()), HTTPStatus.OK

@users_bp.route('/<user_id>', methods=['PUT', 'PATCH'])
def update_user(user_id):
    payload = request.get_json() or {}
    try:
        user = current_app.config['FACADE'].update_user(user_id, payload)
    except ValueError as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))
    if not user:
        abort(HTTPStatus.NOT_FOUND)
    return jsonify(user.to_dict()), HTTPStatus.OK

@users_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    if not current_app.config['FACADE'].delete_user(user_id):
        abort(HTTPStatus.NOT_FOUND)
    return '', HTTPStatus.NO_CONTENT
