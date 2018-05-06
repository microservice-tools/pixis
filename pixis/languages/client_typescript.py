import os

import pixis.utils as utils
from pixis.config import Config
from pixis.template_context import TEMPLATE_CONTEXT


"""
wrappers for emitting templates
"""


def typescript_project_setup():
    print('typescript_project_setup')


def typescript_specification_setup():
    print('typescript_specfication_setup')
    utils.emit_template('typescript_client/index.j2', Config.PATH_OUT, 'index.ts')
    utils.emit_template('typescript_client/variables.j2', Config.PATH_OUT, 'variables.ts')
    utils.emit_template('typescript_client/configuration.j2', Config.PATH_OUT, 'configuration.ts')
    utils.emit_template('typescript_client/api_ts.j2', Config.PATH_OUT / 'api', 'api.ts')
    utils.emit_template('typescript_client/models.j2', Config.PATH_OUT / 'model', 'models.ts')
    utils.emit_template('typescript_client/encoder.j2', Config.PATH_OUT, 'encoder.ts')
    utils.emit_template('typescript_client/api_module.j2', Config.PATH_OUT, 'api.module.ts')
    utils.emit_template('typescript_client/rxjs.j2', Config.PATH_OUT, 'rxjs-operators.ts')


def typescript_generate_service():
    # CHECK notes/servicetemplatesnodes.ts for TODO
    # almost done
    utils.emit_template('typescript_client/service.j2', Config.PATH_OUT / 'api', TEMPLATE_CONTEXT['_current_tag'] + '.service.ts')


def typescript_models_setup():
    # model files
    print('typescript_models_setup')
    utils.emit_template('typescript_client/model.j2', Config.PATH_OUT / 'model', TEMPLATE_CONTEXT['_current_schema'] + '.ts')


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
