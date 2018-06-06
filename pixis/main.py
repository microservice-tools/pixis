import argparse

import pixis.template_handler as tmpl
import pixis.utils as utils


def main():
    parser = argparse.ArgumentParser(description='A rest api code generator')
    parser.add_argument('-b', '--build', default='build.py', help="Set build file location, default: %(default)s", dest='build_file')
    parser.add_argument('-o', '--output', default='build', help="Set output directory location, default: %(default)s", dest='output')
    parser.add_argument('-t', '--templates', default='templates', help="Set local template directory, default: %(default)s", dest='templates')
    parser.add_argument('-v', '--verbose', default=False, help="Set verbose mode, default: %(default)s", dest='verbose')
    parser.add_argument('-w', '--overwrite', default=False, help="Set force overwrite mode, default: %(default)s", dest='overwrite')

    # add back later if we're going to be implementing quiet
    # group = parser.add_mutually_exclusive_group(required=False)
    # group.add_argument('-q', '--quiet', help="Suppress Output", action='store_true', dest='quiet')
    # group.add_argument('-v', '--verbose', help="Increase output verbosity", action='store_true', dest='verbose')
    args = parser.parse_args()

    utils.set_config('BUILD', args.build_file)
    utils.set_config('TEMPLATES', args.templates)
    utils.set_config('OUTPUT', args.output)
    utils.set_config('VERBOSE', args.verbose)
    utils.set_config('OVERWRITE', args.overwrite)

    try:
        utils.load_build_file(args.build_file)
    except FileNotFoundError:
        print('no build file found: using Pixis defaults')

    utils.set_parent()
    utils.set_language()
    utils.load_spec_file()
    utils.load_checksums()
    utils.set_iterators()
    tmpl.create_template_context()
    utils.run_iterators()
    utils.save_checksums()


if __name__ == '__main__':
    main()
