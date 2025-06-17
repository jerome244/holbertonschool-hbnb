from flask import Flask
from flask_restx import Api
from app.api.v1.users import user_ns
from app.api.v1.hosts import host_ns

def create_app():
    app = Flask(__name__)
    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        doc='/api/v1/'             # Swagger UI at /api/v1/
    )
    api.add_namespace(user_ns, path='/api/v1/users')
    api.add_namespace(host_ns, path='/api/v1/hosts')
    return app
