import importlib.util
import os

import pixis.configurations as cfg
import pixis.utils as utils


"""
wrappers for emitting templates
"""


def typescript_project_setup():
    print('typescript_project_setup')


def typescript_specification_setup():
    print('typescript_specfication_setup')
    utils.emit_template('typescript_client/index.j2', cfg.PROJECT_OUTPUT, 'index.ts')
    utils.emit_template('typescript_client/variables.j2', cfg.PROJECT_OUTPUT, 'variables.ts')
    utils.emit_template('typescript_client/configuration.j2', cfg.PROJECT_OUTPUT, 'configuration.ts')
    utils.emit_template('typescript_client/api_ts.j2', cfg.PROJECT_OUTPUT + os.path.sep + 'api', 'api.ts')
    utils.emit_template('typescript_client/models.j2', cfg.PROJECT_OUTPUT + os.path.sep + 'model', 'models.ts')
    utils.emit_template('typescript_client/encoder.j2', cfg.PROJECT_OUTPUT, 'encoder.ts')
    utils.emit_template('typescript_client/api_module.j2', cfg.PROJECT_OUTPUT, 'api.module.ts')
    utils.emit_template('typescript_client/rxjs.j2', cfg.PROJECT_OUTPUT, 'rxjs-operators.ts')


def typescript_generate_service():
    # CHECK notes/servicetemplatesnodes.ts for TODO
    # almost done
    utils.emit_template('typescript_client/service.j2', cfg.PROJECT_OUTPUT + os.path.sep + 'api', cfg.TEMPLATE_CONTEXT['_current_tag'] + '.service.ts')


def typescript_models_setup():
    # model files
    print('typescript_models_setup')
    utils.emit_template('typescript_client/model.j2', cfg.PROJECT_OUTPUT + os.path.sep + 'model', cfg.TEMPLATE_CONTEXT['_current_schema'] + '.ts')


typescript_invocation_iterator_functions = [
    typescript_project_setup,
]

typescript_specification_iterator_functions = [
    typescript_specification_setup
]

typescript_paths_iterator_functions = [
    typescript_generate_service,
]

typescript_schemas_iterator_functions = [
    typescript_models_setup,
]


def stage_default_iterators():
    utils.stage_iterator(utils.invocation_iterator, typescript_invocation_iterator_functions)
    utils.stage_iterator(utils.specification_iterator, typescript_specification_iterator_functions)
    utils.stage_iterator(utils.schemas_iterator, typescript_schemas_iterator_functions)
    utils.stage_iterator(utils.paths_iterator, typescript_paths_iterator_functions)
