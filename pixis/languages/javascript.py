import pixis.config as cfg


class Javascript(cfg.Language):
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
    def to_lang_type(string):
        try:
            return Javascript.TYPE_MAP[string]
        except KeyError as err:
            raise KeyError(err)

    @staticmethod
    def to_lang_style(string):
        return cfg.Language.to_camel_case(string)
