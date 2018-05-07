import os

import yaml


class Config:
    APPLICATION = 'flask'
    BUILD = None
    SPEC = 'swagger.yaml'
    TEMPLATES = 'templates'
    OUT = 'build'

    PATH_BUILD = None
    PATH_SPEC = os.getcwd() + os.path.sep + SPEC
    PATH_TEMPLATES = os.getcwd() + os.path.sep + TEMPLATES
    PATH_OUT = os.getcwd() + os.path.sep + OUT

    SPEC_DICT = {}

    LANGUAGE = None
    IMPLEMENTATION = 'flask'

    # unsure what we're going to do with these
    FLASK_SERVER_NAME = 'flask_server'
    FLASK_SERVER_OUTPUT = PATH_OUT + os.path.sep + FLASK_SERVER_NAME
