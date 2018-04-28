import importlib.util
import os

import pixis.configurations as cfg
import pixis.utils as utils


"""
wrappers for emitting templates
"""


def flask_project_setup():
    # outer codegen folder: setup.py, requirements.txt. Dockerfile
    print('flask_project_setup')
    utils.emit_template('flask_server/requirements.j2', cfg.PROJECT_OUTPUT, 'requirements.txt')
    utils.emit_template('flask_server/Dockerfile.j2', cfg.PROJECT_OUTPUT, 'Dockerfile')
    # utils.emit_template('flask_server/setup.j2', cfg.PROJECT_OUTPUT, 'setup.py')


def flask_generate_base_model():
    print('flask_base_model_setup')
    utils.emit_template('flask_server/base_model.j2', cfg.FLASK_SERVER_OUTPUT + os.path.sep + 'models', 'base_model.py')
    utils.emit_template('flask_server/util.j2', cfg.FLASK_SERVER_OUTPUT, 'util.py')
    utils.emit_template('flask_server/encoder.j2', cfg.FLASK_SERVER_OUTPUT, 'encoder.py')


def flask_generate_main():
    print('flask_generate_main')
    utils.emit_template('flask_server/init.j2', cfg.FLASK_SERVER_OUTPUT, '__init__.py')
    utils.emit_template('flask_server/main.j2', cfg.FLASK_SERVER_OUTPUT, '__main__.py')


def flask_generate_controller():
    # controller files
    print('flask_controllers_setup')
    utils.emit_template('flask_server/controller.j2', cfg.FLASK_SERVER_OUTPUT + os.path.sep + 'controllers', cfg.TEMPLATE_CONTEXT['_current_tag'] + '_controller' + '.py')


def makeFirstLetterLower(s):
    return s[:1].lower() + s[1:] if s else ''


def flask_generate_model():
    utils.emit_template('flask_server/model.j2', cfg.FLASK_SERVER_OUTPUT + os.path.sep + 'models', makeFirstLetterLower(cfg.TEMPLATE_CONTEXT['_current_schema']) + '.py')


flask_invocation_iterator_functions = [
    flask_project_setup,
]

flask_specification_iterator_functions = [
    flask_generate_main,
    flask_generate_base_model,
]

flask_paths_iterator_functions = [
    flask_generate_controller,
]

flask_schemas_iterator_functions = [
    flask_generate_model,
]


def stage_default_iterators():
    utils.stage_iterator(utils.invocation_iterator, flask_invocation_iterator_functions)
    utils.stage_iterator(utils.specification_iterator, flask_specification_iterator_functions)
    utils.stage_iterator(utils.schemas_iterator, flask_schemas_iterator_functions)
    utils.stage_iterator(utils.paths_iterator, flask_paths_iterator_functions)
