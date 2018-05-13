import os

import pixis.config as cfg
import pixis.template_handler as tmpl
from pixis.implementations.implementation import Implementation
from pixis.languages.javascript import Javascript


class Angular2(Implementation):
    LANGUAGE = Javascript

    @staticmethod
    def generate_once():
        tmpl.emit_template('client_angular2/index.j2', cfg.Config.PATH_OUT, 'index.ts')
        tmpl.emit_template('client_angular2/variables.j2', cfg.Config.PATH_OUT, 'variables.ts')
        tmpl.emit_template('client_angular2/configuration.j2', cfg.Config.PATH_OUT, 'configuration.ts')
        tmpl.emit_template('client_angular2/api_ts.j2', Path(cfg.Config.PATH_OUT) / 'api', 'api.ts')
        tmpl.emit_template('client_angular2/models.j2', Path(cfg.Config.PATH_OUT) / 'model', 'models.ts')
        tmpl.emit_template('client_angular2/encoder.j2', Path(cfg.Config.PATH_OUT), 'encoder.ts')
        tmpl.emit_template('client_angular2/api_module.j2', Path(cfg.Config.PATH_OUT), 'api.module.ts')
        tmpl.emit_template('client_angular2/rxjs.j2', Path(cfg.Config.PATH_OUT), 'rxjs-operators.ts')

    @staticmethod
    def generate_per_tag():
        tmpl.emit_template('client_angular2/service.j2', Path(cfg.Config.PATH_OUT) / 'api', tmpl.TEMPLATE_CONTEXT['_current_tag'] + '.service.ts')

    @staticmethod
    def generate_per_schema():
        tmpl.emit_template('client_angular2/model.j2', Path(cfg.Config.PATH_OUT) / 'model', tmpl.TEMPLATE_CONTEXT['_current_schema'] + '.ts')

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
