import pixis.config as cfg
import pixis.template_handler as tmpl
from pixis.languages.python import Python


class Flask(cfg.Implementation):
    LANGUAGE = Python

    @staticmethod
    def process():
        for tag, paths in tmpl.TEMPLATE_CONTEXT['paths'].items():
            for path in paths:
                path.url = path.url.replace('}', '>').replace('{', '<')

    @staticmethod
    def generate_once():
        cfg.emit_template('server_flask/requirements.j2', cfg.Config.OUTPUT, 'requirements.txt')
        cfg.emit_template('server_flask/Dockerfile.j2', cfg.Config.OUTPUT, 'Dockerfile')
        cfg.emit_template('server_flask/util.j2', cfg.Config.OUTPUT + '/' + cfg.Config.FLASK_SERVER_NAME, 'util.py')
        cfg.emit_template('server_flask/encoder.j2', cfg.Config.OUTPUT + '/' + cfg.Config.FLASK_SERVER_NAME, 'encoder.py')
        cfg.emit_template('server_flask/base_model.j2', cfg.Config.OUTPUT + '/' + cfg.Config.FLASK_SERVER_NAME + '/models', 'base_model.py')
        cfg.emit_template('server_flask/init.j2', cfg.Config.OUTPUT + '/' + cfg.Config.FLASK_SERVER_NAME, '__init__.py')
        cfg.emit_template('server_flask/init.j2', cfg.Config.OUTPUT + '/' + cfg.Config.FLASK_SERVER_NAME + '/models', '__init__.py')
        cfg.emit_template('server_flask/init.j2', cfg.Config.OUTPUT + '/' + cfg.Config.FLASK_SERVER_NAME + '/controllers', '__init__.py')
        cfg.emit_template('server_flask/main.j2', cfg.Config.OUTPUT + '/' + cfg.Config.FLASK_SERVER_NAME, '__main__.py')
        cfg.emit_template('server_flask/setup.j2', cfg.Config.OUTPUT, 'setup.py')

    @staticmethod
    def generate_per_tag():
        cfg.emit_template('server_flask/controller.j2', cfg.Config.OUTPUT + '/' + cfg.Config.FLASK_SERVER_NAME + '/controllers', tmpl.TEMPLATE_CONTEXT['_current_tag'] + '_controller.py')

    @staticmethod
    def generate_per_schema():
        cfg.emit_template('server_flask/model.j2', cfg.Config.OUTPUT + '/' + cfg.Config.FLASK_SERVER_NAME + '/models', cfg.Implementation.lower_first(tmpl.TEMPLATE_CONTEXT['_current_schema']) + '.py')

    @staticmethod
    def stage_default_iterators():
        cfg.stage_iterator(cfg.once_iterator, [Flask.generate_once])
        cfg.stage_iterator(cfg.tag_iterator, [Flask.generate_per_tag])
        cfg.stage_iterator(cfg.schema_iterator, [Flask.generate_per_schema])
