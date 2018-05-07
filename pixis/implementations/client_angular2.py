import os

import pixis.config as cfg
import pixis.template_handler as tmpl
from pixis.implementations.implementation import Implementation
from pixis.languages.javascript import Javascript


class Angular2(Implementation):
    LANGUAGE = Javascript

    @staticmethod
    def generate_once():
        tmpl.emit_template('typescript_client/index.j2', cfg.Config.PATH_OUT, 'index.ts')
        tmpl.emit_template('typescript_client/variables.j2', cfg.Config.PATH_OUT, 'variables.ts')
        tmpl.emit_template('typescript_client/configuration.j2', cfg.Config.PATH_OUT, 'configuration.ts')
        tmpl.emit_template('typescript_client/api_ts.j2', cfg.Config.PATH_OUT + os.path.sep + 'api', 'api.ts')
        tmpl.emit_template('typescript_client/models.j2', cfg.Config.PATH_OUT + os.path.sep + 'model', 'models.ts')
        tmpl.emit_template('typescript_client/encoder.j2', cfg.Config.PATH_OUT, 'encoder.ts')
        tmpl.emit_template('typescript_client/api_module.j2', cfg.Config.PATH_OUT, 'api.module.ts')
        tmpl.emit_template('typescript_client/rxjs.j2', cfg.Config.PATH_OUT, 'rxjs-operators.ts')

    @staticmethod
    def generate_per_tag():
        tmpl.emit_template('typescript_client/service.j2', cfg.Config.PATH_OUT + os.path.sep + 'api', tmpl.TEMPLATE_CONTEXT['_current_tag'] + '.service.ts')

    @staticmethod
    def generate_per_schema():
        tmpl.emit_template('typescript_client/model.j2', cfg.Config.PATH_OUT + os.path.sep + 'model', tmpl.TEMPLATE_CONTEXT['_current_schema'] + '.ts')

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
        import pixis.utils as utils
        utils.stage_iterator(utils.once_iterator, Angular2.once_iterator_functions)
        utils.stage_iterator(utils.tag_iterator, Angular2.tag_iterator_functions)
        utils.stage_iterator(utils.schema_iterator, Angular2.schema_iterator_functions)
