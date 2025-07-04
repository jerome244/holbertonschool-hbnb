import sys
from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from .api.v1 import users
from .api.v1 import hosts

# Load configuration classes from config.py
from config import Config

# Instantiate facade and bcrypt
from .services.facade import HBnBFacade
facade = HBnBFacade()

bcrypt = Bcrypt()
jwt    = JWTManager()

# ----------------------- module aliasing ----------------------- #
from .models import place as _place_mod
sys.modules["place"] = _place_mod
from .models import amenity as _amenity_mod
sys.modules["amenity"] = _amenity_mod
from .models import user as _user_mod
sys.modules["user"] = _user_mod
import app.models.booking as _bk_mod
sys.modules["booking"] = _bk_mod
import app.models.review as _rv_mod
sys.modules["review"] = _rv_mod

# ----------------------- API namespace imports ----------------------- #
from .api.v1.ns import ns as users_ns
from .api.v1.places import ns as places_ns
from .api.v1.amenities import ns as amenities_ns
from .api.v1.bookings import ns as bookings_ns
from .api.v1.reviews import ns as reviews_ns
from .api.v1.auth import ns as auth_ns
from .api.v1.admins import ns as admin_ns

# ----------------------- application factory ----------------------- #
def create_app(config_class: str = "config.DevelopmentConfig") -> Flask:
    """
    Factory to create and configure the HBnB Flask application.

    Args:
        config_class (str): Import path for the configuration class.

    Returns:
        Flask: Configured Flask application.
    """
    # Instantiate Flask
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_class)

    # Initialize bcrypt and JWT
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Define Swagger authorizations for JWT
    authorizations = {
        'BearerAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"'
        }
    }

    # Initialize RESTX API with security definitions
    api = Api(
        app,
        version="1.0",
        title="HBnB API",
        description="HBnB Application API",
        doc="/api/v1/",
        authorizations=authorizations,
        security='BearerAuth'
    )

    # Register namespaces
    api.add_namespace(users_ns,     path="/api/v1/users")
    api.add_namespace(places_ns,    path="/api/v1/places")
    api.add_namespace(amenities_ns, path="/api/v1/amenities")
    api.add_namespace(bookings_ns,  path="/api/v1/bookings")
    api.add_namespace(reviews_ns,   path="/api/v1/reviews")
    api.add_namespace(auth_ns,      path="/api/v1/auth")
    api.add_namespace(admin_ns,     path="/api/v1/admins")

    return app
