import os

import pixis.utils as utils
from pixis.config import Config
from pixis.implementations.implementation import Implementation
from pixis.languages.python import Javascript
from pixis.template_context import TEMPLATE_CONTEXT


class Angular2(Implementation):
    LANGUAGE = Javascript

    @staticmethod
    def generate_once():
        utils.emit_template('typescript_client/index.j2', Config.PATH_OUT, 'index.ts')
        utils.emit_template('typescript_client/variables.j2', Config.PATH_OUT, 'variables.ts')
        utils.emit_template('typescript_client/configuration.j2', Config.PATH_OUT, 'configuration.ts')
        utils.emit_template('typescript_client/api_ts.j2', Config.PATH_OUT + os.path.sep + 'api', 'api.ts')
        utils.emit_template('typescript_client/models.j2', Config.PATH_OUT + os.path.sep + 'model', 'models.ts')
        utils.emit_template('typescript_client/encoder.j2', Config.PATH_OUT, 'encoder.ts')
        utils.emit_template('typescript_client/api_module.j2', Config.PATH_OUT, 'api.module.ts')
        utils.emit_template('typescript_client/rxjs.j2', Config.PATH_OUT, 'rxjs-operators.ts')

    @staticmethod
    def generate_per_tag():
        utils.emit_template('typescript_client/service.j2', Config.PATH_OUT + os.path.sep + 'api', TEMPLATE_CONTEXT['_current_tag'] + '.service.ts')

    @staticmethod
    def generate_per_schema():
        utils.emit_template('typescript_client/model.j2', Config.PATH_OUT + os.path.sep + 'model', TEMPLATE_CONTEXT['_current_schema'] + '.ts')

    once_iterator_functions = [
        generate_once,
    ]

    tag_iterator_functions = [
        generate_per_tag,
    ]

    schema_iterator_functions = [
        generate_per_schema,
    ]

    @staticmethod
    def stage_default_iterators():
        utils.stage_iterator(Angular2.once_iterator, Angular2.once_iterator_functions)
        utils.stage_iterator(Angular2.tag_iterator, Angular2.tag_iterator_functions)
        utils.stage_iterator(Angular2.schema_iterator, Angular2.schema_iterator_functions)
