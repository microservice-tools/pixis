import pixis.config as cfg
import pixis.template_handler as tmpl
from pixis.implementations.implementation import Implementation
from pixis.languages.javascript import Javascript


class Angular2(Implementation):
    LANGUAGE = Javascript

    @staticmethod
    def generate_once():
        tmpl.emit_template('client_angular2/index.j2', cfg.Config.OUT, 'index.ts')
        tmpl.emit_template('client_angular2/variables.j2', cfg.Config.OUT, 'variables.ts')
        tmpl.emit_template('client_angular2/configuration.j2', cfg.Config.OUT, 'configuration.ts')
        tmpl.emit_template('client_angular2/api_ts.j2', cfg.Config.OUT + '/api', 'api.ts')
        tmpl.emit_template('client_angular2/models.j2', cfg.Config.OUT + '/model', 'models.ts')
        tmpl.emit_template('client_angular2/encoder.j2', cfg.Config.OUT, 'encoder.ts')
        tmpl.emit_template('client_angular2/api_module.j2', cfg.Config.OUT, 'api.module.ts')
        tmpl.emit_template('client_angular2/rxjs.j2', cfg.Config.OUT, 'rxjs-operators.ts')

    @staticmethod
    def generate_per_tag():
        tmpl.emit_template('client_angular2/service.j2', cfg.Config.OUT + '/api', tmpl.TEMPLATE_CONTEXT['_current_tag'] + '.service.ts')

    @staticmethod
    def generate_per_schema():
        tmpl.emit_template('client_angular2/model.j2', cfg.Config.OUT + '/model', tmpl.TEMPLATE_CONTEXT['_current_schema'] + '.ts')

    @staticmethod
    def stage_default_iterators():
        import pixis.utils as utils
        utils.stage_iterator(utils.once_iterator, [Angular2.generate_once])
        utils.stage_iterator(utils.tag_iterator, [Angular2.generate_per_tag])
        utils.stage_iterator(utils.schema_iterator, [Angular2.generate_per_schema])
