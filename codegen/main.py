import sys
import os
import importlib.util
import yaml
import ast
import json
import argparse

from openapi_spec_validator import openapi_v3_spec_validator

try:  # when just doing $ python3 main.py only below imports work
    from codegen.classes.specification import Specification
    from codegen.flask_server_codegen import flask_server_codegen, stage_default_iterators
    import codegen.codegen_config as cfg
except ImportError as err:  # when packaged, only above imports work
    from classes.specification import Specification
    from flask_server_codegen import flask_server_codegen, stage_default_iterators
    import codegen_config as cfg

# figure out how argparse works later. Not a high priority though??
# parser = argparse.ArgumentParser()
# parser.add_argument('buildfile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
# args = parser.parse_args()
# print(args.buildfile)


def main():

    stage_default_iterators()
    print(sys.argv)
    if len(sys.argv) > 1:
        load_build_file()

    spec_dict = load_spec_file(cfg.SPEC_FILE_PATH)
    validate_specification(spec_dict)

    spec = Specification(spec_dict)
    spec_dict2 = ast.literal_eval(str(vars(spec)))

    # # with open('spec_tree.json', 'wt') as out:
    # #     json.dump(spec_tree_dict, out, indent=4)

    # MAKE A FILE CALLED flask_client_codegen.py, do it similarly to flask_server_codegen.py
    # generate_typescript_client_code(spec, spec_dict2)

    flask_server_codegen(spec_dict)


def load_build_file():
    # update defaults to reflect user's build file
    filename = sys.argv[1]
    print('loading build file:', filename)
    filepath = os.getcwd() + '/' + filename
    spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
    build_script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build_script)
    cfg.BUILD = filename
    cfg.BUILD_FILE_PATH = filepath
    if hasattr(build_script, 'SPEC'):
        cfg.SPEC = build_script.SPEC
        cfg.SPEC_FILE_PATH = os.getcwd() + os.path.sep + cfg.SPEC
    if hasattr(build_script, 'PROJECT_OUTPUT'):
        cfg.PROJECT_OUTPUT = os.getcwd() + os.path.sep + build_script.PROJECT_OUTPUT


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


# def load_build_file(filename):
#     cwd = os.getcwd()
#     full_path = cwd + '/' + filename
#     spec = importlib.util.spec_from_file_location(
#         filename[:-3], full_path)
#     build_script = importlib.util.module_from_spec(spec)
#     spec.loader.exec_module(build_script)
