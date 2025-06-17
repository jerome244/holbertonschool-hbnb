# app/api/__init__.py
from flask import Blueprint
from flask_restx import Api

# 1) Create a Flask Blueprint
bp = Blueprint('api', __name__)

# 2) Wrap it in a RESTX Api for docs & validation
api = Api(
    bp,
    version='1.0',
    title='HBnB API',
    description='Holberton BNBay REST API',
    doc='/docs'    # Swagger UI at /api/v1/docs
)

# 3) Import and register your namespaces
from app.api.v1.users import ns as users_ns

api.add_namespace(users_ns, path='/users')
