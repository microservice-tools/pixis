import argparse
import sys
import os
from pathlib import Path

from openapi_spec_validator import openapi_v3_spec_validator

import pixis.utils as utils
from pixis.config import Config
from pixis.template_context import init_template_context


"""
    1. Loads default configs
    2. Configure according to build file
"""


def main():

    parser = argparse.ArgumentParser(description= 'A rest api code generator')
    parser.add_argument('-b', help= "Use your own build file", dest='build_file')
    parser.add_argument('-o', help= "Output", dest='output') 

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-q', '--quiet', help= "Suppress Output",  action='store_true', dest='quiet')
    group.add_argument('-v', '--verbose', help="Increase output verbosity",  action='store_true', dest='verbose')
    args = parser.parse_args()

    if args.build_file:
        cwd = Path.cwd()
        Config.load_build_file(args.build_file, cwd)

    if args.output:
        Config.out = args.output
        Config.PATH_OUT = Path(Config.OUT)
        Config.FLASK_SERVER_OUTPUT = Config.PATH_OUT / Config.FLASK_SERVER_NAME

    Config.load_spec_file()

    if Config.APPLICATION == 'typescript':
        from pixis.languages.client_typescript import stage_default_iterators
    else:
        from pixis.languages.server_flask import stage_default_iterators

    stage_default_iterators()

    validate_specification(Config.SPEC_DICT)

    init_template_context()

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
