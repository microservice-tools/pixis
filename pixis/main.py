"""
- driver for the program
"""

import argparse

import pixis.template_handler as tmpl
import pixis.utils as utils


"""
    - get implementation/language
    - get spec_dict
    - validate spec
    - default iterators
    - custom iterators
    - template context
    - run iterators
"""


def main():
    parser = argparse.ArgumentParser(description='A rest api code generator')
    parser.add_argument('-b', '--build', default='build.py', help="Set build file location, default: %(default)s", dest='build_file')
    parser.add_argument('-o', '--output', default='build', help="Set output directory location, default: %(default)s", dest='output')
    parser.add_argument('-t', '--templates', default='templates', help="Set local template directory, default: %(default)s", dest='templates')

    # group = parser.add_mutually_exclusive_group(required=False)
    # group.add_argument('-q', '--quiet', help="Suppress Output", action='store_true', dest='quiet')
    # group.add_argument('-v', '--verbose', help="Increase output verbosity", action='store_true', dest='verbose')
    args = parser.parse_args()

    utils.set_config('templates', args.templates)
    utils.set_config('out', args.output)

    try:
        utils.load_build_file(args.build_file)
    except FileNotFoundError:
        print('no build file found: using Pixis defaults')

    utils.set_parent()
    utils.set_language()  # set language class to use for template context translation
    utils.load_spec_file()  # load spec dictionary and verify spec
    utils.set_iterators()
    tmpl.create_template_context()
    utils.run_iterators()


if __name__ == '__main__':
    main()
