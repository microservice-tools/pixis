# import argparse
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
    if len(sys.argv) > 1:
        build_file = sys.argv[1]
        cwd = Path.cwd()
        Config.load_build_file(build_file, cwd)
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
