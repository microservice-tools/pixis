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
    parser.add_argument('-b', help="Use your own build file", dest='build_file')
    parser.add_argument('-o', help="Output", dest='output')

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-q', '--quiet', help="Suppress Output", action='store_true', dest='quiet')
    group.add_argument('-v', '--verbose', help="Increase output verbosity", action='store_true', dest='verbose')
    args = parser.parse_args()

    if args.build_file:
        print(args.build_file)
        utils.load_build_file(args.build_file)  # get target implementation/language

    if args.output:
        utils.set_output(args.output)

    utils.set_language()  # set language class to use for template context translation
    utils.load_spec_file()  # load spec dictionary and verify spec
    utils.set_iterators()
    tmpl.create_template_context()
    utils.run_iterators()


if __name__ == '__main__':
    main()
