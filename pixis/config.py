"""
Contains all of the variables that the user can modify
"""


from pathlib import Path


class Config():
    APPLICATION = 'flask'
    BUILD = None
    SPEC = 'swagger.yaml'
    TEMPLATES = 'templates'
    OUT = 'build'

    PATH_BUILD = None
    PATH_SPEC = str(Path(SPEC))
    PATH_TEMPLATES = str(Path(TEMPLATES))
    PATH_OUT = str(Path(OUT))

    SPEC_DICT = {}

    LANGUAGE = None
    IMPLEMENTATION = 'flask'

    FLASK_SERVER_NAME = 'flask_server'
    FLASK_SERVER_OUTPUT = str(Path(PATH_OUT) / FLASK_SERVER_NAME)
