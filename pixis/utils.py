import collections
import importlib.util
import inspect
import json
import sys
from pathlib import Path

import yaml
from openapi_spec_validator import openapi_v3_spec_validator

import pixis.config as cfg
import pixis.implementations.client_angular2 as pixis_angular2
import pixis.implementations.server_flask as pixis_flask
import pixis.template_handler as tmpl


def validate_specification(spec):
    errors_iterator = openapi_v3_spec_validator.iter_errors(spec)
    errors = list(errors_iterator)
    if (len(errors) > 0):
        print(len(errors), 'errors')
        sys.exit()

    print('specification is valid')


def load_spec_file():
    print(cfg.Config.SPEC)
    with Path(cfg.Config.SPEC).open() as f:
        try:
            cfg.Config.SPEC_DICT = yaml.safe_load(f)
        except yaml.YAMLError as yaml_error:
            try:
                cfg.Config.SPEC_DICT = json.load(f)
            except ValueError as json_error:
                extension = Path(Config.SPEC).suffix
                if extension == 'json':
                    print(json_error)
                    sys.exit()
                else:
                    print(yaml_error)
                    sys.exit()

    validate_specification(cfg.Config.SPEC_DICT)


SUPPORTED = {
    'flask': pixis_flask.Flask,
    'angular2': pixis_angular2.Angular2,
}


def to_class(string):
    return SUPPORTED[string.lower()]


def set_output(out):
    cfg.Config.OUT = out


def set_language():
    if type(cfg.Config.IMPLEMENTATION) == str:
        cfg.Config.IMPLEMENTATION = to_class(cfg.Config.IMPLEMENTATION)
    cfg.Config.LANGUAGE = cfg.Config.IMPLEMENTATION.LANGUAGE


def load_build_file(build_file):  # build_file should be a relative filepath
    filepath = Path(build_file)
    spec = importlib.util.spec_from_file_location(build_file, filepath.name)

    if not spec:
        print("The build file \"" + str(file_path) + "\" was expected to be a python file, ending with a .py extension")
        sys.exit()

    build_script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build_script)

    impl = getattr(build_script, 'IMPLEMENTATION', 'flask')
    if impl in SUPPORTED:
        cfg.Config.IMPLEMENTATION = to_class(impl)
    elif inspect.isclass(impl):
        cfg.Config.IMPLEMENTATION = impl
    else:
        raise TypeError('expected: class or string of supported implementations (such as "flask")')

    cfg.Config.BUILD = build_file
    cfg.Config.SPEC = getattr(build_script, 'SPEC', 'swagger.yaml')
    cfg.Config.TEMPLATES = getattr(build_script, 'TEMPLATES', 'templates')
    cfg.Config.OUT = getattr(build_script, 'OUT', 'build')
    cfg.Config.FLASK_SERVER_NAME = getattr(build_script, 'FLASK_SERVER_NAME', 'flask_server')


iterators_mapping = collections.OrderedDict()
iterator_functions_mapping = collections.OrderedDict()


def stage_iterator(x_iterator, x_iterator_functions):
    iterator_name = x_iterator.__name__
    iterators_mapping[iterator_name] = x_iterator
    iterator_functions_mapping[iterator_name] = [static.__func__ for static in x_iterator_functions]


def run_iterators():
    for iterator_name, iterator in iterators_mapping.items():
        iterator(iterator_functions_mapping[iterator_name])


def set_iterators():
    cfg.Config.IMPLEMENTATION.stage_default_iterators()
    if cfg.Config.BUILD is not None:
        load_build_file(cfg.Config.BUILD)


def once_iterator(once_iterator_functions):
    for f in once_iterator_functions:
        f()


def schema_iterator(schema_iterator_functions):
    for schema_name, schema in tmpl.TEMPLATE_CONTEXT['schemas'].items():
        tmpl.TEMPLATE_CONTEXT['_current_schema'] = schema_name
        for f in schema_iterator_functions:
            f()


def tag_iterator(tag_iterator_functions):
    for tag, paths in tmpl.TEMPLATE_CONTEXT['paths'].items():
        tmpl.TEMPLATE_CONTEXT['_current_tag'] = tag
        for f in tag_iterator_functions:
            f()
