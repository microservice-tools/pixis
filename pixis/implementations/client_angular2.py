import pixis.config as cfg
import pixis.template_handler as tmpl
from pixis.languages.javascript import Javascript


class Angular2(cfg.Implementation):
    LANGUAGE = Javascript

    @staticmethod
    def generate_once():
        cfg.emit_template('client_angular2/index.j2', cfg.Config.OUTPUT, 'index.ts')
        cfg.emit_template('client_angular2/variables.j2', cfg.Config.OUTPUT, 'variables.ts')
        cfg.emit_template('client_angular2/configuration.j2', cfg.Config.OUTPUT, 'configuration.ts')
        cfg.emit_template('client_angular2/api_ts.j2', cfg.Config.OUTPUT + '/api', 'api.ts')
        cfg.emit_template('client_angular2/models.j2', cfg.Config.OUTPUT + '/model', 'models.ts')
        cfg.emit_template('client_angular2/encoder.j2', cfg.Config.OUTPUT, 'encoder.ts')
        cfg.emit_template('client_angular2/api_module.j2', cfg.Config.OUTPUT, 'api.module.ts')
        cfg.emit_template('client_angular2/rxjs.j2', cfg.Config.OUTPUT, 'rxjs-operators.ts')
        cfg.emit_template('client_angular2/Dockerfile.j2', cfg.Config.PARENT, 'Dockerfile')

    @staticmethod
    def generate_per_tag():
        cfg.emit_template('client_angular2/service.j2', cfg.Config.OUTPUT + '/api', tmpl.TEMPLATE_CONTEXT['_current_tag'] + '.service.ts')

    @staticmethod
    def generate_per_schema():
        cfg.emit_template('client_angular2/model.j2', cfg.Config.OUTPUT + '/model', tmpl.TEMPLATE_CONTEXT['_current_schema'] + '.ts')

    @staticmethod
    def stage_default_iterators():
        cfg.stage_iterator(cfg.once_iterator, [Angular2.generate_once])
        cfg.stage_iterator(cfg.tag_iterator, [Angular2.generate_per_tag])
        cfg.stage_iterator(cfg.schema_iterator, [Angular2.generate_per_schema])
