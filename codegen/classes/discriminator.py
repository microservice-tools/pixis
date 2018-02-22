from .rep import Rep


class Discriminator(Rep):
    def __init__(self, dikt):
        from .parse import parse_dict

        allowed = ['propertyName', 'mapping']
        required = ['propertyName']
        mappings = ['mapping']

        d = parse_dict(dikt=dikt, allowed=allowed, required=required,
                       mappings=mappings)

        self.propertyName = d['propertyName']
        self.mapping = d['mapping']
