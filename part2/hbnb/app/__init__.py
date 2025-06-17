# app/__init__.py
from flask import Flask
from app.api import bp as api_bp
from app.services.facade import HBNBFacade

def create_app():
    app = Flask(__name__)

    # Attach your facade (user-only for now)
    app.config['FACADE'] = HBNBFacade()

    # Mount the entire RESTX Api under /api/v1
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    return app
