import sys
from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
import click
from flask.cli import with_appcontext

# standalone DB instance
from .database import db

# Load configuration classes from config.py
from config import Config

# extensions that don’t trigger circular imports
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

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Create all database tables and create a default admin user if no users exist."""
    # Import all models so SQLAlchemy knows about them
    from app.models.user import User
    from app.models.place import Place
    from app.models.review import Review
    from app.models.amenity import Amenity
    from app.models.host import Host
    from app.models.booking import Booking

    # Create all tables
    db.create_all()

    # Check if there are any users in the users table
    admin_user = User.query.filter_by(email="admin@hbnb.io").first()

    if not admin_user:
        # Create a default admin user if no admin exists
        admin_user = User(
            first_name="Admin",
            last_name="User",
            email="admin@hbnb.io",
            is_admin=True
        )
        # Hash the password before saving it
        admin_user.set_password("admin1234")

        # Add the user to the database and commit
        db.session.add(admin_user)
        db.session.commit()
        click.echo('✅ Admin user created.')
    else:
        click.echo('✅ Admin user already exists.')

    click.echo('✅ Database initialized.')

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
    app.debug = True

    # Load configuration
    app.config.from_object(config_class)

    # Bind the shared SQLAlchemy instance
    db.init_app(app)

    # Initialize other extensions
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Now it’s safe to import & instantiate anything that uses `app` or `db`
    from .services.facade import HBnBFacade
    facade = HBnBFacade()

    # Register RESTX namespaces
    authorizations = {
        'BearerAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"'
        }
    }
    api = Api(
        app,
        version="1.0",
        title="HBnB API",
        description="HBnB Application API",
        doc="/api/v1/",
        authorizations=authorizations,
        security='BearerAuth'
    )
    
    from app.api.v1 import users, hosts, places, amenities, bookings, reviews, auth, admins
    
    # ----------------------- API namespace imports ----------------------- #
    from .api.v1.ns import ns as users_ns
    from .api.v1.places import ns as places_ns
    from .api.v1.amenities import ns as amenities_ns
    from .api.v1.bookings import ns as bookings_ns
    from .api.v1.reviews import ns as reviews_ns
    from .api.v1.auth import ns as auth_ns
    from .api.v1.admins import ns as admin_ns

    api.add_namespace(users_ns,     path="/api/v1/users")
    api.add_namespace(places_ns,    path="/api/v1/places")
    api.add_namespace(amenities_ns, path="/api/v1/amenities")
    api.add_namespace(bookings_ns,  path="/api/v1/bookings")
    api.add_namespace(reviews_ns,   path="/api/v1/reviews")
    api.add_namespace(auth_ns,      path="/api/v1/auth")
    api.add_namespace(admin_ns,     path="/api/v1/admins")

    app.cli.add_command(init_db_command)

    return app
