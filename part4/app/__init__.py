import sys
from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
import click
from flask_migrate import Migrate
from flask.cli import with_appcontext
from flask_cors import CORS
from .routes.views import views  
from .routes.dashboard import dashboard
from .routes.places import places
from .routes.amenities import amenities
from .database import db
from config import Config
from app.routes.messages import messages_bp
from app.routes.admin import admin as admin_blueprint
from app.routes.reviews import reviews as reviews_blueprint
from .routes.bookings import bookings as bookings_routes_blueprint
from app.models.user import User
from .routes.place_photo import place_photo_bp
from app.routes.notifications import notifications_bp
from app.api.v1.notifications import notifications_ns

bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()
login_manager = LoginManager()

# Module aliasing as you have it...
from .models import place as _place_mod

sys.modules["place"] = _place_mod
from .models import amenity as _amenity_mod

sys.modules["amenity"] = _amenity_mod
from .models import user as _user_mod

sys.modules["user"] = _user_mod
from .models import message as _message_mod

sys.modules["message"] = _message_mod
import app.models.booking as _bk_mod

sys.modules["booking"] = _bk_mod
import app.models.review as _rv_mod

sys.modules["review"] = _rv_mod


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Create all database tables and a default admin user."""
    from app.models.user import User
    from app.models.place import Place
    from app.models.review import Review
    from app.models.amenity import Amenity
    from app.models.host import Host
    from app.models.booking import Booking

    db.create_all()

    admin_user = User.query.filter_by(email="admin@hbnb.io").first()

    if not admin_user:
        admin_user = User(
            first_name="Admin", last_name="User", email="admin@hbnb.io", is_admin=True
        )
        admin_user.set_password("admin1234")
        db.session.add(admin_user)
        db.session.commit()
        click.echo("✅ Admin user created.")
    else:
        click.echo("✅ Admin user already exists.")

    click.echo("✅ Database initialized.")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def create_app(config_class: str = "config.DevelopmentConfig") -> Flask:
    from .routes.auth import auth
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["JWT_SECRET_KEY"] = (
        "your-very-secret-key"  # Replace with a strong secret!
    )
    print("[DEBUG] Secret key:", app.config["SECRET_KEY"])

    jwt = JWTManager(app)
    app.debug = True
    CORS(app)
    

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Register blueprints with proper URL prefixes
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(views, url_prefix="")  # Public views
    app.register_blueprint(dashboard, url_prefix="/admin")  # Admin dashboard routes
    app.register_blueprint(places, url_prefix="/places")
    app.register_blueprint(messages_bp)
    app.register_blueprint(amenities, url_prefix="/amenities")  # Amenities routes
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(reviews_blueprint)
    app.register_blueprint(bookings_routes_blueprint)
    app.register_blueprint(place_photo_bp)
    app.register_blueprint(notifications_bp)

    # Register API namespaces under /api/v1/
    authorizations = {
        "BearerAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"',
        }
    }
    api = Api(
        app,
        version="1.0",
        title="HBnB API",
        description="HBnB Application API",
        doc="/api/v1/",
        authorizations=authorizations,
        security="BearerAuth",
    )

    from app.api.v1 import users, hosts, bookings, reviews, auth, admins, messages
    import app.api.v1.amenities as api_amenities
    import app.api.v1.places as api_places  # or another name, just not 'places'

    from .api.v1.ns import ns as users_ns
    from .api.v1.places import ns as places_ns
    from .api.v1.amenities import ns as amenities_ns
    from .api.v1.bookings import ns as bookings_ns
    from .api.v1.reviews import ns as reviews_ns
    from .api.v1.auth import ns as auth_ns
    from .api.v1.admins import ns as admin_ns
    from app.api.v1.notifications import notifications_ns

    api.add_namespace(users_ns, path="/api/v1/users")
    api.add_namespace(places_ns, path="/api/v1/places")
    api.add_namespace(amenities_ns, path="/api/v1/amenities")
    api.add_namespace(bookings_ns, path="/api/v1/bookings")
    api.add_namespace(reviews_ns, path="/api/v1/reviews")
    api.add_namespace(auth_ns, path="/api/v1/auth")
    api.add_namespace(admin_ns, path="/api/v1/admins")
    api.add_namespace(messages.ns, path="/api/v1/messages")
    api.add_namespace(notifications_ns, path="/api/v1/notifications")

    app.cli.add_command(init_db_command)

    from flask import session
    from app.models.user import User

    def inject_user():
        user_email = session.get("user")
        user = User.query.filter_by(email=user_email).first() if user_email else None
        return dict(user=user)

    app.context_processor(inject_user)

    return app
