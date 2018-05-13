"""
Contains all of the variables that the user can modify
"""


import os
import yaml
from pathlib import Path

class Config():
    APPLICATION = 'flask'
    BUILD = None
    SPEC = 'swagger.yaml'
    TEMPLATES = 'templates'
    OUT = 'build'

    PATH_BUILD = None
    PATH_SPEC = str(Path(SPEC))
    # os.getcwd() + os.path.sep + SPEC
    # PATH_TEMPLATES = os.getcwd() + os.path.sep + TEMPLATES
    PATH_TEMPLATES = str(Path(TEMPLATES))
    PATH_OUT = str(Path(OUT))

    SPEC_DICT = {}

    LANGUAGE = None
    IMPLEMENTATION = 'flask'

    #: unsure what we're going to do with these
    FLASK_SERVER_NAME = 'flask_server'
    FLASK_SERVER_OUTPUT = str(Path(PATH_OUT) / FLASK_SERVER_NAME)
