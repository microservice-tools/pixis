class Language():
    """
    Language - base abstract class; provides default methods for specific language classes to override
    """
    @staticmethod
    def to_lang_type(string):
        raise NotImplementedError()

    @staticmethod
    def to_lang_style(string):
        raise NotImplementedError()

    @staticmethod
    def to_camel_case(string):
        s = string[0].lower()
        capitalize = False
        for char in string[1:-1]:
            if char == '_':
                capitalize = True
            else:
                if capitalize:
                    s += char.upper()
                else:
                    s += char
                capitalize = False
        return s + string[-1]

    @staticmethod
    def to_snake_case(string):
        s = string[0].lower()
        for char in string[1:-1]:
            if char.isupper():
                s += '_' + char.lower()
            else:
                s += char
        return s + string[-1].lower()
