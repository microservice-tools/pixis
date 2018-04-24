import importlib.util
import os
import re
import sys

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

FLASK_PROJECT_NAME = 'flask-server-generated'
FLASK_PROJECT_OUTPUT = os.getcwd() + os.path.sep + FLASK_PROJECT_NAME
FLASK_SERVER_NAME = 'flask_server'
FLASK_SERVER_OUTPUT = FLASK_PROJECT_OUTPUT + os.path.sep + FLASK_SERVER_NAME

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
