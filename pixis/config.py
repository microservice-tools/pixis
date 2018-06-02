"""
Contains all of the variables that the user can modify
"""


class Config():
    """Provides variables that pixis uses to configure code generation

    Attributes:
        BUILD: Relative path to build file
        SPEC: Relative path to specification file
        TEMPLATES: Relative path to custom templates folder
        OUTPUT: Relative path to output directory
        PARENT: Relative path to parent of output directory
        FLASK_SERVER_NAME: Default server name for flask server implementation
        VERBOSE: Verbose setting
        LANGUAGE: Language class implementation
        IMPLEMENTATION: Implementation class implementation OR string of supported implementations ('flask', 'angular2')
        SPEC_DICT: raw specification dictionary
    """
    # DEFAULTS
    # These are relative paths
    BUILD = 'build.py'
    SPEC = 'swagger.yaml'
    TEMPLATES = 'templates'
    OUTPUT = 'build'
    PARENT = None

    FLASK_SERVER_NAME = 'flask_server'
    VERBOSE = False

    LANGUAGE = None
    IMPLEMENTATION = 'flask'

    SPEC_DICT = {}
    _checksums = {}
