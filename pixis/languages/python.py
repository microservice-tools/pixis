from pixis.languages.language import Language


class Python(Language):
    TYPE_MAP = {
        'integer': 'int',
        'int32': 'int',
        'long': 'int',
        'int64': 'int',
        'float': 'float',
        'double': 'float',
        'string': 'str',
        # 'byte': 'ByteArray',
        'byte': 'str',
        'binary': 'str',
        # 'binary': 'Binary',
        'boolean': 'bool',
        'date': 'date',
        'date-time': 'datetime',
        'password': 'str',
        'object': 'object',  # TODO
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
