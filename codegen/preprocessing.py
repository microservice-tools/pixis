try:  # when just doing $ python3 main.py only below imports work
    import codegen.codegen_config as cfg
except ImportError as err:  # when packaged, only above imports work
    import codegen_config as cfg

#write print functions!!!

class Model:
    def __init__(self, name, schema_obj):
        self.name = name
        # key is filename, value is class that is being imported. **NOT SURE IF THIS WILL BE KEPT**
        self.dependencies = getDeps(schema_obj)
        self.properties = getProperties(schema_obj) # dictionary with key is property name, value is property type

    def __repr__(self):
        return self.to_str()

    def to_str(self):
        return str(self.__dict__)

def getDeps(schema_obj):
    
    deps = []

    for attribute_name, attribute_dikt in schema_obj['properties'].items():
        attr_deps = getDepByAttr(attribute_dikt)
        deps = deps + attr_deps

    print(deps)
    return deps

def getDepByAttr(attribute_dikt):
    depsByAttr = []

    ref = attribute_dikt.get('$ref')
    if ref is not None:
        ref = ref[ref.rfind('/') + 1:]
        depsByAttr.append(ref)

    elif attribute_dikt['type'] == 'array':
        depsByAttr = depsByAttr + getDepByAttr(attribute_dikt['items'])

    return depsByAttr


class Property:
    def __init__(self, name, property_obj, requiredList):
        self.name = name
        self.type = getType(property_obj, 0)
        self.isRequired = isRequired(name, requiredList)
        # returns None if no enums associated with property, otherwise return a list 
        self.enums = getEnums(property_obj)

    def __repr__(self):
        return self.to_str()

    def to_str(self):
        return str(self.__dict__)

class Enum:
    def __init__(self, attributes):
        self.attributes = attributes

    def __repr__(self):
        return self.to_str()

    def to_str(self):
        return str(self.__dict__)

def models():

    #initialize array to hold model and scheamas for use below
    models = {}
    schemas = cfg.SPEC_DICT['components']['schemas']

    #iterate through each schema
    for schema_name, schema in schemas.items():
        model = Model(schema_name, schema)
        # print(model)
        models[model.name] = model

    cfg.TEMPLATE_VARIABLES['schemas'] = models

def getType(schema_obj, depth):

    if '$ref' in schema_obj:
        s = schema_obj['$ref'].split('/')[3]
        for x in range(depth):
            s += '>'
        return s

    if schema_obj['type'] == 'array':
        return 'Array<' + getType(schema_obj['items'], depth + 1)

    # s = typeMapping[schema_obj.type]
    type_format = getattr(schema_obj, 'format', None)
    if type_format is not None:
        s = type_format
    else:
        s = schema_obj['type']

    for x in range(depth):
        s += '>'
    return s


def getEnums(attributes):

    enumList = attributes.get('enum')

    return enumList


def isRequired(attribute_name, requiredList):
    if requiredList is None:
        return False
    elif attribute_name in requiredList:
        return True
    else:
        return False


def getProperties(schema_obj):
    properties = []
    for attribute_name, attribute_dikt in schema_obj['properties'].items():
        property = Property(attribute_name, attribute_dikt, schema_obj.get('required'))
        properties.append(property)

    return properties