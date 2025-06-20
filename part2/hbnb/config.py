"""Stub file for documenting config.py without modifying the original source."""

# ----------------------- imports ----------------------- #
import os


# ----------------------- base config class ----------------------- #
class Config:
    """
    Base configuration class.

    SECRET_KEY (str): Flask secret key, defaults to 'default_secret_key' if env var not set.
    DEBUG (bool): Debug mode flag, defaults to False.
    """

    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    DEBUG = False


# ----------------------- development config ----------------------- #
class DevelopmentConfig(Config):
    """
    Development configuration class.

    Inherits from Config and enables debug mode.

    DEBUG (bool): Override base DEBUG to True.
    """

    DEBUG = True


# ----------------------- config mapping ----------------------- #
"""
Mapping of configuration environment names to their config classes.

- development: DevelopmentConfig
- default: DevelopmentConfig
"""
config = {"development": DevelopmentConfig, "default": DevelopmentConfig}
