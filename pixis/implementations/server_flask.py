import os

import pixis.utils as utils
from pixis.config import Config
from pixis.implementations.implementation import Implementation
from pixis.languages.python import Python
from pixis.template_context import TEMPLATE_CONTEXT


class Flask(Implementation):
    LANGUAGE = Python

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
    def process():
        for tag, paths in TEMPLATE_CONTEXT['paths'].items():
            for path in paths:
                path.url = path.url.replace('}', '>').replace('{', '<')

    @staticmethod
    def generate_once():
        utils.emit_template('flask_server/requirements.j2', Config.PATH_OUT, 'requirements.txt')
        utils.emit_template('flask_server/Dockerfile.j2', Config.PATH_OUT, 'Dockerfile')
        utils.emit_template('flask_server/util.j2', Config.FLASK_SERVER_OUTPUT, 'util.py')
        utils.emit_template('flask_server/encoder.j2', Config.FLASK_SERVER_OUTPUT, 'encoder.py')
        utils.emit_template('flask_server/base_model.j2', Config.FLASK_SERVER_OUTPUT + os.path.sep + 'models', 'base_model.py')
        utils.emit_template('flask_server/init.j2', Config.FLASK_SERVER_OUTPUT, '__init__.py')
        utils.emit_template('flask_server/main.j2', Config.FLASK_SERVER_OUTPUT, '__main__.py')
        # utils.emit_template('flask_server/setup.j2', Config.PATH_OUT, 'setup.py')

    @staticmethod
    def generate_per_tag():
        utils.emit_template('flask_server/controller.j2', Config.FLASK_SERVER_OUTPUT + os.path.sep + 'controllers', TEMPLATE_CONTEXT['_current_tag'] + '_controller' + '.py')

    @staticmethod
    def generate_per_schema():
        utils.emit_template('flask_server/model.j2', Config.FLASK_SERVER_OUTPUT + os.path.sep + 'models', Implementation.lower_first(TEMPLATE_CONTEXT['_current_schema']) + '.py')

    @staticmethod
    def stage_default_iterators():
        utils.stage_iterator(Flask.once_iterator, Flask.once_iterator_functions)
        utils.stage_iterator(Flask.tag_iterator, Flask.tag_iterator_functions)
        utils.stage_iterator(Flask.schema_iterator, Flask. schema_iterator_functions)
