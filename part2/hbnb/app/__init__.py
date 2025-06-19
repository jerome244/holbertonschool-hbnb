import sys
from flask import Flask
from flask_restx import Api

# 1) Instantiate facade before aliasing to avoid circular imports
from .services.facade import HBnBFacade

facade = HBnBFacade()

# 2) Alias bare-module imports so top-level modules (booking, review, etc.) are found
from .models import place as _place_mod

sys.modules["place"] = _place_mod
from .models import amenity as _amenity_mod

sys.modules["amenity"] = _amenity_mod
from .models import user as _user_mod

sys.modules["user"] = _user_mod
# alias booking and review so `import booking` / `from booking import Booking` works
import app.models.booking as _bk_mod

sys.modules["booking"] = _bk_mod
import app.models.review as _rv_mod

sys.modules["review"] = _rv_mod

# 3) Register API namespaces
from .api.v1.users import ns as users_ns
from .api.v1.hosts import ns as hosts_ns
from .api.v1.places import ns as places_ns
from .api.v1.amenities import ns as amenities_ns
from .api.v1.bookings import ns as bookings_ns
from .api.v1.reviews import ns as reviews_ns


def create_app():
    app = Flask(__name__)
    api = Api(
        app,
        version="1.0",
        title="HBnB API",
        description="HBnB Application API",
        doc="/api/v1/",
    )

    api.add_namespace(users_ns, path="/api/v1/users")
    api.add_namespace(hosts_ns, path="/api/v1/hosts")
    api.add_namespace(places_ns, path="/api/v1/places")
    api.add_namespace(amenities_ns, path="/api/v1/amenities")
    api.add_namespace(bookings_ns, path="/api/v1/bookings")
    api.add_namespace(reviews_ns, path="/api/v1/reviews")

    return app
