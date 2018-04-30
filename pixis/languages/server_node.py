import importlib.util
import os

import pixis.configurations as cfg
import pixis.utils as utils


"""
wrappers for emitting templates
"""


def node_project_setup():
    print('node_project_setup')
    utils.emit_template('node_server/index.j2', cfg.PROJECT_OUTPUT, 'index.js')
    utils.emit_template('node_server/package.j2', cfg.PROJECT_OUTPUT, 'package.json')
    utils.emit_template('node_server/writer.j2', cfg.NODE_SERVER_OUTPUT + os.path.sep + 'utils', 'writer.js')


def node_generate_controller():
    # controller files
    print('node_controllers_setup')
    utils.emit_template('node_server/controller.j2', cfg.NODE_SERVER_OUTPUT + os.path.sep + 'controllers', cfg.TEMPLATE_CONTEXT['_current_tag'] + '.py')


def node_generate_service():
    utils.emit_template('node_server/service.j2', cfg.NODE_SERVER_OUTPUT + os.path.sep + 'service', cfg.TEMPLATE_CONTEXT['_current_tag'] + 'Service' + '.py')


node_invocation_iterator_functions = [
    node_project_setup,
]

node_specification_iterator_functions = [
    node_generate_main,
    node_generate_base_model,
]

node_paths_iterator_functions = [
    node_generate_controller,
    node_generate_service
]

node_schemas_iterator_functions = [
]


def stage_default_iterators():
    utils.stage_iterator(utils.invocation_iterator, node_invocation_iterator_functions)
    utils.stage_iterator(utils.specification_iterator, node_specification_iterator_functions)
    utils.stage_iterator(utils.schemas_iterator, node_schemas_iterator_functions)
    utils.stage_iterator(utils.paths_iterator, node_paths_iterator_functions)
