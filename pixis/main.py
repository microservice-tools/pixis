# import argparse
import sys

from openapi_spec_validator import openapi_v3_spec_validator

import pixis.utils as utils
from pixis.config import Config
from pixis.template_context import create_template_context


"""
    1. Loads default configs
    2. Configure according to build file
"""


def main():
    if len(sys.argv) > 1:
        Config.load_build_file(sys.argv[1])  # need to get target implementation/language so we know which iterators to use
    Config.load_spec_file()
    validate_specification(Config.SPEC_DICT)

    Config.IMPLEMENTATION.stage_default_iterators()
    if len(sys.argv) > 1:
        Config.load_build_file(sys.argv[1])  # need to do this again to stage any custom iterators

    create_template_context()

    utils.run_iterators()


def validate_specification(spec):
    errors_iterator = openapi_v3_spec_validator.iter_errors(spec)
    errors = list(errors_iterator)
    if (len(errors) > 0):
        print(len(errors), 'errors')
        sys.exit()

    print('specification is valid')


if __name__ == '__main__':
    main()
