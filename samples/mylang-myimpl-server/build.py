from pixis.config import Config
from pixis.config import Implementation, Language, stage_iterator, once_iterator, tag_iterator, schema_iterator, emit_template, TEMPLATE_CONTEXT

SPEC = 'swagger.yaml'
OUTPUT = 'my_server'
FLASK_SERVER_NAME = 'my_flask_server'


class Python(Language):
    TYPE_MAP = {
        'integer': 'int',
        'int32': 'int',
        'long': 'int',
        'int64': 'int',
        'float': 'float',
        'double': 'float',
        'string': 'str',
        'byte': 'str',
        'binary': 'str',
        'boolean': 'bool',
        'date': 'date',
        'date-time': 'datetime',
        'password': 'str',
        'object': 'object',
        'array': 'List',
        '<': '[',
        '>': ']',
    }

    @staticmethod
    def to_lang_type(string):
        try:
            return Python.TYPE_MAP[string]
        except KeyError as err:
            raise KeyError(err)

    @staticmethod
    def to_lang_style(string):
        return Language.to_snake_case(string)


class Flask(Implementation):
    LANGUAGE = Python

    @staticmethod
    def process():
        for tag, paths in TEMPLATE_CONTEXT['paths'].items():
            for path in paths:
                path.url = path.url.replace('}', '>').replace('{', '<')

    @staticmethod
    def generate_once():
        emit_template('requirements.j2', Config.OUTPUT, 'requirements.txt')
        emit_template('Dockerfile.j2', Config.OUTPUT, 'Dockerfile')
        emit_template('util.j2', Config.OUTPUT + '/' + Config.FLASK_SERVER_NAME, 'util.py')
        emit_template('encoder.j2', Config.OUTPUT + '/' + Config.FLASK_SERVER_NAME, 'encoder.py')
        emit_template('base_model.j2', Config.OUTPUT + '/' + Config.FLASK_SERVER_NAME + '/models', 'base_model.py')
        emit_template('init.j2', Config.OUTPUT + '/' + Config.FLASK_SERVER_NAME, '__init__.py')
        emit_template('init.j2', Config.OUTPUT + '/' + Config.FLASK_SERVER_NAME + '/models', '__init__.py')
        emit_template('init.j2', Config.OUTPUT + '/' + Config.FLASK_SERVER_NAME + '/controllers', '__init__.py')
        emit_template('main.j2', Config.OUTPUT + '/' + Config.FLASK_SERVER_NAME, '__main__.py')
        emit_template('setup.j2', Config.OUTPUT, 'setup.py')

    @staticmethod
    def generate_per_tag():
        emit_template('controller.j2', Config.OUTPUT + '/' + Config.FLASK_SERVER_NAME + '/controllers', TEMPLATE_CONTEXT['_current_tag'] + '_controller.py')

    @staticmethod
    def generate_per_schema():
        emit_template('model.j2', Config.OUTPUT + '/' + Config.FLASK_SERVER_NAME + '/models', Implementation.lower_first(TEMPLATE_CONTEXT['_current_schema']) + '.py')

    @staticmethod
    def stage_default_iterators():
        stage_iterator(once_iterator, [Flask.generate_once])
        stage_iterator(tag_iterator, [Flask.generate_per_tag])
        stage_iterator(schema_iterator, [Flask.generate_per_schema])


IMPLEMENTATION = Flask
