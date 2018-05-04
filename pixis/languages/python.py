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
    def to_lang_type(x):
        try:
            return Python.TYPE_MAP[x]
        except KeyError as e:
            raise KeyError(e)

    @staticmethod
    def to_lang_style(x):
        return x
