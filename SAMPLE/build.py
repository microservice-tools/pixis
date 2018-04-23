"""
Minimal structure and strictness
user will have to import our default_codegen module to use codegen_stage()
"""
import codegen.utils as utils  # import will look like this because codegen will be a package

SPEC = 'swagger.yaml'
LANGUAGE = 'flask'
# PROJECT_NAME = 'myproject' not sure how to implement this yet
TEMPLATES_DIR = 'mytemplates'


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

    utils.codegen_stage(my_iterator, my_iterator_functions)
    # utils.codegen_stage(utils.paths_iterator, [my_controllers_function])


main()
