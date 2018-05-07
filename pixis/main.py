# import argparse
import sys

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
    if len(sys.argv) > 1:
        utils.load_build_file(sys.argv[1])  # get target implementation/language
    utils.set_language()  # set language class to use for template context translation
    utils.load_spec_file()  # load spec dictionary and verify spec
    utils.set_iterators()
    tmpl.create_template_context()
    utils.run_iterators()


if __name__ == '__main__':
    main()
