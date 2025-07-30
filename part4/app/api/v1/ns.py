from flask_restx import Namespace

ns = Namespace(
    "users", description="Operations on user and host accounts", security="BearerAuth"
)
