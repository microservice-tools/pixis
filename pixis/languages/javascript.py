from pixis.languages.language import Language


class Javascript(Language):
    TYPE_MAP = {
        'integer': 'number',
        'int32': 'number',
        'long': 'number',
        'int64': 'number',
        'float': 'number',
        'double': 'number',
        'string': 'string',
        'byte': 'string',
        'binary': 'string',
        'boolean': 'boolean',
        'date': 'string',
        'date-time': 'Date',
        'password': 'string',
        'object': 'any',  # TODO
        'array': 'Array',
        '<': '<',
        '>': '>',
    }

    @staticmethod
    def to_lang_type(x):
        try:
            return Javascript.TYPE_MAP[x]
        except KeyError as e:
            raise KeyError(e)

    @staticmethod
    def to_lang_style(x):
        return x
