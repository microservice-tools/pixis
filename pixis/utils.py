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

_supported = {
    'flask': pixis_flask.Flask,
    'angular2': pixis_angular2.Angular2,
}


def validate_specification(spec):
    """Validates the specification using **openapi_spec_validator** library

    Args:
        spec (dict): OpenAPI 3.0 specification as a dictionary
    """
    errors_iterator = openapi_v3_spec_validator.iter_errors(spec)
    errors = list(errors_iterator)
    if (len(errors) > 0):
        print(len(errors), 'errors')
        sys.exit()

    print('specification is valid')


def load_spec_file():
    """
    Reads in 'yaml' or 'json' file, validates for syntax errors and validates the definition of the specification file.
    """
    print(cfg.Config.SPEC)
    with Path(cfg.Config.SPEC).open() as f:
        try:
            cfg.Config.SPEC_DICT = yaml.safe_load(f)
        except yaml.YAMLError as yaml_error:
            try:
                cfg.Config.SPEC_DICT = json.load(f)
            except json.JSONDecodeError as json_error:
                extension = Path(cfg.Config.SPEC).suffix
                if extension == 'json':
                    print(json_error)
                    sys.exit()
                else:
                    print(yaml_error)
                    sys.exit()

    validate_specification(cfg.Config.SPEC_DICT)


def set_config(key, value):
    """Sets Config class variable (@key) to @value

    Args:
        key (str): Config class variable to set
        value (str): Value to set Config class variable to
    """
    setattr(cfg.Config, key.upper(), value)


def set_parent():
    """Sets Config.PARENT to the parent directory filepath of Config.OUTPUT

    Can be used by *emit_template()* to generate files outside of the build directory
    """
    setattr(cfg.Config, 'PARENT', str(Path(cfg.Config.OUTPUT).parent))


def set_language():
    """Sets Language class for Pixis to use

    Language class is defined within the Implementation class
    """
    if type(cfg.Config.IMPLEMENTATION) == str:
        cfg.Config.IMPLEMENTATION = _supported[cfg.Config.IMPLEMENTATION.lower()]
    cfg.Config.LANGUAGE = cfg.Config.IMPLEMENTATION.LANGUAGE


def load_build_file(build_file):  # build_file should be a relative filepath
    """Executes and pulls info from the user's build file

    Any variable X defined by the user's build file will be integrated into Config class (Config.X)

    Args:
        build_file (str): filepath of build file used for generation customization

    Raises:
        TypeError: Occurs if IMPLEMENTATION was an unsupported string, or if Implementation class could not be found
    """

    filepath = Path(build_file)
    spec = importlib.util.spec_from_file_location(build_file, filepath.name)

    if not spec:
        print("The build file \"" + str(filepath) + "\" was expected to be a python file, ending with a .py extension")
        sys.exit()

    build_script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build_script)

    members = inspect.getmembers(build_script, lambda a: not(inspect.isroutine(a)))
    attributes = [attribute for attribute in members if not(attribute[0].startswith('__') and attribute[0].endswith('__'))]
    for attribute in attributes:
        setattr(cfg.Config, attribute[0], attribute[1])

    if cfg.Config.IMPLEMENTATION in _supported:
        cfg.Config.IMPLEMENTATION = _supported[cfg.Config.IMPLEMENTATION]
    elif not inspect.isclass(cfg.Config.IMPLEMENTATION):
        raise TypeError('Expected IMPLEMENTATION to be a class or string of supported implementation, such as "flask"')


iterators_mapping = collections.OrderedDict()
iterator_functions_mapping = collections.OrderedDict()


def stage_iterator(x_iterator, x_iterator_functions):
    """Stages iterators and their functions to be executed

    Args:
        x_iterator (function): iterator function to execute. Defaults are: *once_iterator()*, *schema_iterator()*, *tag_iterator()*
        x_iterator_functions (List[function]): list of functions to be executed by specified iterator
    """
    iterator_name = x_iterator.__name__
    iterators_mapping[iterator_name] = x_iterator
    iterator_functions_mapping[iterator_name] = [f for f in x_iterator_functions]


def run_iterators():
    """Executes each iterator that was staged by *stage_iterator()*
    """
    for iterator_name, iterator in iterators_mapping.items():
        iterator(iterator_functions_mapping[iterator_name])


def set_iterators():
    """Stages implementation default iterators as well as any user-defined iterators
    """
    cfg.Config.IMPLEMENTATION.stage_default_iterators()
    try:
        load_build_file(cfg.Config.BUILD)
    except FileNotFoundError:
        return


def once_iterator(once_iterator_functions):
    """Executes each function in @once_iterator_functions once

    Args:
        once_iterator_functions (List[function]): functions that this iterator will execute
    """
    for f in once_iterator_functions:
        f()


def schema_iterator(schema_iterator_functions):
    """Executes each function in @schema_iterator_functions once per schema

    Args:
        schema_iterator_functions (List[function]): functions that this iterator will execute
    """
    for schema_name, schema in tmpl.TEMPLATE_CONTEXT['schemas'].items():
        tmpl.TEMPLATE_CONTEXT['_current_schema'] = schema_name
        for f in schema_iterator_functions:
            f()


def tag_iterator(tag_iterator_functions):
    """Executes each function in @tag_iterator_functions once per tag

    Args:
        tag_iterator_functions (List[function]): functions that this iterator will execute
    """
    for tag, paths in tmpl.TEMPLATE_CONTEXT['paths'].items():
        tmpl.TEMPLATE_CONTEXT['_current_tag'] = tag
        for f in tag_iterator_functions:
            f()
