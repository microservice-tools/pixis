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
        tmpl.emit_template('server_flask/requirements.j2', cfg.Config.OUTPUT, 'requirements.txt')
        tmpl.emit_template('server_flask/Dockerfile.j2', cfg.Config.OUTPUT, 'Dockerfile')
        tmpl.emit_template('server_flask/util.j2', cfg.Config.OUTPUT + '/' + cfg.Config.FLASK_SERVER_NAME, 'util.py')
        tmpl.emit_template('server_flask/encoder.j2', cfg.Config.OUTPUT + '/' + cfg.Config.FLASK_SERVER_NAME, 'encoder.py')
        tmpl.emit_template('server_flask/base_model.j2', cfg.Config.OUTPUT + '/' + cfg.Config.FLASK_SERVER_NAME + '/models', 'base_model.py')
        tmpl.emit_template('server_flask/init.j2', cfg.Config.OUTPUT + '/' + cfg.Config.FLASK_SERVER_NAME, '__init__.py')
        tmpl.emit_template('server_flask/init.j2', cfg.Config.OUTPUT + '/' + cfg.Config.FLASK_SERVER_NAME + '/models', '__init__.py')
        tmpl.emit_template('server_flask/init.j2', cfg.Config.OUTPUT + '/' + cfg.Config.FLASK_SERVER_NAME + '/controllers', '__init__.py')
        tmpl.emit_template('server_flask/main.j2', cfg.Config.OUTPUT + '/' + cfg.Config.FLASK_SERVER_NAME, '__main__.py')
        tmpl.emit_template('server_flask/setup.j2', cfg.Config.OUTPUT, 'setup.py')

    @staticmethod
    def generate_per_tag():
        tmpl.emit_template('server_flask/controller.j2', cfg.Config.OUTPUT + '/' + cfg.Config.FLASK_SERVER_NAME + '/controllers', tmpl.TEMPLATE_CONTEXT['_current_tag'] + '_controller.py')

    @staticmethod
    def generate_per_schema():
        tmpl.emit_template('server_flask/model.j2', cfg.Config.OUTPUT + '/' + cfg.Config.FLASK_SERVER_NAME + '/models', cfg.Implementation.lower_first(tmpl.TEMPLATE_CONTEXT['_current_schema']) + '.py')

    @staticmethod
    def stage_default_iterators():
        import pixis.utils as utils
        utils.stage_iterator(utils.once_iterator, [Flask.generate_once])
        utils.stage_iterator(utils.tag_iterator, [Flask.generate_per_tag])
        utils.stage_iterator(utils.schema_iterator, [Flask.generate_per_schema])
