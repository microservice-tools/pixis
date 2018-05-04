import sys
import os
import importlib.util
import yaml
import json
import argparse

from openapi_spec_validator import openapi_v3_spec_validator

from pixis.configuration import Configuration
import pixis.utils as utils
from pixis.template_context import init_template_context

"""
    1. Loads default configurations
    2. Configure according to build file
"""


def main():
    cfg = Configuration()
    if len(sys.argv) > 1:
        cfg.load_build_file(sys.argv[1])

    if cfg.LANGUAGE == 'typescript':
        from pixis.languages.client_typescript import stage_default_iterators
    else:
        from pixis.languages.server_flask import stage_default_iterators

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


def validate_specification(spec):
    errors_iterator = openapi_v3_spec_validator.iter_errors(spec)
    l = list(errors_iterator)
    if (len(l) > 0):
        print(len(l), 'errors')
        sys.exit()

    print('specification is valid')


if __name__ == '__main__':
    main()
