import importlib.util
import json
import os
import sys

import yaml

from pixis.languages.python import Python
from pixis.implementations.server_flask import Flask


class Config():
    BUILD = None
    SPEC = 'swagger.yaml'
    TEMPLATES = 'templates'
    OUT = 'build'

    PATH_BUILD = None
    PATH_SPEC = os.getcwd() + os.path.sep + SPEC
    PATH_TEMPLATES = os.getcwd() + os.path.sep + TEMPLATES
    PATH_OUT = os.getcwd() + os.path.sep + OUT

    SPEC_DICT = {}

    LANGUAGE = Python
    IMPLEMENTATION = Flask

    # unsure what we're going to do with these
    FLASK_SERVER_NAME = 'flask_server'
    FLASK_SERVER_OUTPUT = PATH_OUT + os.path.sep + FLASK_SERVER_NAME

    @staticmethod
    def load_build_file(build_file):  # build_file should be a relative filepath
        filepath = os.getcwd() + os.path.sep + build_file
        spec = importlib.util.spec_from_file_location(build_file[:-3], filepath)
        build_script = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build_script)

        SUPPORTED = ['flask', 'angular2']
        Config.IMPLEMENTATION = getattr(build_script, 'IMPLEMENTATION', 'flask')
        if Config.IMPLEMENTATION not in SUPPORTED:
            # TODO it's a custom implementation
            pass

        Config.BUILD = build_file
        Config.SPEC = getattr(build_script, 'SPEC', 'swagger.yaml')
        Config.TEMPLATES = getattr(build_script, 'TEMPLATES', 'templates')
        Config.OUT = getattr(build_script, 'OUT', 'build')

        Config.PATH_BUILD = os.getcwd() + os.path.sep + build_file
        Config.PATH_SPEC = os.getcwd() + os.path.sep + Config.SPEC
        Config.PATH_TEMPLATES = os.getcwd() + os.path.sep + Config.TEMPLATES
        Config.PATH_OUT = os.getcwd() + os.path.sep + Config.OUT

        Config.FLASK_SERVER_NAME = 'flask_server'
        Config.FLASK_SERVER_OUTPUT = Config.PATH_OUT + os.path.sep + Config.FLASK_SERVER_NAME

    @staticmethod
    def load_spec_file():
        with open(Config.PATH_SPEC) as f:
            try:
                Config.SPEC_DICT = yaml.safe_load(f)
            except yaml.YAMLError as yaml_error:
                try:
                    Config.SPEC_DICT = json.load(f)
                except ValueError as json_error:
                    extension = os.path.splitext(Config.PATH_SPEC)[1][1:]
                    if extension == 'json':
                        print(json_error)
                        sys.exit()
                    else:
                        print(yaml_error)
                        sys.exit()
