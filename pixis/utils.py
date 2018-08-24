import importlib.util
import inspect
import json
import pathlib
import sys

import yaml
import openapi_spec_validator

import pixis.config as cfg
import pixis.implementations.client_angular2 as pixis_client_angular2
import pixis.implementations.server_flask as pixis_server_flask

SUPPORTED = {
    'flask': pixis_server_flask.Flask,
    'angular2': pixis_client_angular2.Angular2,
}


def validate_specification(spec_dict):
    """Validates the specification using **openapi_spec_validator** library. Execution stops if spec is invalid.

    Args:
        spec_dict (dict): OpenAPI 3.0 specification as a dictionary
    """
    errors_iterator = openapi_spec_validator.openapi_v3_spec_validator.iter_errors(spec_dict)
    errors = list(errors_iterator)
    if len(errors) > 0:
        print(len(errors), 'errors')
        sys.exit()

    print('specification [', cfg.Config.SPEC, ']is valid')


def load_spec_file():
    """Saves specification yaml/json as a dict in Config, then validates using *validate_specification()*
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


def load_build_file(build_file):
    """Executes the specified build file, and saves any variables to Config.

    If user-specified build file cannot be found, FileNotFoundError is raised
    If user did not specify a build file, Pixis will look for *build.py* in current directory. If no file exists,
    Pixis will use default settings. (Flask server implementation, output to build/flask_server, look for
        Default settings:
            - implementation: Flask server
            - output: build/flask_server
            - templates: templates/
            - spec: swagger.yaml

    Any variable X defined by the user's build file will be integrated into Config class (Config.X)

    Args:
        build_file (str): relative path of build file

    Raises:
        AttributeError: Occurs when build_spec is None due to build_file not ending in '.py'
        FileNotFoundError: Occurs when specified build file doesn't exist
    """

    filepath = pathlib.Path(build_file)
    build_spec = importlib.util.spec_from_file_location(build_file, filepath.name)

    try:
        build_module = importlib.util.module_from_spec(build_spec)
        build_spec.loader.exec_module(build_module)
        members = inspect.getmembers(build_module, lambda a: not (inspect.isroutine(a)))
        attributes = [attr for attr in members if not (attr[0].startswith('__') and attr[0].endswith('__'))]
        for attr in attributes:
            setattr(cfg.Config, attr[0], attr[1])
    except AttributeError as err:
        err.args += ("CLARIFICATION: build file at '" + build_file + "' is not a Python file",)
        raise
    except FileNotFoundError:
        print("build file at '" + build_file + "' was not found")
        if build_file == 'build.py':
            print("Using Pixis default settings")
        else:
            raise

    if cfg.Config.IMPLEMENTATION in _supported:
        cfg.Config.IMPLEMENTATION = _supported[cfg.Config.IMPLEMENTATION]
    elif not inspect.isclass(cfg.Config.IMPLEMENTATION):
        raise TypeError('Expected IMPLEMENTATION to be a class or string of supported implementation, such as "flask"')


def set_config(key, value):
    """Sets Config class variable @key to @value

    Args:
        key (str): Config class variable to set
        value (str OR None): Value to set Config class variable to
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
    """If .pixis.json exists and is valid, copies the checksums into cfg.Config._checksums
    """
    try:
        cfg.Config._checksums = json.loads(pathlib.Path('.pixis.json').read_text())
        print('Found .pixis.json!')
    except FileNotFoundError:
        print('No .pixis.json found')


def save_checksums():
    """Saves the newly generated files' checksums into .pixis.json
    """
    pathlib.Path('.pixis.json').write_text(json.dumps(cfg.Config._checksums, sort_keys=True, indent=4))
    print('Saved hashes for generated files in .pixis.json')
