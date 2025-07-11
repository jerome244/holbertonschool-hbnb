import os

# ----------------------- base config class ----------------------- #
class Config:
    """
    Base configuration class.

    SECRET_KEY (str): Flask secret key, defaults to 'default_secret_key' if env var not set.
    DEBUG (bool): Debug mode flag, defaults to False.
    JWT_SECRET_KEY (str): Signing key for JWTs, should be overridden via env var in production.
    """
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    DEBUG = False

    # Used by flask-jwt-extended to sign and verify tokens
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "change-me-to-a-secure-random-string-for-development"
    )

# ----------------------- development config ----------------------- #
class DevelopmentConfig(Config):
    """
    Development configuration class.

    Inherits from Config and enables debug mode.
    """
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# ----------------------- config mapping ----------------------- #
"""
Mapping of configuration environment names to their config classes.

- development: DevelopmentConfig
- default: DevelopmentConfig
"""
config = {
    "development": DevelopmentConfig,
    "default":     DevelopmentConfig
}
