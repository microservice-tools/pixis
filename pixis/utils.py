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
    """
    Takes in the specification file specified by 'spec' and uses the 'openapi_v3_spec_validator' library to validate for definition errors.
    
    Args:
        spec (dict): dictionary that stores all the definitions where keys and values are defined by OpenAPI v3.0 specification guide
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
            except ValueError as json_error:
                extension = Path(cfg.Config.SPEC).suffix
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


def set_config(key, value):
    """
    Set default configuration values for config.py

    Args:
        key (str): object variable to set 'value' to
        value (str): value to set config variable to
    """
    setattr(cfg.Config, key.upper(), value)


def set_parent():
    """
    Set default configuration value for PARENT for config.py
    """
    setattr(cfg.Config, 'PARENT', str(Path(cfg.Config.OUT).parent))


def set_language():
    """
    Maps and sets the default configuration value for 'LANGUAGE' from given 'IMPLEMENTATION'
    """
    if type(cfg.Config.IMPLEMENTATION) == str:
        cfg.Config.IMPLEMENTATION = SUPPORTED[cfg.Config.IMPLEMENTATION.lower()]
    cfg.Config.LANGUAGE = cfg.Config.IMPLEMENTATION.LANGUAGE


def load_build_file(build_file):  # build_file should be a relative filepath
    """
    Load and builds module from file name specified by 'build_file' to be executed

    Args:
        build_file (str): name of build file used for generation customization
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

    impl = getattr(build_script, 'IMPLEMENTATION')
    if impl not in SUPPORTED and not inspect.isclass(impl):
        raise TypeError('Expected IMPLEMENTATION to be a class or string of supported implementation, such as "flask"')


iterators_mapping = collections.OrderedDict()
iterator_functions_mapping = collections.OrderedDict()


def stage_iterator(x_iterator, x_iterator_functions):
    """
    Defines all the iterator mappings associated with code generation.

    Args: 
        x_iterator (function): iterator function to be defined
            Valid functions are 'once_iterator', 'schema_iterator', and 'tag_iterator'
        x_iterator_functions (List[function]): list of functions to be generated using specified iterator
    """
    iterator_name = x_iterator.__name__
    iterators_mapping[iterator_name] = x_iterator
    iterator_functions_mapping[iterator_name] = [f for f in x_iterator_functions]


def run_iterators():
    """
    Executes list of functions of each iterator
    """
    for iterator_name, iterator in iterators_mapping.items():
        iterator(iterator_functions_mapping[iterator_name])


def set_iterators():
    """
    Sets the appropriate iterators with function iterators. Uses the build file defined iterators and iterator functions
    """
    cfg.Config.IMPLEMENTATION.stage_default_iterators()
    if cfg.Config.BUILD is not None:
        load_build_file(cfg.Config.BUILD)


def once_iterator(once_iterator_functions):
    """
    Runs functions mapped to once_iterator

    Args:
        once_iterator_functions (List[function]): iterator functions that generate once per project. 
    """
    for f in once_iterator_functions:
        f()


def schema_iterator(schema_iterator_functions):
    """
    Runs functions mapped to schema_iterator

    Args:
        schema_iterator_functions (List[function]): iterator functions that generate for each defined schema
    """
    for schema_name, schema in tmpl.TEMPLATE_CONTEXT['schemas'].items():
        tmpl.TEMPLATE_CONTEXT['_current_schema'] = schema_name
        for f in schema_iterator_functions:
            f()


def tag_iterator(tag_iterator_functions):
    """
    Runs functions mapped to tag_iterator

    Args:
        tag_iterator_functions (List[function]): iterator functions that generate for each defined path
    """
    for tag, paths in tmpl.TEMPLATE_CONTEXT['paths'].items():
        tmpl.TEMPLATE_CONTEXT['_current_tag'] = tag
        for f in tag_iterator_functions:
            f()
    pass
