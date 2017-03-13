import os

# default config


class BaseConfig(object):
    DEBUG = False
    SECRET_KEY = os.urandom(24)
    DATABASE = 'data/todo.db'


class DevelopConfig(BaseConfig):
    DEBUG = True
