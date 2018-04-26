"""
Minimal structure and strictness
user will have to import our default_codegen module to use stage_iterator()
Generated files will be output to the current working directory
"""
import pixis.utils as utils  # import will look like this because codegen will be a package

SPEC = 'swagger.yaml'
LANGUAGE = 'typescript'  # 'typescript is also supported
PROJECT_NAME = 'myproject'  # directory name
# TEMPLATES_DIR = 'templates' not implemented yet


def my_iterator(spec, my_iterator_functions):
    print('starting my iterator')
    dikt = {}
    for f in my_iterator_functions:
        f(dikt)


def function1(dikt):
    print('function1')


def function2(dikt):
    print('function2')


def main():
    my_iterator_functions = [
        function1,
        function2,
    ]

    default.stage_iterator(my_iterator, my_iterator_functions)
    # default.stage_iterator(default_codegen.invocation_iterator, []) TO MODIFY OUR DEFAULT ITERATORS


main()
