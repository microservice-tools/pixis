"""
Contains all of the variables that the user can modify
"""


class Config():
    # These are relative paths
    BUILD = None
    SPEC = 'swagger.yaml'
    TEMPLATES = 'templates'
    OUT = 'build'

    # These are not relative paths
    FLASK_SERVER_NAME = 'flask_server'

    LANGUAGE = None
    IMPLEMENTATION = 'flask'

    SPEC_DICT = {}
