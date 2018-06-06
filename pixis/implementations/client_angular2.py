import pixis.config as cfg
import pixis.template_handler as tmpl
from pixis.languages.javascript import Javascript


class Angular2(cfg.Implementation):
    LANGUAGE = Javascript

    @staticmethod
    def generate_once():
        tmpl.emit_template('client_angular2/index.j2', cfg.Config.OUTPUT, 'index.ts')
        tmpl.emit_template('client_angular2/variables.j2', cfg.Config.OUTPUT, 'variables.ts')
        tmpl.emit_template('client_angular2/configuration.j2', cfg.Config.OUTPUT, 'configuration.ts')
        tmpl.emit_template('client_angular2/api_ts.j2', cfg.Config.OUTPUT + '/api', 'api.ts')
        tmpl.emit_template('client_angular2/models.j2', cfg.Config.OUTPUT + '/model', 'models.ts')
        tmpl.emit_template('client_angular2/encoder.j2', cfg.Config.OUTPUT, 'encoder.ts')
        tmpl.emit_template('client_angular2/api_module.j2', cfg.Config.OUTPUT, 'api.module.ts')
        tmpl.emit_template('client_angular2/rxjs.j2', cfg.Config.OUTPUT, 'rxjs-operators.ts')
        tmpl.emit_template('client_angular2/Dockerfile.j2', cfg.Config.PARENT, 'Dockerfile')

    @staticmethod
    def generate_per_tag():
        tmpl.emit_template('client_angular2/service.j2', cfg.Config.OUTPUT + '/api', tmpl.TEMPLATE_CONTEXT['_current_tag'] + '.service.ts')

    @staticmethod
    def generate_per_schema():
        tmpl.emit_template('client_angular2/model.j2', cfg.Config.OUTPUT + '/model', tmpl.TEMPLATE_CONTEXT['_current_schema'] + '.ts')

    @staticmethod
    def stage_default_iterators():
        import pixis.utils as utils
        utils.stage_iterator(utils.once_iterator, [Angular2.generate_once])
        utils.stage_iterator(utils.tag_iterator, [Angular2.generate_per_tag])
        utils.stage_iterator(utils.schema_iterator, [Angular2.generate_per_schema])
