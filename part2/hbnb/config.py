import os

<<<<<<< HEAD
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
=======

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True


config = {"development": DevelopmentConfig, "default": DevelopmentConfig}
>>>>>>> devJerome
