from .rep import Rep


class ServerVariable(Rep):
    def __init__(self, dikt):
        from .parse import parse_dict

        allowed = ['enum', 'default', 'description', 'extensions']
        required = ['default']
        arrays = ['enum']

        d = parse_dict(dikt=dikt, allowed=allowed)

        self.enum = d['enum']
        self.default = d['default']
        self.description = d['description']
        self.extensions = d['extensions']