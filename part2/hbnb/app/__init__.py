# app/__init__.py
from flask import Flask
from app.api import api_bp
from app.services.facade import HBNBFacade

def create_app():
    app = Flask(__name__)
    # Single-facade for Task 2:
    app.config['FACADE'] = HBNBFacade()
    # Mount all /users routes under /api/v1
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    return app
