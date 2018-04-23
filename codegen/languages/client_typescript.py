import os
import importlib.util

import codegen.utils as utils
import codegen.configurations as cfg

"""
wrappers for emitting templates
"""
# maps the type in OpenApi3 to the type in python
# types: [array, boolean, integer, null,  number, object, string]
# formats that matter for strings: ByteArray, Binary, date, datetime

typeMapping = {
    'integer': 'number',
    'long': 'number',
    'float': 'number',
    'double': 'number',
    'string': 'string',
    'byte': 'string',
    'binary': 'string',
    'boolean': 'boolean',
    'date': 'string',
    'date-time': 'Date',
    'password': 'string',
    'object': 'any'
}


def typescript_project_setup():
    print('typescript_project_setup')
    # utils.emit_template('requirements.j2', dikt, cfg.TYPESCRIPT_PROJECT_OUTPUT, 'requirements.txt')


def typescript_specification_setup():
    print('typescript_specfication_setup')
    utils.emit_template('typescript_client/index.j2', cfg.TYPESCRIPT_PROJECT_OUTPUT, 'index.ts')
    utils.emit_template('typescript_client/variables.j2', cfg.TYPESCRIPT_PROJECT_OUTPUT, 'variables.ts')
    utils.emit_template('typescript_client/configuration.j2', cfg.TYPESCRIPT_PROJECT_OUTPUT, 'configuration.ts')
    utils.emit_template('typescript_client/api_ts.j2', cfg.TYPESCRIPT_PROJECT_OUTPUT + os.path.sep + 'api', 'api.ts')
    utils.emit_template('typescript_client/models.j2', cfg.TYPESCRIPT_PROJECT_OUTPUT + os.path.sep + 'model', 'models.ts')
    utils.emit_template('typescript_client/encoder.j2', cfg.TYPESCRIPT_PROJECT_OUTPUT, 'encoder.ts')
    utils.emit_template('typescript_client/api_module.j2', cfg.TYPESCRIPT_PROJECT_OUTPUT, 'api.module.ts')
    utils.emit_template('typescript_client/rxjs.j2', cfg.TYPESCRIPT_PROJECT_OUTPUT, 'rxjs-operators.ts')


def typescript_generate_service():
    # CHECK notes/servicetemplatesnodes.ts for TODO
    # almost done
    utils.emit_template('typescript_client/service.j2', cfg.TYPESCRIPT_PROJECT_OUTPUT + os.path.sep + 'api', cfg.TEMPLATE_CONTEXT['_current_tag'] + '.service.ts')


def typescript_models_setup():
    # model files
    print('typescript_models_setup')
    utils.emit_template('typescript_client/model.j2', cfg.TYPESCRIPT_PROJECT_OUTPUT + os.path.sep + 'model', makeFirstLetterLower(cfg.TEMPLATE_CONTEXT['_current_schema']) + '.ts')


def makeFirstLetterLower(s):
    return s[:1].lower() + s[1:] if s else ''


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
    utils.codegen_stage(utils.invocation_iterator, typescript_invocation_iterator_functions)
    utils.codegen_stage(utils.specification_iterator, typescript_specification_iterator_functions)
    utils.codegen_stage(utils.schemas_iterator, typescript_schemas_iterator_functions)
    utils.codegen_stage(utils.paths_iterator, typescript_paths_iterator_functions)
