import importlib.util
import inspect
import json
import pathlib
import sys

import yaml
from openapi_spec_validator import openapi_v3_spec_validator

import pixis.config as cfg
import pixis.implementations.client_angular2 as pixis_angular2
import pixis.implementations.server_flask as pixis_flask

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
    with pathlib.Path(cfg.Config.SPEC).open() as f:
        try:
            cfg.Config.SPEC_DICT = yaml.safe_load(f)
        except yaml.YAMLError as yaml_error:
            try:
                cfg.Config.SPEC_DICT = json.load(f)
            except json.JSONDecodeError as json_error:
                extension = pathlib.Path(cfg.Config.SPEC).suffix
                if extension == 'json':
                    print(json_error)
                    sys.exit()
                else:
                    print(yaml_error)
                    sys.exit()

    validate_specification(cfg.Config.SPEC_DICT)


def load_build_file(build_file):  # build_file should be a relative filepath
    """Executes and pulls info from the user's build file

    Any variable X defined by the user's build file will be integrated into Config class (Config.X)

    Args:
        build_file (str): filepath of build file used for generation customization

    Raises:
        TypeError: Occurs if IMPLEMENTATION was an unsupported string, or if Implementation class could not be found
    """

    filepath = pathlib.Path(build_file)
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
    setattr(cfg.Config, 'PARENT', str(pathlib.Path(cfg.Config.OUTPUT).parent))


def set_language():
    """Sets Language class for Pixis to use

    Language class is defined within the Implementation class
    """
    if type(cfg.Config.IMPLEMENTATION) == str:
        cfg.Config.IMPLEMENTATION = _supported[cfg.Config.IMPLEMENTATION.lower()]
    cfg.Config.LANGUAGE = cfg.Config.IMPLEMENTATION.LANGUAGE


def set_iterators():
    """Stages implementation default iterators as well as any user-defined iterators
    """
    cfg.Config.IMPLEMENTATION.stage_default_iterators()
    try:
        load_build_file(cfg.Config.BUILD)
    except FileNotFoundError:
        pass


def run_iterators():
    """Executes each iterator that was staged by *stage_iterator()*
    """
    for iterator_name, iterator in cfg.Config._iterators_mapping.items():
        iterator(cfg.Config._iterator_functions_mapping[iterator_name])


def load_checksums():
    try:
        cfg.Config._checksums = json.loads(pathlib.Path('.pixis.json').read_text())
        print('Found .pixis.json!')
    except FileNotFoundError:
        print('No .pixis.json found')


def save_checksums():
    pathlib.Path('.pixis.json').write_text(json.dumps(cfg.Config._checksums, sort_keys=True, indent=4))
    print('Saved hashes for generated files in .pixis.json')
