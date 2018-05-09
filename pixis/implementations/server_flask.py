import os

import pixis.config as cfg
import pixis.template_handler as tmpl
from pixis.implementations.implementation import Implementation
from pixis.languages.python import Python


class Flask(Implementation):
    LANGUAGE = Python

    @staticmethod
    def process():
        for tag, paths in tmpl.TEMPLATE_CONTEXT['paths'].items():
            for path in paths:
                path.url = path.url.replace('}', '>').replace('{', '<')

    @staticmethod
    def generate_once():
        tmpl.emit_template('server_flask/requirements.j2', cfg.Config.PATH_OUT, 'requirements.txt')
        tmpl.emit_template('server_flask/Dockerfile.j2', cfg.Config.PATH_OUT, 'Dockerfile')
        tmpl.emit_template('server_flask/util.j2', cfg.Config.FLASK_SERVER_OUTPUT, 'util.py')
        tmpl.emit_template('server_flask/encoder.j2', cfg.Config.FLASK_SERVER_OUTPUT, 'encoder.py')
        tmpl.emit_template('server_flask/base_model.j2', cfg.Config.FLASK_SERVER_OUTPUT + os.path.sep + 'models', 'base_model.py')
        tmpl.emit_template('server_flask/init.j2', cfg.Config.FLASK_SERVER_OUTPUT, '__init__.py')
        tmpl.emit_template('server_flask/init.j2', cfg.Config.FLASK_SERVER_OUTPUT + os.path.sep + 'models', '__init__.py')
        tmpl.emit_template('server_flask/init.j2', cfg.Config.FLASK_SERVER_OUTPUT + os.path.sep + 'controllers', '__init__.py')
        tmpl.emit_template('server_flask/main.j2', cfg.Config.FLASK_SERVER_OUTPUT, '__main__.py')
        tmpl.emit_template('server_flask/setup.j2', cfg.Config.PATH_OUT, 'setup.py')

    @staticmethod
    def generate_per_tag():
        tmpl.emit_template('server_flask/controller.j2', cfg.Config.FLASK_SERVER_OUTPUT + os.path.sep + 'controllers', tmpl.TEMPLATE_CONTEXT['_current_tag'] + '_controller' + '.py')

    @staticmethod
    def generate_per_schema():
        tmpl.emit_template('server_flask/model.j2', cfg.Config.FLASK_SERVER_OUTPUT + os.path.sep + 'models', Implementation.lower_first(tmpl.TEMPLATE_CONTEXT['_current_schema']) + '.py')

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
        utils.stage_iterator(utils.once_iterator, Flask.once_iterator_functions)
        utils.stage_iterator(utils.tag_iterator, Flask.tag_iterator_functions)
        utils.stage_iterator(utils.schema_iterator, Flask.schema_iterator_functions)
