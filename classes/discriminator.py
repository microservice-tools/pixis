import parse


class Discriminator:
    def __init__(self, dikt):
        allowed = ['propertyName', 'mapping']
        required = ['propertyName']
        mappings = ['mapping']

        d = parse_dict(dikt=dikt, allowed=allowed, required=required,
                       mappings=mappings)

        self.propertyName = d['propertyName']
        self.mapping = d['mapping']
