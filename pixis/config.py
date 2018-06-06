"""
Contains all of the variables that the user can modify
"""


class Config():
    """Provides variables that pixis uses to configure code generation

    Attributes:
        BUILD: A string that describes relative path to build file
        SPEC: A string that describes relative path to specification file
        TEMPLATES: A string that describes relative path to templates directory
        OUTPUT: A string that describes relative path to output directory
        PARENT: A string that describes relative path to output directory's parent directory (Determined from OUTPUT)
        FLASK_SERVER_NAME: A string that describes the directory name for default Flask server implementation
        VERBOSE: A boolean for Verbose mode (TODO)
        OVERWRITE: A boolean for Force Overwrite
        PROTECTED: A list of strings that describe file names or regular expressions for files that Pixis should never overwrite (even if OVERWRITE is True)
        LANGUAGE: A subclass of Language (Defined from IMPLEMENTATION)
        IMPLEMENTATION: A string that describes a supported implementation {'flask', 'angular2'} OR a subclass of Implementation
        SPEC_DICT: raw specification dictionary
        _checksums: Internal Pixis map for current file checksums
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
    OVERWRITE = False
    PROTECTED = []

    LANGUAGE = None
    IMPLEMENTATION = 'flask'

    SPEC_DICT = {}
    _checksums = {}


class Language():
    """
    Language - base abstract class; provides default methods for specific language classes to override
    """
    @staticmethod
    def to_lang_type(string):
        return string

    @staticmethod
    def to_lang_style(string):
        return string

    @staticmethod
    def to_camel_case(string):
        s = string[0].lower()
        capitalize = False
        for char in string[1:-1]:
            if char == '_':
                capitalize = True
            else:
                if capitalize:
                    s += char.upper()
                else:
                    s += char
                capitalize = False
        return s + string[-1]

    @staticmethod
    def to_snake_case(string):
        s = string[0].lower()
        for char in string[1:-1]:
            if char.isupper():
                s += '_' + char.lower()
            else:
                s += char
        return s + string[-1].lower()


class Implementation():
    @staticmethod
    def process():
        pass

    @staticmethod
    def generate_custom():
        pass

    @staticmethod
    def generate_once():
        pass

    @staticmethod
    def generate_per_schema():
        pass

    @staticmethod
    def generate_per_tag():
        pass

    @staticmethod
    def stage_default_iterators():
        raise NotImplementedError()

    @staticmethod
    def lower_first(s):
        return s[:1].lower() + s[1:] if s else ''
