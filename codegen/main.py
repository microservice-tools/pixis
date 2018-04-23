import sys
import os
import importlib.util
import yaml
import json
import argparse

from openapi_spec_validator import openapi_v3_spec_validator

import codegen.configurations as cfg
import codegen.utils as utils
from codegen.template_context import init_template_context


def main():
    if len(sys.argv) > 1:
        cfg.load_build_file(sys.argv[1])

    if cfg.LANGUAGE == 'typescript':
        from codegen.languages.client_typescript import stage_default_iterators
    else:
        from codegen.languages.server_flask import stage_default_iterators

    stage_default_iterators()

    if len(sys.argv) > 1:
        cfg.load_build_file(sys.argv[1])

    print(sys.argv)
    print(cfg.SPEC)
    print(cfg.SPEC_FILE_PATH)

    cfg.SPEC_DICT = load_spec_file(cfg.SPEC_FILE_PATH)
    validate_specification(cfg.SPEC_DICT)

    init_template_context()

    utils.run_iterators()


def load_spec_file(file_path):
    extension = os.path.splitext(file_path)[1][1:]
    if extension == 'yaml' or 'yml':
        with open(file_path) as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(e)
                sys.exit()
    if extension == 'json':
        with open(file_path) as f:
            try:
                return json.load(f)
            except ValueError as e:
                print(e)
                sys.exit()


def validate_specification(spec):
    errors_iterator = openapi_v3_spec_validator.iter_errors(spec)
    l = list(errors_iterator)
    if (len(l) > 0):
        print(len(l), 'errors')
        sys.exit()

    print('specification is valid')


if __name__ == '__main__':
    main()
