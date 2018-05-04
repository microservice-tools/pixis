import importlib.util
import os
import re
import sys


class Configuration():
    def __init__(self):
        self.APPLICATION = 'flask'

        self.BUILD = None
        self.SPEC = 'swagger.yaml'
        self.TEMPLATES = 'templates'
        self.OUT = 'build'

        self.PATH_BUILD = None
        self.PATH_SPEC = os.getcwd() + os.path.sep + 'swagger.yaml'
        self.PATH_TEMPLATES = os.getcwd() + os.path.sep + 'templates'
        self.PATH_OUT = os.getcwd() + os.path.sep + 'build'

        self.SPEC_DICT = {}
        self.TEMPLATE_CONTEXT = {}

    def load_build_file(self, build_file):
        filepath = os.getcwd() + os.path.sep + build_file
        spec = importlib.util.spec_from_file_location(build_file[:-3], filepath)
        build_script = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build_script)

        self.APPLICATION = getattr(build_script, 'APPLICATION', 'flask')

        self.BUILD = build_file
        self.SPEC = getattr(build_script, 'SPEC', 'swagger.yaml')
        self.TEMPLATES = getattr(build_script, 'TEMPLATES', 'templates')
        self.OUT = getattr(build_script, 'OUT', 'build')

        self.PATH_BUILD = os.getcwd() + os.path.sep + build_file
        self.PATH_SPEC = os.getcwd() + os.path.sep + self.SPEC
        self.PATH_TEMPLATES = os.getcwd() + os.path.sep + self.TEMPLATES
        self.PATH_OUT = os.getcwd() + os.path.sep + self.OUT

    def load_spec_file(self, file_path):
        extension = os.path.splitext(file_path)[1][1:]
        if extension == 'yaml' or 'yml':
            with open(file_path) as f:
                try:
                    self.SPEC_DICT = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    print(e)
                    sys.exit()
        if extension == 'json':
            with open(file_path) as f:
                try:
                    self.SPEC_DICT = json.load(f)
                except ValueError as e:
                    print(e)
                    sys.exit()


EXT_REGEX = re.compile('x-.*')

BUILD = None
BUILD_FILE_PATH = None

SPEC = 'swagger.yaml'
SPEC_FILE_PATH = os.getcwd() + os.path.sep + SPEC

SPEC_DICT = None

TEMPLATE_CONTEXT = {}

JAVASCRIPT_TYPE_MAPPING = {
    'integer': 'number',
    'int32': 'number',
    'long': 'number',
    'int64': 'number',
    'float': 'number',
    'double': 'number',
    'string': 'string',
    'byte': 'string',
    'binary': 'string',
    'boolean': 'boolean',
    'date': 'string',
    'date-time': 'Date',
    'password': 'string',
    'object': 'any',  # TODO
    'array': 'Array',
    '<': '<',
    '>': '>',
}

PYTHON_TYPE_MAPPING = {
    'integer': 'int',
    'int32': 'int',
    'long': 'int',
    'int64': 'int',
    'float': 'float',
    'double': 'float',
    'string': 'str',
    # 'byte': 'ByteArray',
    'byte': 'str',
    'binary': 'str',
    # 'binary': 'Binary',
    'boolean': 'bool',
    'date': 'date',
    'date-time': 'datetime',
    'password': 'str',
    'object': 'object',  # TODO
    'array': 'List',
    '<': '[',
    '>': ']',
}

TYPE_MAPPINGS = {
    'python': PYTHON_TYPE_MAPPING,
    'flask': PYTHON_TYPE_MAPPING,
    'javascript': JAVASCRIPT_TYPE_MAPPING,
    'typescript': JAVASCRIPT_TYPE_MAPPING,
}

TEMPLATES_DIR = 'templates'

LANGUAGE = 'flask'

PROJECT_NAME = 'build'
PROJECT_OUTPUT = os.getcwd() + os.path.sep + PROJECT_NAME
FLASK_SERVER_NAME = 'flask_server'
FLASK_SERVER_OUTPUT = PROJECT_OUTPUT + os.path.sep + FLASK_SERVER_NAME

# TODO not using these for now. May be better to just have a singular output directory name
FLASK_PROJECT_NAME = 'flask-server-generated'
FLASK_PROJECT_OUTPUT = os.getcwd() + os.path.sep + FLASK_PROJECT_NAME
TYPESCRIPT_PROJECT_NAME = 'services'
TYPESCRIPT_PROJECT_OUTPUT = os.getcwd() + os.path.sep + TYPESCRIPT_PROJECT_NAME


def load_build_file(filename):
    global BUILD
    global BUILD_FILE_PATH
    global SPEC
    global SPEC_FILE_PATH
    global SPEC_DICT
    global SPECIFICATION
    global TEMPLATES_DIR
    global LANGUAGE
    global FLASK_PROJECT_NAME
    global FLASK_PROJECT_OUTPUT
    global FLASK_SERVER_NAME
    global FLASK_SERVER_OUTPUT
    global TYPESCRIPT_PROJECT_NAME
    global TYPESCRIPT_PROJECT_OUTPUT

    print('loading build file:', filename)
    filepath = os.getcwd() + '/' + filename
    spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
    build_script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build_script)

    BUILD = filename
    BUILD_FILE_PATH = filepath

    if hasattr(build_script, 'SPEC'):
        SPEC = build_script.SPEC
        SPEC_FILE_PATH = os.getcwd() + os.path.sep + SPEC

    if hasattr(build_script, 'LANGUAGE'):
        LANGUAGE = build_script.LANGUAGE

    if hasattr(build_script, 'TEMPLATES_DIR'):
        TEMPLATES_DIR = build_script.TEMPLATES_DIR
