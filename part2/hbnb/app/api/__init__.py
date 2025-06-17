# app/api/__init__.py
from flask import Blueprint

api_bp = Blueprint('api', __name__)

from app.api.v1.users import users_bp
api_bp.register_blueprint(users_bp, url_prefix='/users')
